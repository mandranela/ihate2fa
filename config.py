from os import path

ENCODING = "utf-8"

BASE_DIR = path.dirname(path.abspath(__file__))

"""
Пути для хранения статичных файлов
"""

STATIC_PATH = "static"

DATASETS_FOLDER = "datasets"
DATASETS_FOLDER_REL_PATH = path.join(STATIC_PATH, DATASETS_FOLDER)
DATASETS_FOLDER_ABS_PATH = path.join(BASE_DIR, STATIC_PATH, DATASETS_FOLDER)

DATASETS_PATHS = {
    "ASCCDCV": "all_sites_combined_concentration_data_clean_version.xlsx",
    "ARGAZAL": "argentine_all_zones_all_winds.xlsx",
    "ARMAZAL": "armourdale_all_zones_all_winds.xlsx",
    "BWQAS": "beach_water_quality_automated_sensors_1.csv",
    "BWSAS": "beach_weather_stations_automated_sensors_1.csv",
    "IOTNL": "iot_network_logs.csv",
    "IOTTEMP": "iot_temp.csv",
    "IOT1": "iotpond1.csv",
    "IOT2": "iotpond2.csv",
    "IOT3": "iotpond3.csv",
    "IOT4": "iotpond4.csv",
    "IOT6": "iotpond6.csv",
    "IOT7": "iotpond7.csv",
    "IOT8": "iotpond8.csv",
    "IOT9": "iotpond9.csv",
    "IOT10": "iotpond10.csv",
    "IOT11": "iotpond11.csv",
    "IOT12": "iotpond12.csv",
    "TAZAW": "turner_all_zones_all_winds.xlsx",
}

DATASETS_REL_PATHS = {
    dataset: path.join(DATASETS_FOLDER_REL_PATH, dataset_path)
    for dataset, dataset_path in DATASETS_PATHS.items()
}
DATASETS_ABS_PATHS = {
    dataset: path.join(DATASETS_FOLDER_ABS_PATH, dataset_path)
    for dataset, dataset_path in DATASETS_PATHS.items()
}

"""
Пути для хранения сторонних библиотек
"""

PROTOC_EXE = "libs\\protoc-25.1-win64\\bin\\protoc.exe"
PROTOC_LIBS = "libs\\protoc-25.1-win64\\include\\google\\protobuf"

"""
Пути для хранения динамичных файлов
"""

PROTOS_FOLDER = "protos"
MESSAGES_FOLDER = "messages"

PROTOS_FOLDER_ABS_PATH = path.join(BASE_DIR, PROTOS_FOLDER)
MESSAGES_FOLDER_ABS_PATH = path.join(BASE_DIR, MESSAGES_FOLDER)

"""
Логи
"""

LOG_FILE = "logs.log"
LOG_FILES_PATH = "logs"

LOG_ABS_PATH = path.join(BASE_DIR, LOG_FILES_PATH, LOG_FILE)

"""
Настройки loguru
"""
LOG_FORMAT = "{time} | {level} | {message}"
LOG_ROTATION = "10 MB"
