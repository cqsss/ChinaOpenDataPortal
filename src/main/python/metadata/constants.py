import os


"""Constants"""
DEFAULT_ENCODING = 'utf-8'
REQUEST_TIME_OUT = 5
REQUEST_MAX_TIME = 10

PROVINCE_CURL_JSON_PATH = f"{os.path.dirname(__file__)}/config/curl.json"
NAME_MAPPING_JSON_PATH = f"{os.path.dirname(__file__)}/json/name_mapping.json"

PROVINCE_LIST = ['shandong', 'jiangsu']

METADATA_SAVE_PATH = f"{os.path.dirname(__file__)}/data/metadata/"

MAPPING_SAVE_PATH = f"{os.path.dirname(__file__)}/data/mapping/"
