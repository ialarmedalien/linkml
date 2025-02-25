# Auto generated from extensions.yaml by pythongen.py version: 0.9.0
# Generation date: 2022-03-08T16:58:00
# Schema: extensions
#
# id: https://w3id.org/linkml/extensions
# description: Extension mixin
# license: https://creativecommons.org/publicdomain/zero/1.0/

import dataclasses
import re
import sys
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional, Union

from jsonasobj2 import JsonObj, as_dict
from linkml_runtime.utils.curienamespace import CurieNamespace
from linkml_runtime.utils.dataclass_extensions_376 import \
    dataclasses_init_fn_with_kwargs
from linkml_runtime.utils.enumerations import EnumDefinitionImpl
from linkml_runtime.utils.formatutils import camelcase, sfx, underscore
from linkml_runtime.utils.metamodelcore import (URIorCURIE, bnode, empty_dict,
                                                empty_list)
from linkml_runtime.utils.slot import Slot
from linkml_runtime.utils.yamlutils import (YAMLRoot, extended_float,
                                            extended_int, extended_str)
from rdflib import Namespace, URIRef

from .types import String, Uriorcurie

metamodel_version = "1.7.0"
version = "2.0.0"

# Overwrite dataclasses _init_fn to add **kwargs in __init__
dataclasses._init_fn = dataclasses_init_fn_with_kwargs

# Namespaces
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
DEFAULT_ = LINKML


# Types

# Class references
class ExtensionTag(URIorCURIE):
    pass


@dataclass
class Extension(YAMLRoot):
    """
    a tag/value pair used to add non-model information to an entry
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = LINKML.Extension
    class_class_curie: ClassVar[str] = "linkml:Extension"
    class_name: ClassVar[str] = "extension"
    class_model_uri: ClassVar[URIRef] = LINKML.Extension

    tag: Union[str, ExtensionTag] = None
    value: str = None
    extensions: Optional[Union[Dict[Union[str, ExtensionTag], Union[dict, "Extension"]], List[Union[dict, "Extension"]]]] = empty_dict()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.tag):
            self.MissingRequiredField("tag")
        if not isinstance(self.tag, ExtensionTag):
            self.tag = ExtensionTag(self.tag)

        if self._is_empty(self.value):
            self.MissingRequiredField("value")
        if not isinstance(self.value, str):
            self.value = str(self.value)

        self._normalize_inlined_as_dict(slot_name="extensions", slot_type=Extension, key_name="tag", keyed=True)

        super().__post_init__(**kwargs)


@dataclass
class Extensible(YAMLRoot):
    """
    mixin for classes that support extension
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = LINKML.Extensible
    class_class_curie: ClassVar[str] = "linkml:Extensible"
    class_name: ClassVar[str] = "extensible"
    class_model_uri: ClassVar[URIRef] = LINKML.Extensible

    extensions: Optional[Union[Dict[Union[str, ExtensionTag], Union[dict, Extension]], List[Union[dict, Extension]]]] = empty_dict()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        self._normalize_inlined_as_dict(slot_name="extensions", slot_type=Extension, key_name="tag", keyed=True)

        super().__post_init__(**kwargs)


# Enumerations


# Slots
class slots:
    pass

slots.extensions = Slot(uri=LINKML.extensions, name="extensions", curie=LINKML.curie('extensions'),
                   model_uri=LINKML.extensions, domain=None, range=Optional[Union[Dict[Union[str, ExtensionTag], Union[dict, Extension]], List[Union[dict, Extension]]]])

slots.extension_tag = Slot(uri=LINKML.tag, name="extension_tag", curie=LINKML.curie('tag'),
                   model_uri=LINKML.extension_tag, domain=Extension, range=Union[str, ExtensionTag])

slots.extension_value = Slot(uri=LINKML.value, name="extension_value", curie=LINKML.curie('value'),
                   model_uri=LINKML.extension_value, domain=Extension, range=str)