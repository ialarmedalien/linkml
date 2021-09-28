import logging
import os
from copy import copy
from dataclasses import dataclass, field
from enum import unique
from typing import List, Dict, Union, TextIO

from sqlalchemy import *

from linkml_runtime.linkml_model import SchemaDefinition, ClassDefinition, SlotDefinition, Annotation, \
    ClassDefinitionName, Prefix
from linkml_runtime.utils.formatutils import underscore, camelcase
from linkml_runtime.utils.schemaview import SchemaView

from linkml.transformers.relmodel_transformer import RelationalModelTransformer
from linkml.utils.generator import Generator


class SqlNamingPolicy(Enum):
    preserve = 'preserve'
    underscore = 'underscore'
    camelcase = 'camelcase'

RANGEMAP = {
    'str': Text(),
    'NCName': Text(),
    'URIorCURIE': Text(),
    'int': Integer(),
    'double': Float(),
    'float': Float(),
    'Bool': Boolean(),
    'URI': Text(),
    'XSDTime': Time(),
    'XSDDateTime': DateTime(),
    'XSDDate': Date(),
}



class SQLTableGenerator(Generator):
    """
    A `Generator` for creating SQL DDL

    The basic algorithm for mapping a linkml schema S is as follows:

     - Each schema S corresponds to one database schema D (see SQLSchema)
     - Each Class C in S is mapped to a table T (see SQLTable)
     - Each slot S in each C is mapped to a column Col (see SQLColumn)

    if the direct_mapping attribute is set to true, then no further transformations
    are applied. Note that this means:

     - inline objects are modeled as Text strings
     - multivalued fields are modeled as single Text strings

    this direct mapping is useful for simple spreadsheet/denormalized representations of complex data.
    however, for other applications, additional transformations should occur. these are:

    MULTIVALUED SLOTS

    The relational model does not have direct representation of lists. These are normalized as follows.

    If the range of the slot is a class, and there are no other slots whose range is this class,
    and the slot is for a class that has a singular primary key, then a backref is added.

    E.g. if we have User 0..* Address,
    then add a field User_id to Address.

    When SQLAlchemy bindings are created, a backref mapping is added

    If the range of the slot is an enum or type, then a new linktable is created, and a backref added

    E.g. if a class User has a multivalues slot alias whose range is a string,
    then create a table user_aliases, with two columns (1) alias [a string] and (2) a backref to user

     Each mapped slot C.S has a range R

     ranges that are types (literals):
       - If R is a type, and the slot is NOT multivalued, do a direct type conversion
       - If R is a type, and the slot is multivalued:
         * do not include the mapped column
         * create a new table T_S, with 2 columns: S, and a backref to T
      ranges that are classes:
       Ref = map_class_to_table(R)
       - if R is a class, and the slot is NOT multivalued, and Ref has a singular primary key:
         * Col.type = ForeignKey(Ref.PK)
       - if R is a class, and the slot is NOT multivalued, and Ref has NO singular primary key:
         * add a foreign key C.pk to Ref
         * add a backref C.S => Ref, C.pk
         * remove Col from T
       - If R is a class, and the slot IS multivalued

    """
    generatorname = os.path.basename(__file__)
    generatorversion = "0.1.1"
    valid_formats = ['sql']
    use_inherits: bool = False  ## postgresql supports inheritance
    dialect: str
    inject_primary_keys: bool = True

    def __init__(self, schema: Union[str, TextIO, SchemaDefinition], dialect='sqlite',
                 use_foreign_keys = True,
                 rename_foreign_keys = False,
                 direct_mapping = False,
                 **kwargs) -> None:
        # do not do generator-based transform of schema
        #super().__init__(schema, **kwargs)
        self.schema = schema
        self.relative_slot_num = 0
        self.dialect = dialect
        self.use_foreign_keys = use_foreign_keys
        self.rename_foreign_keys = rename_foreign_keys
        self.direct_mapping = direct_mapping

    def generate_ddl(self, naming_policy: SqlNamingPolicy = None, **kwargs) -> str:
        ddl_str = ""
        def dump(sql, *multiparams, **params):
            nonlocal ddl_str
            ddl_str += f"{str(sql.compile(dialect=engine.dialect)).rstrip()};"

        engine = create_mock_engine(
            f'{self.dialect}://./MyDb',
            strategy='mock',
            executor= dump)
        schema_metadata = MetaData()
        sqltr = RelationalModelTransformer(SchemaView(self.schema))
        tr_result = sqltr.transform(**kwargs)
        schema = tr_result.schema

        def sql_name(n: str) -> str:
            if naming_policy is not None:
                if naming_policy == SqlNamingPolicy.underscore:
                    return underscore(n)
                elif naming_policy == SqlNamingPolicy.camelcase:
                    return camelcase(n)
                elif naming_policy == SqlNamingPolicy.preserve:
                    return n
                else:
                    raise Exception(f'Unknown: {naming_policy}')
            else:
                return n

        sv = SchemaView(schema)
        for cn, c in schema.classes.items():
            pk_slot = sv.get_identifier_slot(cn)
            if c.attributes:
                cols = []
                for sn, s in c.attributes.items():
                    is_pk = 'primary_key' in s.annotations
                    if pk_slot:
                        is_pk = sn == pk_slot.name
                    #else:
                    #    is_pk = True  ## TODO: use unique key
                    args = []
                    if s.range in schema.classes:
                        fk = sql_name(self.get_foreign_key(s.range, sv))
                        args = [ForeignKey(fk)]
                    field_type = self.get_sql_range(s, schema)
                    col = Column(sql_name(sn), field_type, *args, primary_key=is_pk, nullable=not s.required)
                    cols.append(col)
                Table(sql_name(cn), schema_metadata, *cols)
        schema_metadata.create_all(engine)
        return ddl_str

    # TODO: merge with code from sqlddlgen
    def get_sql_range(self, slot: SlotDefinition, schema: SchemaDefinition):
        """
        returns a SQL Alchemy column type
        """
        range = slot.range
        if range in schema.classes:
            return Text()
        if range in schema.types:
            range = schema.types[range].base

        if range in schema.enums:
            e = schema.enums[range]
            if e.permissible_values is not None:
                vs = [str(v) for v in e.permissible_values]
                return Enum(name=e.name, *vs)
        if range in RANGEMAP:
            return RANGEMAP[range]
        else:
            logging.warning(f'UNKNOWN: {range} // {type(range)}')
            return Text()

    def get_foreign_key(self, cn: str, sv: SchemaView) -> str:
        pk = sv.get_identifier_slot(cn)
        if pk is None:
            raise Exception(f'No PK for {cn}')
        return f'{cn}.{pk.name}'