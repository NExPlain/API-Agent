
'Generated protocol buffer code.'
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from . import intent_data_pb2 as intent__data__pb2
from . import meta_data_pb2 as meta__data__pb2
from . import workflow_example_pb2 as workflow__example__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x17workflow_template.proto\x12\x08workflow\x1a\x11intent_data.proto\x1a\x0fmeta_data.proto\x1a\x16workflow_example.proto"\xbe\x01\n\x10WorkflowTemplate\x12\x0c\n\x04type\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x13\n\x0bdescription\x18\x03 \x01(\t\x12%\n\tmeta_data\x18\x04 \x01(\x0b2\x12.workflow.MetaData\x12%\n\x07intents\x18\x05 \x03(\x0b2\x14.workflow.IntentData\x12+\n\x08examples\x18\x06 \x03(\x0b2\x19.workflow.WorkflowExampleb\x06proto3')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'workflow_template_pb2', globals())
if (_descriptor._USE_C_DESCRIPTORS == False):
    DESCRIPTOR._options = None
    _WORKFLOWTEMPLATE._serialized_start = 98
    _WORKFLOWTEMPLATE._serialized_end = 288
