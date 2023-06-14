import json
import urllib
import copy

import bs4

from constants import REQUEST_TIME_OUT
import requests

from constants import (METADATA_SAVE_PATH, PROVINCE_CURL_JSON_PATH, PROVINCE_LIST)
from detail import Detail
from resultlist import ResultList

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

    # TODO: 反爬虫 ConnectionResetError: [WinError 10054]
    def crawl_beijing_beijing(self):
        for page in range(1, 2):
            print(page)
            curl = self.result_list_curl.copy()
            curl['data']['curPage'] = str(page)
            links = self.result_list.get_result_list(curl)
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] = link
                metadata = self.detail.get_detail(curl)
                print(metadata)
                self.metadata_list.append(metadata)

    def crawl_tianjin_tianjin(self):
        curl = self.result_list_curl.copy()
        links = self.result_list.get_result_list(curl)
        for link in links[:10]:
            curl = self.detail_list_curl.copy()
            curl['url'] = link
            metadata = self.detail.get_detail(curl)
            print(metadata)
            self.metadata_list.append(metadata)

    def crawl_hebei_hebei(self):
        for page in range(1, 5):
            print(page)
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
                print(metadata)
                self.metadata_list.append(metadata)

    def crawl_neimenggu_neimenggu(self):
        for page in range(1, 5):
            print(page)
            curl = self.result_list_curl.copy()
            curl['data']['page'] = str(page)
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = self.detail_list_curl.copy()
                curl['data']['id'] = id
                metadata = self.detail.get_detail(curl)
                print(metadata)
                self.metadata_list.append(metadata)

    def crawl_liaoning_liaoning(self):
        for page in range(1, 5):
            print(page)
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link
                metadata = self.detail.get_detail(curl)
                print(metadata)
                self.metadata_list.append(metadata)

    def crawl_shandong_shandong(self):
        for page in range(1, 5):
            print(page)
            curl = self.result_list_curl.copy()
            curl['params']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link
                metadata = self.detail.get_detail(curl)
                print(metadata)
                self.metadata_list.append(metadata)

    def crawl_jiangsu_jiangsu(self):
        for city in ['', 'all']:
            for page in range(0, 10):
                print(page)
                curl = self.result_list_curl.copy()
                curl['data'] = curl['data'].format(page, city)
                rowGuids = self.result_list.get_result_list(curl)
                for rowGuid in rowGuids:
                    curl = self.detail_list_curl.copy()
                    curl['url'] = curl['url'].format(rowGuid)
                    curl['data'] = curl['data'].format(rowGuid)
                    metadata = self.detail.get_detail(curl)
                    print(metadata)
                    self.metadata_list.append(metadata)

    def crawl_shanghai_shanghai(self):
        for page in range(1, 5):
            print(page)
            curl = self.result_list_curl.copy()
            curl['data'] = curl['data'].replace('\"pageNum\":1', f'\"pageNum\":{page}').encode()
            dataset_ids = self.result_list.get_result_list(curl)
            for dataset_id in dataset_ids:
                curl = self.detail_list_curl.copy()
                curl['headers']['Referer'] = curl['headers']['Referer'].format(
                    dataset_id['datasetId'], urllib.parse.quote(dataset_id['datasetName']))
                curl['url'] = curl['url'].format(dataset_id['datasetId'])
                metadata = self.detail.get_detail(curl)
                print(metadata)
                self.metadata_list.append(metadata)

    def crawl_zhejiang_zhejiang(self):
        for page in range(1, 5):
            print(page)
            curl = self.result_list_curl.copy()
            curl['data']['pageNumber'] = str(page)
            iids = self.result_list.get_result_list(curl)
            for iid in iids:
                curl = self.detail_list_curl.copy()
                curl['queries'] = iid
                metadata = self.detail.get_detail(curl)
                print(metadata)
                self.metadata_list.append(metadata)

    def crawl_anhui_anhui(self):
        for page in range(1, 5):
            print(page)
            curl = self.result_list_curl.copy()
            curl['data']['pageNum'] = str(page)
            rids = self.result_list.get_result_list(curl)
            for rid in rids:
                curl = self.detail_list_curl.copy()
                curl['headers']['Referer'] = curl['headers']['Referer'].format(rid)
                curl['data']['rid'] = rid
                metadata = self.detail.get_detail(curl)
                print(metadata)
                self.metadata_list.append(metadata)

    def crawl_jiangxi_jiangxi(self):
        for page in range(1, 5):
            print(page)
            curl = self.result_list_curl.copy()
            curl['data']['current'] = page
            data_ids = self.result_list.get_result_list(curl)
            for data_id in data_ids:
                curl = self.detail_list_curl.copy()
                curl['headers']['Referer'] = curl['headers']['Referer'].format(data_id)
                curl['queries']['dataId'] = data_id
                metadata = self.detail.get_detail(curl)
                print(metadata)
                self.metadata_list.append(metadata)

    def crawl_fujian_fujian(self):
        for page in range(1, 5):
            print(page)
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link
                metadata = self.detail.get_detail(curl)
                print(metadata)
                self.metadata_list.append(metadata)

    def crawl_guangdong_guangdong(self):
        for page in range(1, 5):
            print(page)
            curl = self.result_list_curl.copy()
            curl['data']['pageNo'] = page
            res_ids = self.result_list.get_result_list(curl)
            for res_id in res_ids:
                curl = self.detail_list_curl.copy()
                curl['data']['resId'] = res_id
                metadata = self.detail.get_detail(curl)
                print(metadata)
                self.metadata_list.append(metadata)

    def crawl_guangxi_guangxi(self):
        for page in range(1, 5):
            print(page)
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link
                metadata = self.detail.get_detail(curl)
                print(metadata)
                self.metadata_list.append(metadata)

    def crawl_hainan_hainan(self):
        for page in range(0, 5):
            print(page)
            curl = self.result_list_curl.copy()
            curl['data']['curPage'] = page
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = self.detail_list_curl.copy()
                curl['url'] = curl['url'].format(id)
                metadata = self.detail.get_detail(curl)
                print(metadata)
                self.metadata_list.append(metadata)

    def crawl_ningxia_ningxia(self):
        for page in range(1, 5):
            print(page)
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link
                metadata = self.detail.get_detail(curl)
                print(metadata)
                self.metadata_list.append(metadata)

    def crawl_shaanxi_shaanxi(self):
        for page in range(1, 5):
            print(page)
            curl = self.result_list_curl.copy()
            curl['queries']['page.pageNo'] = str(page)
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = self.detail_list_curl.copy()
                curl['queries']['id'] = str(id)
                metadata = self.detail.get_detail(curl)
                print(metadata)
                self.metadata_list.append(metadata)

    def crawl_sichuan_sichuan(self):
        for page in range(1, 5):
            print(page)
            curl = self.result_list_curl.copy()
            curl['queries']['page'] = str(page)
            links = self.result_list.get_result_list(curl)
            for link in links:
                curl = self.detail_list_curl.copy()
                curl['url'] += link
                metadata = self.detail.get_detail(curl)
                print(metadata)
                self.metadata_list.append(metadata)

    def crawl_guizhou_guizhou(self):
        for page in range(1, 5):
            print(page)
            curl = self.result_list_curl.copy()
            curl['data']['pageIndex'] = page
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = self.detail_list_curl.copy()
                curl['data']['id'] = id
                metadata = self.detail.get_detail(curl)
                print(metadata)
                self.metadata_list.append(metadata)

    def crawl_hubei_wuhan(self):
        for page in range(1, 5):
            curl = copy.deepcopy(self.result_list_curl)
            curl['data']['current'] = page
            curl['data']['size'] = 6
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = copy.deepcopy(self.detail_list_curl)
                curl['queries']['cataId'] = id
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_hubei_yichang(self):
        for page in range(1, 5):
            curl = copy.deepcopy(self.result_list_curl)
            curl['dataset']['crawl_type'] = 'dataset'
            curl['dataset']['data']['pageNum'] = page
            ids = self.result_list.get_result_list(curl['dataset'])
            for id in ids:
                curl = copy.deepcopy(self.detail_list_curl)
                curl['dataset']['crawl_type'] = 'dataset'
                curl['dataset']['queries']['dataId'] = id
                metadata = self.detail.get_detail(curl['dataset'])
                self.metadata_list.append(metadata)
        for page in range(1,5):
            curl = copy.deepcopy(self.result_list_curl)
            curl['interface']['crawl_type'] = 'interface'
            curl['interface']['data']['pageNum'] = page
            ids = self.result_list.get_result_list(curl['interface'])
            for id in ids:
                curl = copy.deepcopy(self.detail_list_curl)
                curl['interface']['crawl_type'] = 'interface'
                curl['interface']['data']['baseDataId'] = id
                metadata = self.detail.get_detail(curl['interface'])
                self.metadata_list.append(metadata)

    def crawl_hubei_ezhou(self):
        for page in range(0, 5):
            curl = copy.deepcopy(self.result_list_curl)
            curl['hangye']['crawl_type'] = 'hangye'
            curl['hangye']['url'] = curl['hangye']['url'].format('index{}.html'.format(f'_{page}'if page else ''))
            urls = self.result_list.get_result_list(curl['hangye'])
            for url in urls:
                curl = copy.deepcopy(self.detail_list_curl)
                curl['url'] = url
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)
        for page in range(0,5):
            curl = copy.deepcopy(self.result_list_curl)
            curl['shiji']['crawl_type'] = 'shiji'
            curl['shiji']['url'] = curl['shiji']['url'].format('index{}.html'.format(f'_{page}'if page else ''))
            urls = self.result_list.get_result_list(curl['shiji'])
            for url in urls:
                curl = copy.deepcopy(self.detail_list_curl)
                curl['url'] = url
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_hubei_jingzhou(self):
        for page in range(1,5):
            curl = copy.deepcopy(self.result_list_curl)
            curl['queries']['page'] = page
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = copy.deepcopy(self.detail_list_curl)
                curl['url'] = curl['url'].format(id)
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_hubei_suizhou(self):
        for page in range(1, 5):
            curl = copy.deepcopy(self.result_list_curl)
            curl['url'] = curl['url'].format('dataSet')
            curl['data']['page'] = page
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = copy.deepcopy(self.detail_list_curl)
                curl['crawl_type'] = 'dataset'
                curl['url'] = curl['url'].format('dataSet/toDataDetails/'+str(id))
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)
        for page in range(1,5):
            curl = copy.deepcopy(self.result_list_curl)
            curl['url'] = curl['url'].format('dataApi')
            curl['data']['page'] = page
            ids = self.result_list.get_result_list(curl)
            for id in ids:
                curl = copy.deepcopy(self.detail_list_curl)
                curl['crawl_type'] = 'api'
                curl['url'] = curl['url'].format('dataApi/toDataDetails/'+str(id))
                metadata = self.detail.get_detail(curl)
                self.metadata_list.append(metadata)

    def crawl_hunan_yueyang(self):
        curl = copy.deepcopy(self.result_list_curl)
        response = requests.get(curl['all_type']['url'], params=curl['all_type']['queries'], headers=curl['all_type']['headers'], verify=False,
                                timeout=REQUEST_TIME_OUT)
        soup = bs4.BeautifulSoup(response.text,'html.parser')
        lis = soup.find_all('li',class_='list-group-item-action')
        type_ids = []
        for li in lis:
            text = str(li.find_next('a')['onclick'])
            type_ids.append(text.split('(')[1].split(')')[0].split(','))
        for type,id in type_ids:
            all_links = []
            for page in range(0,5):
                curl = copy.deepcopy(self.result_list_curl)
                curl['frame']['queries']['dataInfo.offset'] = page*6
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
        for page in range(1, 5):
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


    def crawl_other(self):
        print("暂无该省")

    def save_matadata_as_json(self, save_dir):
        filename = save_dir + self.province + '_' + self.city + '.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(f, self.metadata_list)

if __name__ == '__main__':
    provinces = PROVINCE_LIST
    with open(PROVINCE_CURL_JSON_PATH, 'r', encoding='utf-8') as curlFile:
        curls = json.load(curlFile)

    crawler = Crawler("anhui", "anhui")
    crawler.crawl()
    crawler.save_as_json(METADATA_SAVE_PATH)
    # for province in provinces:
    #     crawler = Crawler(province)
    #     crawler.crawl()
