
'\n@generated by mypy-protobuf.  Do not edit manually!\nisort:skip_file\n'
import builtins
import google.protobuf.descriptor
import google.protobuf.message
import sys
if (sys.version_info >= (3, 8)):
    import typing as typing_extensions
else:
    import typing_extensions
DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

@typing_extensions.final
class MetaData(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    EMOJI_FIELD_NUMBER: builtins.int
    LOGO_URL_FIELD_NUMBER: builtins.int
    THUMBNAIL_FIELD_NUMBER: builtins.int
    emoji: builtins.str
    logo_url: builtins.str
    thumbnail: builtins.str

    def __init__(self, *, emoji: builtins.str=..., logo_url: builtins.str=..., thumbnail: builtins.str=...) -> None:
        ...

    def ClearField(self, field_name: typing_extensions.Literal[('emoji', b'emoji', 'logo_url', b'logo_url', 'thumbnail', b'thumbnail')]) -> None:
        ...
global___MetaData = MetaData
