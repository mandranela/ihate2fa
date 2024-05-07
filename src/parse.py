from typing import List
# from generated import example_pb2
from google.protobuf.internal.well_known_types import Timestamp
from google.protobuf.message import Message
import pandas as pd
import inflection
from dateutil import parser
from google.protobuf.descriptor_pb2 import FileDescriptorProto
from google.protobuf import message_factory
from google.protobuf import reflection

def get_proto_message_with_class(data: pd.Series, class_: Message) -> Message:  
    columns = data.keys()
    columns_underscore = [
        inflection.underscore(column).replace('/', '_').replace(' (', '_').replace('(', '_').replace(" ", "_").replace('.', '_').replace('(', '').replace(')', '') for column in data.keys()
    ]
    message = class_()

    for proto_attr_name, column_name in zip(columns_underscore, columns):
        to_set = data[column_name]
        if isinstance(getattr(message, proto_attr_name), Timestamp):
            attr: Timestamp = getattr(message, proto_attr_name)

            date = parser.parse(data[column_name])
            attr.FromDatetime(dt=date)
            continue
        if isinstance(getattr(message, proto_attr_name), int):
            setattr(message, proto_attr_name, int(to_set))
            continue
        setattr(message, proto_attr_name, to_set)
    return message

# def get_proto_message(data: pd.Series) -> Message:
#     columns = data.keys()
#     columns_underscore = [
#         inflection.underscore(column).replace(" ", "_") for column in data.keys()
#     ]
#     message = example_pb2.MyMessage()
#     for proto_attr_name, column_name in zip(columns_underscore, columns):
#         to_set = data[column_name]
#         if type(getattr(message, proto_attr_name)) == Timestamp:
#             date = parser.parse(data[column_name])
#             getattr(message, proto_attr_name).FromDatetime(dt=date)
#             continue
#         setattr(message, proto_attr_name, to_set)
#     return message


# def get_proto_messages(df: pd.DataFrame) -> List[Message]:

#     columns = df.columns
#     columns_underscore = [
#         inflection.underscore(column).replace(" ", "_") for column in df.columns
#     ]

#     messages = []
#     for row in df.iloc:
#         try:
#             message = example_pb2.MyMessage()
#             for proto_attr_name, column_name in zip(columns_underscore, columns):
#                 to_set = row[column_name]
#                 if type(getattr(message, proto_attr_name)) == Timestamp:
#                     date = parser.parse(row[column_name])
#                     getattr(message, proto_attr_name).FromDatetime(dt=date)
#                     continue
#                 setattr(message, proto_attr_name, to_set)
#             messages.append(message)
#         except Exception as e:
#             print(e)
#     return messages
