from os import path, system

import pandas as pd
from config import *


def compile_proto_BWSAS():
    M_BEACH_PROTO = path.join(PROTOS_FOLDER, "m_beach.proto")

    compile_proto_command = f"{PROTOC_EXE} --python_out=. {M_BEACH_PROTO}"
    system(compile_proto_command)


def timestamp2unix(timestamp):
    seconds = int(timestamp.timestamp())
    nanos = int(timestamp.timestamp() % 1 * 1e9)

    return (seconds, nanos)


def serialize_BWSAS(df):

    import protos.m_beach_pb2 as m_beach_pb2

    bwsas_messages = []
    for message in df.to_dict(orient='records'):
        
        bwsas_msg = m_beach_pb2.m_beach_message() 
        for field, value in message.items():
            if value is None:
                continue
            if type(value) is pd.Timestamp:
                seconds, nanos = timestamp2unix(value)
                setattr(getattr(bwsas_msg, field), "seconds", seconds)
                setattr(getattr(bwsas_msg, field), "nanos", nanos)
            else:
                try:
                    setattr(bwsas_msg, field, value)
                except Exception as e:
                    print(f"Exception: {e} | field: {field} | value: {value}")

        bwsas_messages.append(bwsas_msg)
    
    return bwsas_messages

