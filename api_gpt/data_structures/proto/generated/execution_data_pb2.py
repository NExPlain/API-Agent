
'Generated protocol buffer code.'
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from . import intent_output_pb2 as intent__output__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x14execution_data.proto\x12\x08workflow\x1a\x13intent_output.proto"\xa5\x01\n\x0fExecutionResult\x12\x12\n\nis_success\x18\x01 \x01(\x08\x12\x12\n\nerror_code\x18\x02 \x01(\x05\x12\x15\n\rerror_message\x18\x03 \x01(\t\x12\'\n\x07outputs\x18\x04 \x03(\x0b2\x16.workflow.IntentOutput\x12\x14\n\x0cdisplay_link\x18\x05 \x01(\t\x12\x14\n\x0cdisplay_name\x18\x06 \x01(\t"\x92\x01\n\rExecutionData\x12\x14\n\x0cis_executing\x18\x01 \x01(\x08\x12\x16\n\x0eexecution_time\x18\x02 \x01(\x05\x12\x13\n\x0bexecutor_id\x18\x03 \x01(\t\x12\x13\n\x0bis_finished\x18\x04 \x01(\x08\x12)\n\x06result\x18\x05 \x01(\x0b2\x19.workflow.ExecutionResultb\x06proto3')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'execution_data_pb2', globals())
if (_descriptor._USE_C_DESCRIPTORS == False):
    DESCRIPTOR._options = None
    _EXECUTIONRESULT._serialized_start = 56
    _EXECUTIONRESULT._serialized_end = 221
    _EXECUTIONDATA._serialized_start = 224
    _EXECUTIONDATA._serialized_end = 370
