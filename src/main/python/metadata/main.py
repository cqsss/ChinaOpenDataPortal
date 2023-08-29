from concurrent.futures import ThreadPoolExecutor
import json
import re
import time
import copy
import urllib
import bs4
import requests

from constants import (METADATA_SAVE_PATH, PROVINCE_CURL_JSON_PATH, REQUEST_TIME_OUT)
from detail import Detail
from resultlist import ResultList

from util import log_error

curls = {}


class Crawler:
    def __init__(self, province, city):
        self.province = province
        self.city = city
        self.result_list = ResultList(self.province, self.city)
        self.detail = Detail(self.province, self.city)
        self.result_list_curl = curls[province][city]['resultList']
        self.detail_list_curl = curls[province][city]['detail']
        self.metadata_list = []

    def crawl(self):
        func_name = f"crawl_{str(self.province)}_{str(self.city)}"
        func = getattr(self, func_name, self.crawl_other)
        func()

    def log_result_list_error(self, stat):
        log_error("%s_%s crawl: get result list error, %s", self.province, self.city, stat)

    def logs_detail_error(self, link, action):
        log_error("%s_%s crawl: get detail error with %s -> %s", self.province, self.city, link, action)

    def crawl_beijing_beijing(self):
        for page in range(1, 1600):
            curl = self.result_list_curl.copy()
            curl['data']['curPage'] = str(page)
            links = None
            try_cnt = 0
            while not links:
                try_cnt += 1
                if try_cnt >= 3:
                    break
                try:
                    links = self.result_list.get_result_list(curl)
                except (requests.exceptions.ProxyError, requests.exceptions.SSLError) as e:
                    links = None
                    time.sleep(5)
                    self.log_result_list_error(f"retrying at page {page}...")
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] = link
                metadata = None
                try_cnt = 0
                while not metadata:
                    try_cnt += 1
                    if try_cnt >= 3:
                        break
                    try:
                        metadata = self.detail.get_detail(curl)
                        self.metadata_list.append(metadata)
                    except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as e:
                        time.sleep(5)
                        metadata = None
                        self.logs_detail_error(link, "continue")
                    except AttributeError as e:
                        # e.g. https://data.beijing.gov.cn/zyml/ajg/sswj1/598f4a53ae9d4cbe88074777572b38d5.htm
                        self.logs_detail_error(link, "break")
                        break

    def crawl_tianjin_tianjin(self):
        curl = self.result_list_curl.copy()
        link_format_data = self.result_list.get_result_list(curl)
        for data in link_format_data:
            curl = self.detail_list_curl.copy()
            curl['url'] = data['link']
            metadata = None
            while not metadata:
                try:
                    metadata = self.detail.get_detail(curl)
                    metadata['url'] = data['link']
                    metadata['format'] = data['format']
                    self.metadata_list.append(metadata)
                except requests.exceptions.ProxyError as e:
                    metadata = None
                    self.logs_detail_error(data['link'], "continue")

    def crawl_hebei_hebei(self):
        for page in range(1, 128):
            curl = self.result_list_curl.copy()
            curl['data']['pageNo'] = str(page)
            metadata_ids = self.result_list.get_result_list(curl)
            for metadata_id in metadata_ids:
                curl = self.detail_list_curl.copy()
                curl['data']['rowkey'] = metadata_id['METADATA_ID']
                curl['data']['list_url'] = curl['data']['list_url'].format(page)
                metadata = self.detail.get_detail(curl)
                metadata['所属主题'] = metadata_id['THEME_NAME']
                metadata['发布时间'] = metadata_id['CREAT_DATE']
                metadata['更新日期'] = metadata_id['UPDATE_DATE']
                self.metadata_list.append(metadata)

    def crawl_shanxi_datong(self):
        for page in range(1, 61):
            curl = self.result_list_curl.copy()
            curl['queries']['pageNumber'] = str(page)
            links = self.result_list.get_result_list(curl)
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link
                metadata = self.detail.get_detail(curl)
                metadata['url'] = curl['url']
                self.metadata_list.append(metadata)

    def crawl_shanxi_changzhi(self):
        for page in range(1, 17):
            curl = self.result_list_curl.copy()
            curl['data']['start'] = str((page - 1) * int(curl['data']['pageLength']))
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = self.detail_list_curl.copy()
                curl['queries']['cata_id'] = id
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_shanxi_jincheng(self):
        for page in range(1, 57):
            curl = self.result_list_curl.copy()
            curl['data']['curPage'] = str(page)
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = self.detail_list_curl.copy()
                curl['url'] = curl['url'].format(id)
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_shanxi_yuncheng(self):
        for page in range(1, 5):
            curl = self.result_list_curl.copy()
            curl['queries']['pageIndex'] = str(page)
            links = self.result_list.get_result_list(curl)
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_neimenggu_neimenggu(self):
        for page in range(1, 8):
            curl = self.result_list_curl.copy()
            curl['data']['page'] = str(page)
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = self.detail_list_curl.copy()
                curl['data']['id'] = id
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_neimenggu_xinganmeng(self):
        for page in range(1, 24):
            curl = self.result_list_curl.copy()
            curl['data']['pageNum'] = page
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = self.detail_list_curl.copy()
                curl['url'] = curl['url'].format(id)
                metadata = self.detail.get_detail(curl)
                metadata['url'] = curl['detail_url'].format(id)
                self.metadata_list.append(metadata)

    def crawl_liaoning_liaoning(self):
        for page in range(1, 26):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_liaoning_shenyang(self):
        for page in range(1, 202):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_heilongjiang_harbin(self):
        for page in range(1, 295):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    # def crawl_jilin_jilin(self):
    #     for page in range(1, 25):
    #         curl = self.result_list_curl.copy()
    #         curl['data']['page'] = str(page)
    #         links = self.result_list.get_result_list(curl)
    #         for link in links:
    #             curl = self.detail_list_curl.copy()
    #             curl['url'] += link
    #             metadata = self.detail.get_detail(curl)
    #             self.metadata_list.append(metadata)

    def crawl_shanghai_shanghai(self):
        for page in range(1, 451):
            curl = self.result_list_curl.copy()
            curl['data'] = curl['data'].replace('\"pageNum\":1', f'\"pageNum\":{page}').encode()
            dataset_ids = self.result_list.get_result_list(curl)
            for dataset_id in dataset_ids:
                curl = self.detail_list_curl.copy()
                curl['headers']['Referer'] = curl['headers']['Referer'].format(
                    dataset_id['datasetId'], urllib.parse.quote(dataset_id['datasetName']))
                curl['url'] = curl['url'].format(dataset_id['datasetId'])
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_jiangsu_jiangsu(self):
        for city, max_page in zip(['', 'all'], [54, 11]):
            for page in range(0, max_page):
                curl = self.result_list_curl.copy()
                curl['data'] = curl['data'].format(page, city)
                rowGuid_tag_list = self.result_list.get_result_list(curl)
                for rowGuid, tags in rowGuid_tag_list:
                    curl = self.detail_list_curl.copy()
                    curl['url'] = curl['url'].format(rowGuid)
                    curl['data'] = curl['data'].format(rowGuid)
                    metadata = self.detail.get_detail(curl)
                    metadata["数据格式"] = tags
                    metadata["详情页网址"] = curl['headers']['Referer'].format(rowGuid)
                    self.metadata_list.append(metadata)

    # def crawl_jiangsu_nanjing(self):
    #     curl = self.result_list_curl.copy()
    #     links = self.result_list.get_result_list(curl)

    def crawl_jiangsu_wuxi(self):
        for page in range(1, 295):
            curl = self.result_list_curl.copy()
            curl['data']['page'] = str(page)
            cata_ids = self.result_list.get_result_list(curl)
            for cata_id in cata_ids:
                curl = self.detail_list_curl.copy()
                curl['params']['cata_id'] = cata_id
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_jiangsu_xuzhou(self):
        for page in range(1, 43):
            curl = self.result_list_curl.copy()
            curl['json_data']['pageNo'] = page
            mlbhs = self.result_list.get_result_list(curl)
            for mlbh in mlbhs:
                curl = self.detail_list_curl.copy()
                curl['params']['mlbh'] = mlbh
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_jiangsu_suzhou(self):
        for page in range(1, 162):
            curl = self.result_list_curl.copy()
            curl['params']['current'] = str(page)
            curl['json_data']['current'] = str(page)
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = self.detail_list_curl.copy()
                curl['params']['id'] = id
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_jiangsu_nantong(self):
        for page in range(120):
            curl = self.result_list_curl.copy()
            curl['params']['page'] = str(page)
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = self.detail_list_curl.copy()
                curl['params']['id'] = id
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_jiangsu_lianyungang(self):
        for page in range(1, 111):
            curl = self.result_list_curl.copy()
            curl['params']['pageNum1'] = str(page)
            dmids = self.result_list.get_result_list(curl)
            for dmid in dmids:
                curl = self.detail_list_curl.copy()
                curl['params']['dmid'] = dmid
                valid, metadata = self.detail.get_detail(curl)
                if valid:
                    self.metadata_list.append(metadata)

    def crawl_jiangsu_huaian(self):
        for page in range(1, 130):
            curl = self.result_list_curl.copy()
            curl['params']['pageNum'] = str(page)
            catalogIds = self.result_list.get_result_list(curl)
            for catalogId in catalogIds:
                curl = self.detail_list_curl.copy()
                curl['params']['catalogId'] = catalogId
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_jiangsu_yancheng(self):
        for page in range(1, 99):
            curl = self.result_list_curl.copy()
            curl['params']['pageNumber'] = str(page)
            catalogPks = self.result_list.get_result_list(curl)
            for catalogPk in catalogPks:
                curl = self.detail_list_curl.copy()
                curl['params']['catalogId'] = catalogPk
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_jiangsu_zhenjiang(self):
        for page in range(215):
            curl = self.result_list_curl.copy()
            curl['params']['page'] = str(page)
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = self.detail_list_curl.copy()
                curl['params']['id'] = id
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_jiangsu_taizhou(self):
        for page in range(1, 541):
            curl = self.result_list_curl.copy()
            curl['params']['page'] = str(page)
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = self.detail_list_curl.copy()
                curl['url'] = curl['url'].format(id)
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_jiangsu_suqian(self):
        for page in range(1, 268):
            curl = self.result_list_curl.copy()
            curl['params']['page'] = str(page)
            id_infos = self.result_list.get_result_list(curl)
            for id, update_time in id_infos:
                curl = self.detail_list_curl.copy()
                curl['url'] = curl['url'].format(id)
                metadata = self.detail.get_detail(curl)
                metadata["更新时间"] = update_time
                self.metadata_list.append(metadata)

    def crawl_zhejiang_zhejiang(self):
        for page in range(1, 132):
            curl = self.result_list_curl.copy()
            curl['data']['pageNumber'] = str(page)
            iids = self.result_list.get_result_list(curl)
            for iid in iids:
                curl = self.detail_list_curl.copy()
                curl['queries'] = iid
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_zhejiang_hangzhou(self):
        for page in range(1, 660):
            curl = self.result_list_curl.copy()
            post_data_json = json.loads(curl['data']['postData'])
            post_data_json['pageSplit']['pageNumber'] = page
            curl['data']['postData'] = json.dumps(post_data_json)
            id_formats = self.result_list.get_result_list(curl)
            for id, mformat in id_formats:
                curl = copy.deepcopy(self.detail_list_curl)
                curl['format'] = mformat
                curl['url'] = curl['url'].format(mformat)
                curl['headers']['Referer'] = curl['headers']['Referer'].format(mformat, id)
                post_data_json = json.loads(curl['data']['postData'])
                post_data_json['source_id'] = id
                curl['data']['postData'] = json.dumps(post_data_json)
                metadata = self.detail.get_detail(curl)
                if metadata is None:
                    continue
                metadata["数据格式"] = mformat
                self.metadata_list.append(metadata)

    def crawl_zhejiang_ningbo(self):
        for page in range(1, 177):
            curl = self.result_list_curl.copy()
            curl['json_data']['pageNo'] = str(page)
            uuids = self.result_list.get_result_list(curl)
            for uuid in uuids:
                curl = self.detail_list_curl.copy()
                curl['json_data']['uuid'] = uuid
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_zhejiang_wenzhou(self):
        for page in range(1, 51):
            curl = self.result_list_curl.copy()
            curl['data']['pageNumber'] = str(page)
            iids = self.result_list.get_result_list(curl)
            for iid in iids:
                curl = self.detail_list_curl.copy()
                curl['params']['iid'] = iid['iid']
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_zhejiang_jiaxing(self):
        for page in range(1, 20):
            curl = self.result_list_curl.copy()
            curl['data']['pageNumber'] = str(page)
            iids = self.result_list.get_result_list(curl)
            for iid in iids:
                curl = self.detail_list_curl.copy()
                curl['params']['iid'] = iid['iid']
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_zhejiang_shaoxing(self):
        for page in range(1, 75):
            if page == 3:
                continue
            curl = self.result_list_curl.copy()
            curl['json_data']['pageNum'] = page
            iids = self.result_list.get_result_list(curl)
            for iid in iids:
                curl = self.detail_list_curl.copy()
                curl['params']['dataId'] = iid
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_zhejiang_jinhua(self):
        for page in range(1, 39):
            curl = self.result_list_curl.copy()
            curl['data']['pageNumber'] = str(page)
            iids = self.result_list.get_result_list(curl)
            for iid in iids:
                curl = self.detail_list_curl.copy()
                curl['params']['iid'] = iid['iid']
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_zhejiang_quzhou(self):
        for page in range(1, 51):
            curl = self.result_list_curl.copy()
            curl['data']['pageNumber'] = str(page)
            iids = self.result_list.get_result_list(curl)
            for iid in iids:
                curl = self.detail_list_curl.copy()
                curl['params']['iid'] = iid['iid']
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_zhejiang_zhoushan(self):
        for page in range(1, 12):
            curl = self.result_list_curl.copy()
            curl['json_data']['pageNo'] = page
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = self.detail_list_curl.copy()
                curl['params']['id'] = id
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_zhejiang_taizhou(self):
        for page in range(1, 108):
            curl = self.result_list_curl.copy()
            curl['json_data']['pageNum'] = page
            iids = self.result_list.get_result_list(curl)
            for iid in iids:
                curl = self.detail_list_curl.copy()
                curl['params']['dataId'] = iid
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_zhejiang_lishui(self):
        for page in range(1, 44):
            curl = self.result_list_curl.copy()
            curl['data']['pageNumber'] = str(page)
            iids = self.result_list.get_result_list(curl)
            for iid in iids:
                curl = self.detail_list_curl.copy()
                curl['params']['iid'] = iid['iid']
                metadata = self.detail.get_detail(curl)
                if metadata is not None:
                    self.metadata_list.append(metadata)

    def crawl_anhui_anhui(self):
        for page in range(1, 100000000):
            curl = self.result_list_curl.copy()
            curl['data']['pageNum'] = str(page)
            rids = self.result_list.get_result_list(curl)
            if len(rids) == 0:
                break
            for rid in rids:
                curl = self.detail_list_curl.copy()
                curl['headers']['Referer'] = curl['headers']['Referer'].format(rid)
                curl['data']['rid'] = rid
                metadata = self.detail.get_detail(curl)
                metadata['url'] = 'http://data.ahzwfw.gov.cn:8000/dataopen-web/api-data-details.html?rid=' + rid
                self.metadata_list.append(metadata)

    def crawl_anhui_hefei(self):
        for page in range(1, 34):
            curl = self.result_list_curl.copy()
            curl['queries']['currentPageNo'] = str(page)
            # curl['queries']['_'] = str(int(round(time.time() * 1000)))
            # curl['headers']['Referer'] = curl['headers']['Referer'].format(str(page))
            ids = self.result_list.get_result_list(curl)
            if len(ids) == 0:
                self.log_result_list_error(f"break at page {page}.")
                break
            for iid, zyId in ids:
                curl = self.detail_list_curl.copy()
                curl['data']['id'] = iid
                curl['data']['zyId'] = zyId
                metadata = self.detail.get_detail(curl)
                metadata["详情页网址"] = f'https://www.hefei.gov.cn/open-data-web/data/detail-hfs.do?&id={iid}&zyId={zyId}'
                self.metadata_list.append(metadata)

    def crawl_anhui_wuhu(self):
        for page in range(1, 37):
            curl = self.result_list_curl.copy()
            curl['data']['pageNo'] = str(page)
            metadata_list = self.result_list.get_result_list(curl)
            if len(metadata_list) == 0:
                break
            self.metadata_list.extend(metadata_list)

    def crawl_anhui_bengbu(self):
        # dataset
        for page in range(0, 8):
            curl = self.result_list_curl.copy()
            curl['queries']['pageIndex'] = str(page)
            ids = self.result_list.get_result_list(curl)
            if len(ids) == 0:
                break
            for iid in ids:
                curl = self.detail_list_curl.copy()
                curl['queries']['resourceId'] = re.search(r"(?<=resourceId=)\d+", iid).group(0)
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = 'https://www.bengbu.gov.cn' + iid
                if metadata['下载格式'][0] == '':
                    metadata['下载格式'] = ['file']
                self.metadata_list.append(metadata)
        # api
        for page in range(0, 2):
            curl = self.result_list_curl.copy()
            curl['queries']['pageIndex'] = str(page)
            curl['queries']['resourceType'] = 'api'
            ids = self.result_list.get_result_list(curl)
            if len(ids) == 0:
                break
            for iid in ids:
                curl = self.detail_list_curl.copy()
                curl['queries']['resourceId'] = re.search(r"(?<=resourceId=)\d+", iid).group(0)
                curl['url'] = 'https://www.bengbu.gov.cn/site/tpl/6541'
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = 'https://www.bengbu.gov.cn' + iid
                metadata['下载格式'] = ['api']
                self.metadata_list.append(metadata)

    def crawl_anhui_huainan(self):
        for page in range(1, 5):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            data_ids = self.result_list.get_result_list(curl)
            if len(data_ids) == 0:
                break
            for data_id in data_ids:
                curl = self.detail_list_curl.copy()
                curl['queries']['dataId'] = str(data_id)
                metadata = self.detail.get_detail(curl)
                metadata['url'] = 'https://sjzyj.huainan.gov.cn/odssite/view/page/govDataFile?pageIndex=' + metadata[
                    '数据类型'] + '&dataId=' + str(data_id)
                self.metadata_list.append(metadata)

    def crawl_anhui_huaibei(self):
        for page in range(1, 39):
            curl = self.result_list_curl.copy()
            curl['queries']['curPageNumber'] = str(page)
            ids = self.result_list.get_result_list(curl)
            if len(ids) == 0:
                break
            for iid in ids:
                curl = self.detail_list_curl.copy()
                curl['queries']['id'] = iid
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = 'http://open.huaibeidata.cn:1123/#/data_public/detail/' + iid
                self.metadata_list.append(metadata)

    def crawl_anhui_huangshan(self):
        # dataset
        for page in range(1, 26):
            curl = self.result_list_curl.copy()
            curl['queries']['pageIndex'] = str(page)
            time.sleep(1)
            ids = self.result_list.get_result_list(curl)
            if len(ids) == 0:
                break
            for iid, depart, cata, format_list in ids:
                curl = self.detail_list_curl.copy()
                curl['queries']['resourceId'] = re.search(r"(?<=resourceId=)\d+", iid).group(0)
                time.sleep(1)
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = 'https://www.huangshan.gov.cn' + iid
                metadata['提供机构'] = depart
                metadata['数据领域'] = cata
                metadata['资源格式'] = format_list
                metadata['开放条件'] = '无条件开放'
                self.metadata_list.append(metadata)

    def crawl_anhui_chuzhou(self):
        for page in range(0, 86):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            time.sleep(1)
            metadata_list = self.result_list.get_result_list(curl)
            if len(metadata_list) == 0:
                break
            for meta in metadata_list:
                curl = self.detail_list_curl.copy()
                curl['queries']['name'] = meta['标题']
                time.sleep(1)
                remains = self.detail.get_detail(curl)
                remains.update(meta)
                self.metadata_list.append(remains)

    def crawl_anhui_suzhou(self):
        for page in range(1, 54):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            if len(links) == 0:
                break
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link['link']
                metadata = self.detail.get_detail(curl)
                metadata['数据格式'] = link['data_formats']
                metadata['url'] = curl['url']
                self.metadata_list.append(metadata)

    def crawl_anhui_luan(self):
        for page in range(1, 56):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            if len(links) == 0:
                break
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link['link']
                metadata = self.detail.get_detail(curl)
                metadata['数据格式'] = link['data_formats']
                metadata['url'] = curl['url']
                self.metadata_list.append(metadata)

    def crawl_anhui_chizhou(self):
        for page in range(1, 276):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            metadatas = self.result_list.get_result_list(curl)
            if len(metadatas) == 0:
                break
            for metadata in metadatas:
                self.metadata_list.append(metadata)

    def crawl_fujian_fujian(self):
        for page in range(1, 737):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link
                metadata = self.detail.get_detail(curl)
                metadata['url'] = curl['url']
                self.metadata_list.append(metadata)

    def crawl_fujian_fuzhou(self):
        for page in range(1, 116):
            curl = self.result_list_curl.copy()
            curl['data']['pageNo'] = str(page)
            res_ids = self.result_list.get_result_list(curl)
            for res_id in res_ids:
                curl = self.detail_list_curl.copy()
                curl['data']['resId'] = res_id
                metadata = self.detail.get_detail(curl)
                metadata['url'] = 'http://data.fuzhou.gov.cn/data/catalog/toDataCatalog'
                self.metadata_list.append(metadata)

    def crawl_fujian_xiamen(self):
        for page in range(1, 102):
            curl = self.result_list_curl.copy()
            curl['data']['page']['currentPage'] = str(page)
            catalog_ids = self.result_list.get_result_list(curl)
            for catalog_id in catalog_ids:
                curl = self.detail_list_curl.copy()
                curl['queries']['catalogId'] = catalog_id
                metadata = self.detail.get_detail(curl)
                metadata['url'] = curl['url'] + '?' + catalog_id
                self.metadata_list.append(metadata)

    def crawl_jiangxi_jiangxi(self):
        for page in range(1, 29):
            curl = self.result_list_curl.copy()
            curl['data']['current'] = page
            data_ids = self.result_list.get_result_list(curl)
            for data_id in data_ids:
                curl = self.detail_list_curl.copy()
                curl['headers']['Referer'] = curl['headers']['Referer'].format(data_id['dataId'])
                curl['queries']['dataId'] = data_id['dataId']
                metadata = self.detail.get_detail(curl)
                if metadata == {}:
                    continue
                metadata['数据格式'] = '[' + data_id['filesType'] + ']' if data_id['filesType'] is not None else ''
                metadata['url'] = 'https://data.jiangxi.gov.cn/open-data/detail?id=' + data_id['dataId']
                self.metadata_list.append(metadata)

    # def crawl_jiangxi_ganzhou(self):
    #     for page in range(1, 24):
    #         curl = self.result_list_curl.copy()
    #         curl['url'] = curl['url'].format(page)
    #         ids = self.result_list.get_result_list(curl)
    #         for id in ids:
    #             curl = self.detail_list_curl.copy()
    #             curl['url'] = curl['url'].format(id)
    #             metadata = self.detail.get_detail(curl)
    #             if metadata == {}:
    #                 continue
    #             metadata['url'] = 'https://data.jiangxi.gov.cn/open-data/detail?id=' + data_id['dataId']
    #             self.metadata_list.append(metadata)

    def crawl_shandong_common(self, use_cache=True, page_size=10):
        # TODO:debug
        # use_cache = False
        max_retry = 3
        page = 1
        retry_time = 0
        cache_dir = "./results/cache/"
        index_cache_dir = cache_dir + f"{self.province}_{self.city}_index_cache.txt"
        data_cache_dir = cache_dir + f"{self.province}_{self.city}_data_cache.json"
        if use_cache:
            cache_page = self.prepare_cache(cache_dir, index_cache_dir, data_cache_dir, page_size)
            page += cache_page

        # for page in range(637, 638):
        while (True):
            # TODO:加文件类型
            curl = self.result_list_curl.copy()
            curl['params']['page'] = str(page)
            page += 1
            links = self.result_list.get_result_list(curl)
            if not len(links):
                if retry_time >= max_retry:
                    return
                else:
                    retry_time += 1
                    continue
            retry_time = 0  # 重置
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link['link']
                metadata = self.detail.get_detail(curl)
                metadata["数据格式"] = link['data_formats']  # TODO：扔到detail方法里面
                metadata["详情页网址"] = curl['url']
                self.metadata_list.append(metadata)
            if use_cache:
                with open(index_cache_dir, 'w', encoding='utf-8') as page_writer:
                    page_writer.write(str(page))
                # TODO:append来提高效率
                with open(data_cache_dir, 'w', encoding='utf-8') as data_writer:
                    json.dump(self.metadata_list, data_writer, ensure_ascii=False)

    def crawl_shandong_shandong(self, use_cache=True, page_size=10):
        self.crawl_shandong_common(use_cache, page_size)

    def crawl_shandong_jinan(self, use_cache=True, page_size=10):
        self.crawl_shandong_common(use_cache, page_size)

    def crawl_shandong_qingdao(self, use_cache=True, page_size=10):
        self.crawl_shandong_common(use_cache, page_size)

    def crawl_shandong_zibo(self, use_cache=True, page_size=10):
        self.crawl_shandong_common(use_cache, page_size)

    def crawl_shandong_zaozhuang(self, use_cache=True, page_size=10):
        self.crawl_shandong_common(use_cache, page_size)

    def crawl_shandong_dongying(self, use_cache=True, page_size=10):
        self.crawl_shandong_common(use_cache, page_size)

    def crawl_shandong_yantai(self, use_cache=True, page_size=10):
        self.crawl_shandong_common(use_cache, page_size)

    def crawl_shandong_weifang(self, use_cache=True, page_size=10):
        self.crawl_shandong_common(use_cache, page_size)

    def crawl_shandong_jining(self, use_cache=True, page_size=10):
        self.crawl_shandong_common(use_cache, page_size)

    def crawl_shandong_taian(self, use_cache=True, page_size=10):
        self.crawl_shandong_common(use_cache, page_size)

    def crawl_shandong_weihai(self, use_cache=True, page_size=10):
        self.crawl_shandong_common(use_cache, page_size)

    def crawl_shandong_rizhao(self, use_cache=True, page_size=10):
        self.crawl_shandong_common(use_cache, page_size)

    def crawl_shandong_linyi(self, use_cache=True, page_size=10):
        self.crawl_shandong_common(use_cache, page_size)

    def crawl_shandong_dezhou(self, use_cache=True, page_size=10):
        self.crawl_shandong_common(use_cache, page_size)

    def crawl_shandong_liaocheng(self, use_cache=True, page_size=10):
        self.crawl_shandong_common(use_cache, page_size)

    def crawl_shandong_binzhou(self, use_cache=True, page_size=10):
        self.crawl_shandong_common(use_cache, page_size)

    def crawl_shandong_heze(self, use_cache=True, page_size=10):
        self.crawl_shandong_common(use_cache, page_size)

    def crawl_hubei_wuhan(self):
        all_ids = []
        for page in range(1, 236):
            curl = copy.deepcopy(self.result_list_curl)
            curl['data']['current'] = page
            curl['data']['size'] = 6
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                if id in all_ids:
                    continue
                else:
                    all_ids.append(id)
                curl = copy.deepcopy(self.detail_list_curl)
                curl['queries']['cataId'] = id
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_hubei_huangshi(self):
        all_ids = []
        curl = copy.deepcopy(self.result_list_curl)
        curl['url'] = curl['url'].format("1")
        ids = self.result_list.get_result_list(curl)
        for id in ids:
            if id in all_ids:
                continue
            else:
                all_ids.append(id)
            curl = copy.deepcopy(self.detail_list_curl)
            curl['queries']['infoid'] = id
            metadata = self.detail.get_detail(curl)
            self.metadata_list.append(metadata)

        curl = copy.deepcopy(self.result_list_curl)
        curl['url'] = curl['url'].format("0")
        ids = self.result_list.get_result_list(curl)
        for id in ids:
            if id in all_ids:
                continue
            else:
                all_ids.append(id)
            curl = copy.deepcopy(self.detail_list_curl)
            curl['queries']['infoid'] = id
            metadata = self.detail.get_detail(curl)
            self.metadata_list.append(metadata)

    def crawl_hubei_yichang(self):
        all_ids = []
        for page in range(1, 66):
            curl = copy.deepcopy(self.result_list_curl)
            curl['dataset']['crawl_type'] = 'dataset'
            curl['dataset']['data']['pageNum'] = page
            ids = self.result_list.get_result_list(curl['dataset'])
            for id in ids:
                if id in all_ids:
                    continue
                else:
                    all_ids.append(id)
                curl = copy.deepcopy(self.detail_list_curl)
                curl['dataset']['crawl_type'] = 'dataset'
                curl['dataset']['queries']['dataId'] = id
                metadata = self.detail.get_detail(curl['dataset'])
                self.metadata_list.append(metadata)
        for page in range(1, 14):
            curl = copy.deepcopy(self.result_list_curl)
            curl['interface']['crawl_type'] = 'interface'
            curl['interface']['data']['pageNum'] = page
            ids = self.result_list.get_result_list(curl['interface'])
            for id in ids:
                if id in all_ids:
                    continue
                else:
                    all_ids.append(id)
                curl = copy.deepcopy(self.detail_list_curl)
                curl['interface']['crawl_type'] = 'interface'
                curl['interface']['data']['baseDataId'] = id
                metadata = self.detail.get_detail(curl['interface'])
                self.metadata_list.append(metadata)

    def crawl_hubei_ezhou(self):
        all_ids = []
        for page in range(0, 30):
            curl = copy.deepcopy(self.result_list_curl)
            curl['hangye']['crawl_type'] = 'hangye'
            curl['hangye']['url'] = curl['hangye']['url'].format('index{}.html'.format(f'_{page}' if page else ''))
            urls = self.result_list.get_result_list(curl['hangye'])
            for url in urls:
                if url in all_ids:
                    continue
                else:
                    all_ids.append(url)
                curl = copy.deepcopy(self.detail_list_curl)
                curl['url'] = url
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)
        for page in range(0, 1):
            curl = copy.deepcopy(self.result_list_curl)
            curl['shiji']['crawl_type'] = 'shiji'
            curl['shiji']['url'] = curl['shiji']['url'].format('index{}.html'.format(f'_{page}' if page else ''))
            urls = self.result_list.get_result_list(curl['shiji'])
            for url in urls:
                if url in all_ids:
                    continue
                else:
                    all_ids.append(url)
                curl = copy.deepcopy(self.detail_list_curl)
                curl['url'] = url
                curl['api'] = True
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_hubei_jingzhou(self):
        all_ids = []
        for page in range(1, 121):
            curl = copy.deepcopy(self.result_list_curl)
            curl['queries']['page'] = page
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                if id in all_ids:
                    continue
                else:
                    all_ids.append(id)
                curl = copy.deepcopy(self.detail_list_curl)
                curl['url'] = curl['url'].format(id)
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_hubei_xianning(self):
        curl = copy.deepcopy(self.result_list_curl)
        response = requests.get(curl['url'], headers=curl['headers'])
        data = json.loads(response.text)
        for item in data:
            metadata = {
                '名称': item['title'],
                "详情页网址": item['link'],
                "创建时间": item['pubDate'],
                "更新时间": item['update'],
                "数据来源": item["department"],
                "数据领域": item['theme'],
                "文件类型": item['chnldesc']
            }
            metadata['更新时间'] = metadata['更新时间'].replace('年', '-').replace('月', '-').replace('日', '')
            metadata['创建时间'] = metadata['创建时间'].replace('年', '-').replace('月', '-').replace('日', '')
            metadata['文件类型'] = 'file' if metadata['文件类型'] == '数据集' else 'api'
            metadata['文件类型'] = metadata['文件类型'].split(',')
            self.metadata_list.append(metadata)

    def crawl_hubei_suizhou(self):
        all_ids = []
        for page in range(1, 48):
            curl = copy.deepcopy(self.result_list_curl)
            curl['url'] = curl['url'].format('dataSet')
            curl['data']['page'] = page
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                if id in all_ids:
                    continue
                else:
                    all_ids.append(id)
                curl = copy.deepcopy(self.detail_list_curl)
                curl['crawl_type'] = 'dataset'
                curl['url'] = curl['url'].format('dataSet/toDataDetails/' + str(id))
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)
        for page in range(1, 2):
            curl = copy.deepcopy(self.result_list_curl)
            curl['url'] = curl['url'].format('dataApi')
            curl['data']['page'] = page
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                if id in all_ids:
                    continue
                else:
                    all_ids.append(id)
                curl = copy.deepcopy(self.detail_list_curl)
                curl['crawl_type'] = 'api'
                curl['url'] = curl['url'].format('dataApi/toDataDetails/' + str(id))
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_hunan_yueyang(self):
        curl = copy.deepcopy(self.result_list_curl)
        response = requests.get(curl['all_type']['url'],
                                params=curl['all_type']['queries'],
                                headers=curl['all_type']['headers'],
                                verify=False,
                                timeout=REQUEST_TIME_OUT)
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        lis = soup.find_all('li', class_='list-group-item-action')
        type_ids = []
        for li in lis:
            text = str(li.find_next('a')['onclick'])
            type_ids.append(text.split('(')[1].split(')')[0].split(','))
        for type, id in type_ids:
            all_links = []
            for page in range(0, 5):
                curl = copy.deepcopy(self.result_list_curl)
                curl['frame']['queries']['dataInfo.offset'] = page * 6
                curl['frame']['queries']['type'] = type
                curl['frame']['queries']['id'] = id
                links = self.result_list.get_result_list(curl['frame'])
                for link in links:
                    if link in all_links:
                        continue
                    else:
                        all_links.append(link)
                    curl = copy.deepcopy(self.detail_list_curl)
                    curl['queries']['id'] = link
                    metadata = self.detail.get_detail(curl)
                    self.metadata_list.append(metadata)

    def crawl_hunan_changde(self):
        all_ids = []
        for page in range(1, 3):
            curl = copy.deepcopy(self.result_list_curl)
            curl['queries']['page'] = page
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                if id in all_ids:
                    continue
                else:
                    all_ids.append(id)
                curl = copy.deepcopy(self.detail_list_curl)
                curl['queries']['cataId'] = id
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_hunan_yiyang(self):
        curl = copy.deepcopy(self.result_list_curl)
        response = requests.get(curl['all_type']['url'],
                                headers=curl['all_type']['headers'],
                                verify=False,
                                timeout=REQUEST_TIME_OUT)
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        lis = soup.find_all('li', class_='wb-tree-item')
        type_ids = []
        for li in lis:
            text = str(li.find_next('a')['onclick'])
            type_ids.append(text.split('(')[1].split(')')[0].split(','))
        all_links = []
        for type, id in type_ids:
            before_links = []
            for page in range(0, 10):
                curl = copy.deepcopy(self.result_list_curl)
                curl['frame']['queries']['dataInfo.offset'] = page * 6
                curl['frame']['queries']['type'] = type
                curl['frame']['queries']['id'] = id
                links = self.result_list.get_result_list(curl['frame'])
                if links == before_links:
                    break
                before_links = links
                for link in links:
                    if link in all_links:
                        continue
                    else:
                        all_links.append(link)
                    curl = copy.deepcopy(self.detail_list_curl)
                    curl['queries']['id'] = link
                    metadata = self.detail.get_detail(curl)
                    self.metadata_list.append(metadata)

    def crawl_hunan_chenzhou(self):
        curl = copy.deepcopy(self.result_list_curl)
        response = requests.get(curl['all_type']['url'],
                                params=curl['all_type']['queries'],
                                headers=curl['all_type']['headers'],
                                verify=False,
                                timeout=REQUEST_TIME_OUT)
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        lis = soup.find_all('li', class_='wb-tree-item')
        type_ids = []
        for li in lis:
            text = str(li.find_next('a')['onclick'])
            type_ids.append(text.split('(')[1].split(')')[0].split(','))
        all_links = []
        for type, id in type_ids:
            before_links = []
            for page in range(0, 32):
                curl = copy.deepcopy(self.result_list_curl)
                curl['frame']['queries']['dataInfo.offset'] = page * 6
                curl['frame']['queries']['type'] = type
                curl['frame']['queries']['id'] = id
                links = self.result_list.get_result_list(curl['frame'])
                if before_links == links:
                    break
                before_links = links
                for link in links:
                    if link in all_links:
                        continue
                    else:
                        all_links.append(link)
                    curl = copy.deepcopy(self.detail_list_curl)
                    curl['queries']['id'] = link
                    metadata = self.detail.get_detail(curl)
                    self.metadata_list.append(metadata)

    def crawl_guangdong_guangdong(self):
        all_ids = []
        for page in range(1, 7574):
            curl = copy.deepcopy(self.result_list_curl)
            curl['dataset']['data']['pageNo'] = page
            curl['dataset']['crawl_type'] = 'dataset'
            ids = self.result_list.get_result_list(curl['dataset'])
            for id in ids:
                if id in all_ids:
                    continue
                else:
                    all_ids.append(id)
                curl = copy.deepcopy(self.detail_list_curl)
                curl['dataset']['crawl_type'] = 'dataset'
                curl['dataset']['data']['resId'] = id
                metadata = self.detail.get_detail(curl['dataset'])
                self.metadata_list.append(metadata)
        for page in range(1, 37):
            curl = copy.deepcopy(self.result_list_curl)
            curl['api']['data']['pageNo'] = page
            curl['api']['crawl_type'] = 'api'
            ids = self.result_list.get_result_list(curl['api'])
            for id in ids:
                if id in all_ids:
                    continue
                else:
                    all_ids.append(id)
                curl = copy.deepcopy(self.detail_list_curl)
                curl['api']['data']['resId'] = id
                curl['api']['crawl_type'] = 'api'
                metadata = self.detail.get_detail(curl['api'])
                self.metadata_list.append(metadata)

    def crawl_guangdong_guangzhou(self):
        all_ids = []
        for page in range(1, 129):
            curl = copy.deepcopy(self.result_list_curl)
            curl['data']['body']['useType'] = None
            curl['data']['page'] = page
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                if id in all_ids:
                    continue
                else:
                    all_ids.append(id)
                curl = copy.deepcopy(self.detail_list_curl)
                curl['detail']['url'] = curl['detail']['url'].format(id)
                curl['doc']['queries']['sid'] = id
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_guangdong_shenzhen(self):
        all_ids = []
        for page in range(1, 553):
            curl = copy.deepcopy(self.result_list_curl)
            curl['dataset']['data']['pageNo'] = page
            curl['dataset']['crawl_type'] = 'dataset'
            ids = self.result_list.get_result_list(curl['dataset'])
            for id in ids:
                if id in all_ids:
                    continue
                else:
                    all_ids.append(id)
                curl = copy.deepcopy(self.detail_list_curl)
                curl['data']['resId'] = id
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)
        for page in range(1, 548):
            curl = copy.deepcopy(self.result_list_curl)
            curl['api']['data']['pageNo'] = page
            curl['api']['crawl_type'] = 'api'
            ids = self.result_list.get_result_list(curl['api'])
            for id in ids:
                if id in all_ids:
                    continue
                else:
                    all_ids.append(id)
                curl = copy.deepcopy(self.detail_list_curl)
                curl['data']['resId'] = id
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_guangdong_zhongshan(self):
        all_ids = []
        for page in range(1, 85):
            curl = copy.deepcopy(self.result_list_curl)
            curl['data']['page'] = page
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                if id in all_ids:
                    continue
                else:
                    all_ids.append(id)
                curl = copy.deepcopy(self.detail_list_curl)
                curl['queries']['id'] = id
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_guangxi_guangxi(self):
        for page in range(1, 2000000):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            if len(links) == 0:
                break
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link['link']
                metadata = self.detail.get_detail(curl)
                if len(metadata):
                    metadata['详情页网址'] = curl['url']
                    metadata['数据格式'] = link['data_formats']
                    self.metadata_list.append(metadata)

    def crawl_guangxi_nanning(self):
        for page in range(1, 2000000):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            if len(links) == 0:
                break
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link['link']
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = curl['url']
                metadata['数据格式'] = link['data_formats']
                self.metadata_list.append(metadata)

    def crawl_guangxi_liuzhou(self):
        for page in range(1, 2000000):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            if len(links) == 0:
                break
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link['link']
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = curl['url']
                metadata['数据格式'] = link['data_formats']
                self.metadata_list.append(metadata)

    def crawl_guangxi_guilin(self):
        for page in range(1, 2000000):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            if len(links) == 0:
                break
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link['link']
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = curl['url']
                metadata['数据格式'] = link['data_formats']
                self.metadata_list.append(metadata)

    def crawl_guangxi_wuzhou(self):
        for page in range(1, 2000000):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            if len(links) == 0:
                break
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link['link']
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = curl['url']
                metadata['数据格式'] = link['data_formats']
                self.metadata_list.append(metadata)

    def crawl_guangxi_beihai(self):
        for page in range(1, 2000000):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            if len(links) == 0:
                break
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link['link']
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = curl['url']
                metadata['数据格式'] = link['data_formats']
                self.metadata_list.append(metadata)

    def crawl_guangxi_fangchenggang(self):
        for page in range(1, 2000000):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            if len(links) == 0:
                break
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link['link']
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = curl['url']
                metadata['数据格式'] = link['data_formats']
                self.metadata_list.append(metadata)

    def crawl_guangxi_qinzhou(self):
        for page in range(1, 2000000):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            if len(links) == 0:
                break
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link['link']
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = curl['url']
                metadata['数据格式'] = link['data_formats']
                self.metadata_list.append(metadata)

    def crawl_guangxi_guigang(self):
        for page in range(1, 2000000):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            if len(links) == 0:
                break
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link['link']
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = curl['url']
                metadata['数据格式'] = link['data_formats']
                self.metadata_list.append(metadata)

    def crawl_guangxi_yulin(self):
        for page in range(1, 2000000):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            if len(links) == 0:
                break
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link['link']
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = curl['url']
                metadata['数据格式'] = link['data_formats']
                self.metadata_list.append(metadata)

    def crawl_guangxi_baise(self):
        for page in range(1, 2000000):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            if len(links) == 0:
                break
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link['link']
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = curl['url']
                metadata['数据格式'] = link['data_formats']
                self.metadata_list.append(metadata)

    def crawl_guangxi_hezhou(self):
        for page in range(1, 2000000):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            if len(links) == 0:
                break
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link['link']
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = curl['url']
                metadata['数据格式'] = link['data_formats']
                self.metadata_list.append(metadata)

    def crawl_guangxi_hechi(self):
        for page in range(1, 2000000):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            if len(links) == 0:
                break
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link['link']
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = curl['url']
                metadata['数据格式'] = link['data_formats']
                self.metadata_list.append(metadata)

    def crawl_guangxi_laibin(self):
        for page in range(1, 2000000):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            if len(links) == 0:
                break
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link['link']
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = curl['url']
                metadata['数据格式'] = link['data_formats']
                self.metadata_list.append(metadata)

    def crawl_guangxi_chongzuo(self):
        for page in range(1, 2000000):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            if len(links) == 0:
                break
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link['link']
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = curl['url']
                metadata['数据格式'] = link['data_formats']
                self.metadata_list.append(metadata)

    def crawl_hainan_hainan(self):
        for page in range(0, 100000):
            curl = self.result_list_curl.copy()
            curl['data']['curPage'] = page
            ids = self.result_list.get_result_list(curl)
            if len(ids) == 0:
                break
            for id in ids:
                curl = self.detail_list_curl.copy()
                curl['url'] = curl['url'].format(id)
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = curl['url']
                self.metadata_list.append(metadata)

    def crawl_chongqing_chongqing(self):

        curl = self.result_list_curl.copy()
        # curl['data']['variables']['input']['offset'] = page * 10
        metadatas = self.result_list.get_result_list(curl)
        # if len(metadatas) == 0:
        #     break
        for metadata in metadatas:
            self.metadata_list.append(metadata)

    def crawl_sichuan_sichuan(self):
        for page in range(1, 1249):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            if len(links) == 0:
                break
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link['link']
                metadata = self.detail.get_detail(curl)
                if bool(metadata):
                    metadata['数据格式'] = link['data_formats'] if link['data_formats'] != '[]' else "['file']"
                    metadata['详情页网址'] = curl['url']
                    self.metadata_list.append(metadata)

    def crawl_sichuan_chengdu(self):
        for page in range(1, 704):
            # for page in range(1, 704):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            time.sleep(5)
            links = self.result_list.get_result_list(curl)
            if len(links) == 0:
                break
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link['link']
                metadata = self.detail.get_detail(curl)
                if bool(metadata):
                    metadata['数据格式'] = link['data_formats'] if link['data_formats'] != '[]' else "['file']"
                    metadata['详情页网址'] = curl['url']
                    self.metadata_list.append(metadata)

    def crawl_sichuan_zigong(self):
        for page in range(1, 870):
            curl = self.result_list_curl.copy()
            time.sleep(5)
            curl['queries']['offset'] = str((page - 1) * 10)
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = self.detail_list_curl.copy()
                curl['queries']['id'] = id
                metadata = self.detail.get_detail(curl)
                if bool(metadata):
                    metadata['详情页网址'] = 'https://data.zg.cn/snww/sjzy/detail.html?' + id
                    # 根据可下载类型获取type
                    turl = curls[self.province][self.city]['typeList'].copy()
                    turl['queries']['id'] = id
                    response = requests.get(turl['url'],
                                            params=turl['queries'],
                                            headers=turl['headers'],
                                            timeout=REQUEST_TIME_OUT)
                    if response.status_code != requests.codes.ok:
                        self.logs_detail_error(turl['url'], f'break with response code {response.status_code}')
                        type_json = dict()
                    else:
                        type_json = json.loads(response.text)['data']
                    if not bool(type_json):
                        type_json = dict()
                    type_list = []
                    for name, type_info in type_json.items():
                        type_list.append(type_info['type'])
                    metadata['数据格式'] = str(type_list) if bool(type_list) else "['file']"
                    self.metadata_list.append(metadata)

    def crawl_sichuan_panzhihua(self):
        for page in range(1, 700):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            if len(links) == 0:
                break
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link['link']
                metadata = self.detail.get_detail(curl)
                if bool(metadata):
                    metadata['数据格式'] = link['data_formats'] if link['data_formats'] != '[]' else "['file']"
                    metadata['详情页网址'] = curl['url']
                    self.metadata_list.append(metadata)

    def crawl_sichuan_luzhou(self):
        for page in range(1, 701):
            # for page in range(1, 701):
            curl = self.result_list_curl.copy()
            time.sleep(5)
            curl['data']['page'] = str(page)
            ids = self.result_list.get_result_list(curl)
            for id, opens, publisht, updatet in ids:
                curl = self.detail_list_curl.copy()
                curl['queries']['id'] = id
                curl['queries']['type'] = "opendata"
                metadata = self.detail.get_detail(curl)
                if bool(metadata):
                    metadata['开放条件'] = "无条件开放" if opens == '1' else "有条件开放"
                    metadata['详情页网址'] = 'https://data.luzhou.cn/portal/service_detail?id=' + id + '&type=opendata'
                    metadata['发布时间'] = publisht
                    metadata['更新时间'] = updatet
                    metadata['数据格式'] = "['api']"
                    self.metadata_list.append(metadata)

    def crawl_sichuan_deyang(self):
        for page in range(1, 99):
            curl = self.result_list_curl.copy()
            time.sleep(5)
            curl['data']['pageNo'] = page
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = self.detail_list_curl.copy()
                curl['queries']['mlbh'] = id
                metadata = self.detail.get_detail(curl)
                if bool(metadata):
                    metadata['详情页网址'] = "https://www.dysdsj.cn/#/DataSet/" + id.replace("/", "%2F")
                    self.metadata_list.append(metadata)

    def crawl_sichuan_mianyang(self):
        for page in range(1, 1297):
            curl = self.result_list_curl.copy()
            # time.sleep(5)
            curl['queries']['startNum'] = str((page - 1) * 8)
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = self.detail_list_curl.copy()
                curl['queries']['id'] = id
                metadata = self.detail.get_detail(curl)
                if bool(metadata):
                    metadata['详情页网址'] = "https://data.mianyang.cn/zwztzlm/index.jhtml?caseid=" + id
                    metadata['数据格式'] = "['api']"  # 只有数据库和接口类型，实际全是接口
                    self.metadata_list.append(metadata)
            if page % 100 == 0:
                self.save_matadata_as_json(METADATA_SAVE_PATH)
                self.metadata_list.clear()

    def crawl_sichuan_guangyuan(self):
        for page in range(1, 1874):
            curl = self.result_list_curl.copy()
            # time.sleep(3)
            curl['data']['currentPage'] = page
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = self.detail_list_curl.copy()
                curl['data']['id'] = str(id)
                metadata = self.detail.get_detail(curl)
                if bool(metadata):
                    metadata['详情页网址'] = "http://data.cngy.gov.cn/open/index.html?id=user&messid=" + str(id)
                    metadata['领域名称'] = "生活服务"
                    metadata['行业名称'] = "公共管理、社会保障和社会组织"
                    self.metadata_list.append(metadata)
            if page % 100 == 0:
                self.save_matadata_as_json(METADATA_SAVE_PATH)
                self.metadata_list.clear()

    def crawl_sichuan_suining(self):
        for page in range(1, 910):
            curl = self.result_list_curl.copy()
            curl['data']['pageNo'] = page
            ids = self.result_list.get_result_list(curl)
            for id, typeList in ids:
                curl = self.detail_list_curl.copy()
                curl['queries']['mlbh'] = id
                metadata = self.detail.get_detail(curl)
                if bool(metadata):
                    metadata['详情页网址'] = "https://www.suining.gov.cn/data#/DataSet/" + id.replace("/", "%2F")
                    type_mapping = {'10': 'csv', '04': 'xlsx', '08': 'xml', '09': 'json'}
                    type_list = ['api']
                    for label in typeList:
                        type_list.append(type_mapping[label])
                    metadata['资源格式'] = str(type_list)
                    self.metadata_list.append(metadata)
            if page % 100 == 0:
                self.save_matadata_as_json(METADATA_SAVE_PATH)
                self.metadata_list.clear()

    def crawl_sichuan_neijiang(self):
        for page in range(0, 317):
            curl = self.result_list_curl.copy()
            curl['data']['page'] = page
            curl['queries']['page'] = str(page)
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = self.detail_list_curl.copy()
                curl['data']['id'] = id
                metadata = self.detail.get_detail(curl)
                if bool(metadata):
                    metadata['详情页网址'] = "https://www.neijiang.gov.cn/neiJiangPublicData/resourceCatalog/detail?id=" + id
                    self.metadata_list.append(metadata)
            if page % 100 == 0:
                self.save_matadata_as_json(METADATA_SAVE_PATH)
                self.metadata_list.clear()

    def crawl_sichuan_leshan(self):
        for page in range(1, 1575):
            curl = self.result_list_curl.copy()
            # time.sleep(3)
            curl['queries']['pageIndex'] = str(page)
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = self.detail_list_curl.copy()
                curl['queries']['resourceId'] = id
                metadata = self.detail.get_detail(curl)
                if bool(metadata):
                    metadata['详情页网址'] = "https://www.leshan.gov.cn/data/#/source_catalog_detail/" + id + "/0"
                    self.metadata_list.append(metadata)
            if page % 100 == 0:
                self.save_matadata_as_json(METADATA_SAVE_PATH)
                self.metadata_list.clear()

    def crawl_sichuan_nanchong(self):
        for page in range(1, 1655):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = self.detail_list_curl.copy()
                curl['queries']['id'] = id
                metadata = self.detail.get_detail(curl)
                if bool(metadata):
                    metadata['详情页网址'] = "https://www.nanchong.gov.cn/data/catalog/details.html?id=" + id
                    self.metadata_list.append(metadata)
            # 响应太慢了，每次都写入吧
            self.save_matadata_as_json(METADATA_SAVE_PATH)
            self.metadata_list.clear()

    def crawl_sichuan_meishan(self):
        for page in range(1, 617):
            curl = self.result_list_curl.copy()
            curl['data']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            for link in links:
                curl = self.detail_list_curl.copy()
                #curl['headers']['Referer'] = "http://data.ms.gov.cn/portal/service_detail?id="+link['id']+"&type=opendata&orgId==#tabLink1"
                curl['queries']['id'] = link['id']
                metadata = self.detail.get_detail(curl)
                metadata["标题"] = link['serviceName']
                # metadata["提供单位"]=link['orgName']
                # metadata["发布时间"]=link['publishTime']
                # metadata["行业名称"]=link['industryName']


                self.metadata_list.append(metadata)
            time.sleep(5)

    def crawl_sichuan_yibin(self):
        for page in range(1, 444):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            if len(links) == 0:
                break
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link['link']
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = curl['url']
                metadata['数据格式'] = link['data_formats']
                self.metadata_list.append(metadata)
            time.sleep(5)

    def crawl_sichuan_dazhou(self):
        for page in range(1, 565):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            if len(links) == 0:
                break
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link['link']
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = curl['url']
                metadata['数据格式'] = link['data_formats']
                self.metadata_list.append(metadata)
            time.sleep(5)

    def crawl_sichuan_yaan(self):
        for page in range(1, 840):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            if len(links) == 0:
                break
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link['link']
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = curl['url']
                metadata['数据格式'] = link['data_formats']
                self.metadata_list.append(metadata)
            time.sleep(5)

    def crawl_sichuan_bazhong(self):
        for page in range(1, 1809):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            if len(links) == 0:
                break
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['queries']['dataCatalogId'] = link
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = "https://www.bzgongxiang.com/#/dataCatalog/catalogDetail/" + link
                self.metadata_list.append(metadata)

    def crawl_sichuan_aba(self):
        for page in range(1, 739):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            if len(links) == 0:
                break
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['queries']['tableId'] = str(link)
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = "http://abadata.cn/ABaPrefectureGateway/open/api/getTableDetail?tableId" + str(link)
                self.metadata_list.append(metadata)

    def crawl_sichuan_ganzi(self):
        for page in range(1, 1192):
            curl = self.result_list_curl.copy()
            curl['data']['pageNo'] = page
            links = self.result_list.get_result_list(curl)
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['queries']['mlbh'] = link
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = "http://182.132.59.11:11180/dexchange/open/#/DataSet/" + link.replace('/', "%2F")
                self.metadata_list.append(metadata)

    def crawl_guizhou_guizhou(self):
        for page in range(1, 1368):
            curl = self.result_list_curl.copy()
            curl['data']['pageIndex'] = page
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = self.detail_list_curl.copy()
                curl['data']['id'] = id['id']
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = "http://data.guizhou.gov.cn/open-data/" + id['id']
                metadata['数据格式'] = id['resourceFormats']
                self.metadata_list.append(metadata)

    def crawl_guizhou_guiyang(self):
        for page in range(1, 207):
            curl = self.result_list_curl.copy()
            curl['data']['pageIndex'] = page
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = self.detail_list_curl.copy()
                curl['data']['id'] = id['id']
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = "http://data.guizhou.gov.cn/open-data/" + id['id']
                metadata['数据格式'] = id['resourceFormats']
                self.metadata_list.append(metadata)

    def crawl_guizhou_liupanshui(self):
        for page in range(1, 84):
            curl = self.result_list_curl.copy()
            curl['data']['pageIndex'] = page
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = self.detail_list_curl.copy()
                curl['data']['id'] = id['id']
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = "http://data.guizhou.gov.cn/open-data/" + id['id']
                metadata['数据格式'] = id['resourceFormats']
                self.metadata_list.append(metadata)

    def crawl_guizhou_zunyi(self):
        for page in range(1, 122):
            curl = self.result_list_curl.copy()
            curl['data']['pageIndex'] = page
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = self.detail_list_curl.copy()
                curl['data']['id'] = id['id']
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = "http://data.guizhou.gov.cn/open-data/" + id['id']
                metadata['数据格式'] = id['resourceFormats']
                self.metadata_list.append(metadata)

    def crawl_guizhou_anshun(self):
        for page in range(1, 108):
            curl = self.result_list_curl.copy()
            curl['data']['pageIndex'] = page
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = self.detail_list_curl.copy()
                curl['data']['id'] = id['id']
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = "http://data.guizhou.gov.cn/open-data/" + id['id']
                metadata['数据格式'] = id['resourceFormats']
                self.metadata_list.append(metadata)

    def crawl_guizhou_bijie(self):
        for page in range(1, 123):
            curl = self.result_list_curl.copy()
            curl['data']['pageIndex'] = page
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = self.detail_list_curl.copy()
                curl['data']['id'] = id['id']
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = "http://data.guizhou.gov.cn/open-data/" + id['id']
                metadata['数据格式'] = id['resourceFormats']
                self.metadata_list.append(metadata)

    def crawl_guizhou_tongren(self):
        for page in range(1, 86):
            curl = self.result_list_curl.copy()
            curl['data']['pageIndex'] = page
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = self.detail_list_curl.copy()
                curl['data']['id'] = id['id']
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = "http://data.guizhou.gov.cn/open-data/" + id['id']
                metadata['数据格式'] = id['resourceFormats']
                self.metadata_list.append(metadata)

    def crawl_guizhou_qianxinan(self):
        for page in range(1, 54):
            curl = self.result_list_curl.copy()
            curl['data']['pageIndex'] = page
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = self.detail_list_curl.copy()
                curl['data']['id'] = id['id']
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = "http://data.guizhou.gov.cn/open-data/" + id['id']
                metadata['数据格式'] = id['resourceFormats']
                self.metadata_list.append(metadata)

    def crawl_guizhou_qiandongnan(self):
        for page in range(1, 132):
            curl = self.result_list_curl.copy()
            curl['data']['pageIndex'] = page
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = self.detail_list_curl.copy()
                curl['data']['id'] = id['id']
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = "http://data.guizhou.gov.cn/open-data/" + id['id']
                metadata['数据格式'] = id['resourceFormats']
                self.metadata_list.append(metadata)

    def crawl_guizhou_qiannan(self):
        for page in range(1, 131):
            curl = self.result_list_curl.copy()
            curl['data']['pageIndex'] = page
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = self.detail_list_curl.copy()
                curl['data']['id'] = id['id']
                metadata = self.detail.get_detail(curl)
                metadata['详情页网址'] = "http://data.guizhou.gov.cn/open-data/" + id['id']
                metadata['数据格式'] = id['resourceFormats']
                self.metadata_list.append(metadata)

    def crawl_shaanxi_shaanxi(self):
        for page in range(1, 16):
            curl = self.result_list_curl.copy()
            curl['queries']['page.pageNo'] = str(page)
            metas = self.result_list.get_result_list(curl)
            self.metadata_list.extend(metas)
            if page % 100 == 0:
                self.save_matadata_as_json(METADATA_SAVE_PATH)
                self.metadata_list.clear()

    def crawl_ningxia_ningxia(self):
        for page in range(1, 202):
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            if len(links) == 0:
                break
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link['link']
                metadata = self.detail.get_detail(curl)
                if bool(metadata):
                    metadata['数据格式'] = link['data_formats'] if link['data_formats'] != '[]' else "['file']"
                    metadata['详情页网址'] = curl['url']
                    self.metadata_list.append(metadata)
            if page % 100 == 0:
                self.save_matadata_as_json(METADATA_SAVE_PATH)
                self.metadata_list.clear()

    def crawl_ningxia_yinchuan(self):
        for page in range(1, 169):
            curl = self.result_list_curl.copy()
            curl['data']['start'] = str((page - 1) * 6)
            ids = self.result_list.get_result_list(curl)
            if len(ids) == 0:
                break
            for cata_id, formate in ids:
                curl = self.detail_list_curl.copy()
                curl['queries']['cata_id'] = cata_id
                metadata = self.detail.get_detail(curl)
                if bool(metadata):
                    metadata['详情页网址'] = "http://data.yinchuan.gov.cn/odweb/catalog/catalogDetail.htm?cata_id=" + cata_id
                    formate_mapping = {'1': 'xls', '2': 'xml', '3': 'json', '4': 'csv'}
                    if formate is None:
                        metadata['数据格式'] = "['file']"
                    else:
                        type_list = [formate_mapping[s.strip()] for s in formate.split(',')[:-1]]
                        metadata['数据格式'] = str(type_list)
                    self.metadata_list.append(metadata)

    def crawl_xinjiang_wulumuqi(self):
        for page in range(1, 18):
            curl = self.result_list_curl.copy()
            curl['data']['start'] = str((page - 1) * 6)
            ids = self.result_list.get_result_list(curl)
            if len(ids) == 0:
                break
            for cata_id, formate in ids:
                curl = self.detail_list_curl.copy()
                curl['queries']['cata_id'] = cata_id
                metadata = self.detail.get_detail(curl)
                if bool(metadata):
                    metadata['详情页网址'] = "http://zwfw.wlmq.gov.cn/odweb/catalog/catalogDetail.htm?cata_id=" + cata_id
                    formate_mapping = {'1': 'xls', '2': 'xml', '3': 'json', '4': 'csv'}
                    if formate is None:
                        metadata['数据格式'] = "['file']"
                    else:
                        type_list = [formate_mapping[s.strip()] for s in formate.split(',')[:-1]]
                        metadata['数据格式'] = str(type_list)
                    self.metadata_list.append(metadata)
            if page % 100 == 0:
                self.save_matadata_as_json(METADATA_SAVE_PATH)
                self.metadata_list.clear()

    def crawl_other(self):
        log_error("crawl: 暂无该省")

    def save_metadata_as_json(self, save_dir):
        filename = save_dir + self.province + '_' + self.city + '.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.metadata_list, f, ensure_ascii=False)


if __name__ == '__main__':
    requests.packages.urllib3.disable_warnings()

    with open(PROVINCE_CURL_JSON_PATH, 'r', encoding='utf-8') as curlFile:
        curls = json.load(curlFile)

    pool = ThreadPoolExecutor(max_workers=20)

    def crawl_then_save(province, city):
        crawler = Crawler(province, city)
        crawler.crawl()
        crawler.save_metadata_as_json(METADATA_SAVE_PATH)

    for province in curls:
        for city in curls[province]:
            pool.submit(crawl_then_save, province, city)

    pool.shutdown()


    # crawler = Crawler("chongqing", "chongqing")
    # crawler.crawl()
    # crawler.save_metadata_as_json(METADATA_SAVE_PATH)
