from google.protobuf.descriptor_pb2 import FileDescriptorProto, DescriptorProto

def create_proto_file(filename):
    """Creates a new protobuf file with the given filename.

    Args:
        filename: The name of the protobuf file to create.

    Returns:
        The newly created protobuf file.
    """

    # Create a new protobuf file object.
    file = FileDescriptorProto()

    # Add a message to the file.
    message = DescriptorProto()
    message.name = "MyMessage"
    file.message_type.append(message)

    # Write the file to disk.
    with open(filename, "wb") as f:
        f.write(file.SerializeToString())

# Example usage
create_proto_file("example.proto")

def compile():
    import os

    protoc_exe = "libs\protoc-25.1-win64\\bin\\protoc.exe"
    protoc_libs = "libs\protoc-25.1-win64\\include\\google\\protobuf"

    example_proto = "example.proto"

    compile_proto_command = f"{protoc_exe} --python_out=. {example_proto}"
    print(compile_proto_command)
    os.system(compile_proto_command)

compile() 

