from typing import List
from generated import example_pb2
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.message import Message
import pandas as pd
import inflection
from dateutil import parser


def get_proto_message(data: pd.Series) -> Message:
    columns = data.keys()
    columns_underscore = [
        inflection.underscore(column).replace(" ", "_") for column in data.keys()
    ]
    message = example_pb2.MyMessage()
    for proto_attr_name, column_name in zip(columns_underscore, columns):
        to_set = data[column_name]
        if type(getattr(message, proto_attr_name)) == Timestamp:
            date = parser.parse(data[column_name])
            getattr(message, proto_attr_name).FromDatetime(dt=date)
            continue
        setattr(message, proto_attr_name, to_set)
    return message


def get_proto_messages(df: pd.DataFrame) -> List[Message]:

    columns = df.columns
    columns_underscore = [
        inflection.underscore(column).replace(" ", "_") for column in df.columns
    ]

    messages = []
    for row in df.iloc:
        try:
            message = example_pb2.MyMessage()
            for proto_attr_name, column_name in zip(columns_underscore, columns):
                to_set = row[column_name]
                if type(getattr(message, proto_attr_name)) == Timestamp:
                    date = parser.parse(row[column_name])
                    getattr(message, proto_attr_name).FromDatetime(dt=date)
                    continue
                setattr(message, proto_attr_name, to_set)
            messages.append(message)
        except Exception as e:
            print(e)
    return messages
