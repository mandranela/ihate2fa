import json
import os
import pandas as pd
import os.path
from parse import get_proto_message
from settings import compression_dict
import logging

logging.basicConfig(level=logging.INFO)


def compression_loop(df: pd.DataFrame, compression: str, format: str):
    compressor = compression_dict[compression]
    while True:
        try:
            for index, message in df.iterrows():
                if index % 10 == 0:
                    logging.info(
                        f"{compression = } {format = } Compressing {index} message"
                    )
                if format == "json":
                    encoded = json.dumps(message.to_dict()).encode()
                else:
                    proto_messages = get_proto_message(message)
                    encoded = proto_messages.SerializeToString()
                compressor(encoded)
        except Exception:
            logging.exception("Something went wrong!")
            raise


def start_power_measure(df):
    compression = os.environ["COMPRESSION"]
    format = os.environ["FORMAT"]
    compression_loop(df, compression, format)


if __name__ == "__main__":
    beach_sensors = "/datasets/beach-weather-stations-automated-sensors-1.csv"
    df = pd.read_csv(beach_sensors)
    df = df.replace(r"^\s*$", None, regex=True)
    df = df.dropna(axis=0)
    df = df.reset_index(drop=True)
    start_power_measure(df)
