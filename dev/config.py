from os import path

ENCODING = 'utf-8'

BASE_DIR = path.dirname(path.abspath(__file__))

"""
Пути для хранения статичных файлов
"""

STATIC_PATH = 'static'

DATASETS_FOLDER = "datasets"
DATASETS_FOLDER_ABS_PATH = path.join(BASE_DIR, STATIC_PATH, DATASETS_FOLDER)

DATASETS_PATHS = {
    "ASCCDCV"   : "All Sites combined concentration data clean version.xlsx",
    "ARGAZAL"   : "Argentine All Zones all Winds.xlsx",
    "ARMAZAL"   : "Armourdale All Zones All Winds.xlsx",
    "BWQAS"     : "beach-water-quality-automated-sensors-1.csv",
    "BWSAS"     : "beach-weather-stations-automated-sensors-1.csv",
    "DTFSHZPG"  : "Data Table for Science Hub Zhou paper Gullett.xlsx",
    "IOTNL"     : "IoT_Network_Logs.csv",
    "IOTTEMP"   : "IOT-temp.csv",
    "IOT1"      : "IoTpond1.csv",
    "IOT2"      : "IoTPond2.csv",
    "IOT3"      : "IoTPond3.csv",
    "IOT4"      : "IoTPond4.csv",
    "IOT6"      : "IoTPond6.csv",
    "IOT7"      : "IoTPond7.csv",
    "IOT8"      : "IoTPond8.csv",
    "IOT9"      : "IoTPond9.csv",
    "IOT10"     : "IoTPond10.csv",
    "IOT11"     : "IoTPond11.csv",
    "IOT12"     : "IoTPond12.csv",
    "MELPED"    : "Melbourne Pedestrians.csv",
    "TAZAW"     : "Turner All Zones All Winds.xls"
}

DATASETS_ABS_PATHS = {dataset: path.join(DATASETS_FOLDER_ABS_PATH, dataset_path) for dataset, dataset_path in DATASETS_PATHS.items()}

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

LOG_FILE = 'logs.log'
LOG_FILES_PATH = 'logs'

LOG_ABS_PATH = path.join(BASE_DIR, LOG_FILES_PATH, LOG_FILE)

'''
Настройки loguru
'''
LOG_FORMAT = '{time} | {level} | {message}'
LOG_ROTATION = '10 MB'
