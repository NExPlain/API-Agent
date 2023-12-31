
'\n@generated by mypy-protobuf.  Do not edit manually!\nisort:skip_file\n'
import builtins
import collections.abc
import google.protobuf.descriptor
import google.protobuf.internal.containers
import google.protobuf.message
from . import intent_input_pb2
from . import intent_output_pb2
from . import meta_data_pb2
import sys
if (sys.version_info >= (3, 8)):
    import typing as typing_extensions
else:
    import typing_extensions
DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

@typing_extensions.final
class IntentTemplate(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    TYPE_FIELD_NUMBER: builtins.int
    NAME_FIELD_NUMBER: builtins.int
    META_DATA_FIELD_NUMBER: builtins.int
    INPUTS_FIELD_NUMBER: builtins.int
    OUTPUTS_FIELD_NUMBER: builtins.int
    CREATE_TIMESTAMP_FIELD_NUMBER: builtins.int
    OAUTH_ENDPOINT_FIELD_NUMBER: builtins.int
    EXECUTE_ENDPOINT_FIELD_NUMBER: builtins.int
    APP_NAME_FIELD_NUMBER: builtins.int
    type: builtins.str
    name: builtins.str

    @property
    def meta_data(self) -> meta_data_pb2.MetaData:
        ...

    @property
    def inputs(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[intent_input_pb2.IntentInput]:
        ...

    @property
    def outputs(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[intent_output_pb2.IntentOutput]:
        ...
    create_timestamp: builtins.str
    oauth_endpoint: builtins.str
    execute_endpoint: builtins.str
    app_name: builtins.str

    def __init__(self, *, type: builtins.str=..., name: builtins.str=..., meta_data: (meta_data_pb2.MetaData | None)=..., inputs: (collections.abc.Iterable[intent_input_pb2.IntentInput] | None)=..., outputs: (collections.abc.Iterable[intent_output_pb2.IntentOutput] | None)=..., create_timestamp: builtins.str=..., oauth_endpoint: builtins.str=..., execute_endpoint: builtins.str=..., app_name: builtins.str=...) -> None:
        ...

    def HasField(self, field_name: typing_extensions.Literal[('meta_data', b'meta_data')]) -> builtins.bool:
        ...

    def ClearField(self, field_name: typing_extensions.Literal[('app_name', b'app_name', 'create_timestamp', b'create_timestamp', 'execute_endpoint', b'execute_endpoint', 'inputs', b'inputs', 'meta_data', b'meta_data', 'name', b'name', 'oauth_endpoint', b'oauth_endpoint', 'outputs', b'outputs', 'type', b'type')]) -> None:
        ...
global___IntentTemplate = IntentTemplate
