import argparse
import json
import os

import pymysql
from constants import MAPPING_SAVE_PATH, METADATA_SAVE_PATH, NAME_MAPPING_JSON_PATH
from util import log_error

parser = argparse.ArgumentParser()
parser.add_argument("--db-host", type=str)
parser.add_argument("--db-port", type=int)
parser.add_argument("--db-user", type=str)
parser.add_argument("--db-pswd", type=str)
parser.add_argument("--database", type=str)
parser.add_argument("--table", type=str)
parser.add_argument("--ref-table", type=str, default="metadata")

parser.add_argument("--mapping-path", type=str, default=MAPPING_SAVE_PATH)
parser.add_argument("--metadata-path", type=str, default=METADATA_SAVE_PATH)
parser.add_argument("--name-map-path", type=str, default=NAME_MAPPING_JSON_PATH)

args = parser.parse_args()

DB_HOST = args.db_host
DB_PORT = args.db_port
DB_USER = args.db_user
DB_PSWD = args.db_pswd
DATABASE_NAME = args.database
TABLE_NAME = args.table
REF_TABLE_NAME = args.ref_table

mapping_path = args.mapping_path
metadata_path = args.metadata_path
name_map_path = args.name_map_path

db = pymysql.connect(host=DB_HOST,
                     port=DB_PORT,
                     user=DB_USER,
                     password=DB_PSWD,
                     database=DATABASE_NAME,
                     charset='utf8')

c = db.cursor()

def write_metadata():
    field_names = [
        'title', 'description', 'tags', 'department', 'category', 'publish_time', 'update_time', 'is_open',
        'data_volume', 'industry', 'update_frequency', 'telephone', 'email', 'data_formats', 'url'
    ]

    with open(name_map_path, "r", encoding="utf-8") as f:
        name_mapping = json.load(f)
    cnt = 0

    province_city = {}
    path = metadata_path
    file_list = os.listdir(metadata_path)

    sql = f"CREATE TABLE IF NOT EXISTS {TABLE_NAME} LIKE {REF_TABLE_NAME}"
    c.execute(sql)

    # sql = f"SELECT DISTINCT province, city FROM {TABLE_NAME}"
    # c.execute(sql)
    # finished_list = c.fetchall()
    # finished_list = [x[0] + '_' + x[1] for x in finished_list]
    # print(finished_list)

    sql = f"INSERT INTO {TABLE_NAME} VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    for file in file_list:
        file_name = file.split('.')[0]
        province, city = file_name.split('_')
        if not name_mapping.get(province):
            continue
        if not name_mapping[province].get(city):
            continue
        city = name_mapping[province][city]
        province = name_mapping[province][province]
        # if province + '_' + city in finished_list:
        #     continue
        if province not in province_city:
            province_city[province] = []
        province_city[province].append(city)
        # print(province, city)
        metadata_file_path = os.path.join(path, file)
        assert os.path.isfile(metadata_file_path)
        mapping_file_path = os.path.join(mapping_path, file)
        if not os.path.exists(mapping_file_path):
            log_error("database-writer: file '%s' does not exist.", mapping_file_path)
            continue
        with open(mapping_file_path, 'r', encoding='utf-8') as json_file:
            mapping_dict = json.load(json_file)
        if not os.path.exists(metadata_file_path):
            log_error("database-writer: file '%s' does not exist.", metadata_file_path)
            continue
        with open(metadata_file_path, 'r', encoding='utf-8') as json_file:
            metadata_list = json.load(json_file)
        dataset_list = []
        for dataset in metadata_list:
            metadata = {}
            for key, value in dataset.items():
                if key in mapping_dict:
                    metadata[mapping_dict[key]] = str(value)
            di = []
            di.append(None)
            for field in field_names:
                di.append(metadata[field]) if field in metadata else di.append(None)
                if field in metadata and metadata[field] is not None and metadata[field] not in ["暂无", "无", ""]:
                    cnt += 1
            di.append(province)
            di.append(city)
            di.append(None)
            dataset_list.append(di)
        # print(len(dataset_list[0]))
        # print(dataset_list[0])
        c.executemany(sql, dataset_list)
        db.commit()
        # finished_list.append(file_name)
        # print(cnt)


def stastic():
    format_cnt = {}
    sql = f"SELECT data_formats FROM {TABLE_NAME}"
    c.execute(sql)
    formats = c.fetchall()
    for fi in formats:
        if fi[0] is None:
            continue
        format_list = fi[0].split(',')
        for i in format_list:
            if i not in format_cnt:
                format_cnt[i] = 0
            format_cnt[i] += 1
    format_cnt = sorted(format_cnt.items(), key=lambda x: x[1], reverse=True)
    for i in format_cnt:
        print(i[0], i[1])


write_metadata()
# stastic()

c.close()