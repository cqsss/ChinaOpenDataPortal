import json
import os

import pymysql
from constants import MAPPING_SAVE_PATH, METADATA_SAVE_PATH, NAME_MAPPING_JSON_PATH

db = pymysql.connect(host='172.28.96.1',
                     port=8906,
                     user='root',
                     password='',
                     database='china_open_data_portal_2023',
                     charset='utf8')

c = db.cursor()
TABLE_NAME = 'metadata_test_bshan'

def write_metadata():
    field_names = [
        'title', 'description', 'tags', 'department', 'category', 'publish_time', 'update_time', 'is_open',
        'data_volume', 'industry', 'update_frequency', 'telephone', 'email', 'data_formats', 'url'
    ]

    with open(NAME_MAPPING_JSON_PATH, "r", encoding="utf-8") as f:
        name_mapping = json.load(f)
    cnt = 0

    province_city = {}
    path = METADATA_SAVE_PATH
    file_list = os.listdir(METADATA_SAVE_PATH)

    sql = f"SELECT DISTINCT province, city FROM {TABLE_NAME}"

    c.execute(sql)
    finished_list = c.fetchall()
    finished_list = [x[0] + '_' + x[1] for x in finished_list]
    print(finished_list)

    sql = f"INSERT INTO {TABLE_NAME} VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    for file in file_list:
        file_name = file.split('.')[0]
        province, city = file_name.split('_')
        city = name_mapping[province][city]
        province = name_mapping[province][province]
        if province + '_' + city in finished_list:
            continue
        if province not in province_city:
            province_city[province] = []
        province_city[province].append(city)
        print(province, city)
        metadata_file_path = os.path.join(path, file)
        assert os.path.isfile(metadata_file_path)
        mapping_file_path = MAPPING_SAVE_PATH + file
        with open(mapping_file_path, 'r', encoding='utf-8') as json_file:
            mapping_dict = json.load(json_file)
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
        print(len(dataset_list[0]))
        print(dataset_list[0])
        c.executemany(sql, dataset_list)
        db.commit()
        finished_list.append(file_name)
        print(cnt)


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