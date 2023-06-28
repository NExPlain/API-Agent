
'Generated protocol buffer code.'
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from . import intent_input_pb2 as intent__input__pb2
from . import intent_output_pb2 as intent__output__pb2
from . import meta_data_pb2 as meta__data__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15intent_template.proto\x12\x08workflow\x1a\x12intent_input.proto\x1a\x13intent_output.proto\x1a\x0fmeta_data.proto"\x81\x02\n\x0eIntentTemplate\x12\x0c\n\x04type\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12%\n\tmeta_data\x18\x03 \x01(\x0b2\x12.workflow.MetaData\x12%\n\x06inputs\x18\x04 \x03(\x0b2\x15.workflow.IntentInput\x12\'\n\x07outputs\x18\x05 \x03(\x0b2\x16.workflow.IntentOutput\x12\x18\n\x10create_timestamp\x18\x06 \x01(\t\x12\x16\n\x0eoauth_endpoint\x18\x07 \x01(\t\x12\x18\n\x10execute_endpoint\x18\x08 \x01(\t\x12\x10\n\x08app_name\x18\t \x01(\tb\x06proto3')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'intent_template_pb2', globals())
if (_descriptor._USE_C_DESCRIPTORS == False):
    DESCRIPTOR._options = None
    _INTENTTEMPLATE._serialized_start = 94
    _INTENTTEMPLATE._serialized_end = 351
