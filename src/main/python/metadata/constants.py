import os


"""Constants for Crawler"""
DEFAULT_ENCODING = 'utf-8'
REQUEST_TIME_OUT = 5
REQUEST_MAX_TIME = 10

PROVINCE_CURL_JSON_PATH = f"{os.path.dirname(__file__)}/config/curl.json"

"""Constants for Database Writer"""
NAME_MAPPING_JSON_PATH = f"{os.path.dirname(__file__)}/json/name_mapping.json"
MAPPING_SAVE_PATH = f"{os.path.dirname(__file__)}/data/mapping/"

"""Constants for Both"""
METADATA_SAVE_PATH = f"{os.path.dirname(__file__)}/data/metadata/"
