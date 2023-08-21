import json
import re
import urllib
from importlib.metadata import metadata

import requests
from bs4 import BeautifulSoup
from constants import REQUEST_TIME_OUT


class ResultList:
    def __init__(self, province, city) -> None:
        self.province = province
        self.city = city

    def get_result_list(self, curl):
        func_name = f"result_list_{str(self.province)}_{str(self.city)}"
        func = getattr(self, func_name, self.result_list_other)
        return func(curl)

    def result_list_beijing_beijing(self, curl):
        response = requests.post(curl['url'], data=curl['data'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        resultList = json.loads(response.text)['object']['docs']
        print(resultList)
        links = [x['url'] for x in resultList]
        return links

    def result_list_tianjin_tianjin(self, curl):
        response = requests.get(curl['url'], timeout=REQUEST_TIME_OUT)
        resultList = json.loads(response.text)['dataList']
        links = [x['href'] for x in resultList]
        return links

    def result_list_hebei_hebei(self, curl):
        response = requests.post(curl['url'],
                                 headers=curl['headers'],
                                 data=curl['data'],
                                 timeout=REQUEST_TIME_OUT,
                                 verify=False)
        resultList = json.loads(response.text)['page']['dataList']
        metadata_ids = [{
            'METADATA_ID': x['METADATA_ID'],
            'CREAT_DATE': x['CREAT_DATE'],
            'UPDATE_DATE': x['UPDATE_DATE'],
            'THEME_NAME': x['THEME_NAME']
        } for x in resultList]
        return metadata_ids

    def result_list_neimenggu_neimenggu(self, curl):
        response = requests.post(curl['url'],
                                 headers=curl['headers'],
                                 data=curl['data'],
                                 timeout=REQUEST_TIME_OUT,
                                 verify=False)
        resultList = json.loads(response.text)['data']
        ids = [x['id'] for x in resultList]
        return ids

    def result_list_liaoning_liaoning(self, curl):
        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for title in soup.find_all('div', attrs={'class': 'cata-title'}):
            link = title.find('a', attrs={'href': re.compile("/oportal/catalog/*")})
            links.append(link['href'])
        return links

    def result_list_shandong_shandong(self, curl):
        response = requests.get(curl['url'], params=curl['params'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for title in soup.find_all('div', attrs={'class': 'cata-title'}):
            link = title.find('a', attrs={'href': re.compile("/portal/catalog/*")})
            links.append(link['href'])
        return links

    def result_list_jiangsu_jiangsu(self, curl):
        response = requests.post(curl['url'],
                                 data=curl['data'],
                                 headers=curl['headers'],
                                 timeout=REQUEST_TIME_OUT,
                                 verify=False)
        resultList = json.loads(response.text)['custom']['resultList']
        rowGuids = [x['rowGuid'] for x in resultList]
        return rowGuids

    def result_list_shanghai_shanghai(self, curl):
        response = requests.post(curl['url'], headers=curl['headers'], data=curl['data'], timeout=REQUEST_TIME_OUT)
        resultList = json.loads(response.text)['data']['content']
        dataset_ids = [{'datasetId': x['datasetId'], 'datasetName': x['datasetName']} for x in resultList]
        return dataset_ids

    def result_list_zhejiang_zhejiang(self, curl):
        response = requests.post(curl['url'], data=curl['data'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = json.loads(response.text)['data']
        soup = BeautifulSoup(html, "html.parser")
        iids = []
        for title in soup.find_all('div', attrs={'class': 'search_result'}):
            link = title.find('a', attrs={'href': re.compile("../detail/data.do*")})
            parsed_link = urllib.parse.urlparse(link['href'])
            querys = urllib.parse.parse_qs(parsed_link.query)
            querys = {k: v[0] for k, v in querys.items()}
            iids.append(querys)
        return iids

    def result_list_anhui_anhui(self, curl):
        response = requests.post(curl['url'],
                                 data=curl['data'],
                                 headers=curl['headers'],
                                 verify=False,
                                 timeout=REQUEST_TIME_OUT)
        resultList = json.loads(response.text)['data']['rows']
        rids = [x['rid'] for x in resultList]
        return rids

    def result_list_anhui_hefei(self, curl):
        response = requests.get(curl['url'],
                                params=curl['queries'],
                                cookies=curl['cookies'],
                                headers=curl['headers'],
                                timeout=REQUEST_TIME_OUT)
        resultList = json.loads(response.text)['data']['result']
        ids = [x['id'] for x in resultList]
        return ids

    def result_list_anhui_wuhu(self, curl):
        response = requests.post(curl['url'], data=curl['data'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        resultList = json.loads(response.text)['smcDataSetList']
        ids = [x['id'] for x in resultList]
        return ids

    def result_list_anhui_huainan(self, curl):
        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        resultList = json.loads(response.text)['rows']
        data_ids = [x['dataId'] for x in resultList]
        return data_ids

    def result_list_anhui_chuzhou(self, curl):
        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        resultList = json.loads(response.text)['content']
        ids = [x['id'] for x in resultList]
        return ids

    def result_list_anhui_suzhou(self, curl):
        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        links = []

        for dataset in soup.find('div', attrs={'class': 'bottom-content'}).find('ul').find_all('li', recursive=False):
            link = dataset.find('div', attrs={
                'class': 'cata-title'
            }).find('a', attrs={'href': re.compile("/oportal/catalog/*")})
            data_formats = []
            for data_format in dataset.find('div', attrs={'class': 'file-type'}).find_all('li'):
                data_format_text = data_format.get_text()
                if data_format_text == '接口':
                    data_format_text = 'api'
                data_formats.append(data_format_text.lower())
            links.append({'link': link['href'], 'data_formats': str(data_formats)})
        return links

    def result_list_anhui_luan(self, curl):
        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        links = []

        for dataset in soup.find('div', attrs={'class': 'bottom-content'}).find('ul').find_all('li', recursive=False):
            link = dataset.find('div', attrs={
                'class': 'cata-title'
            }).find('a', attrs={'href': re.compile("/oportal/catalog/*")})
            data_formats = []
            for data_format in dataset.find('div', attrs={'class': 'file-type'}).find_all('li'):
                data_format_text = data_format.get_text()
                if data_format_text == '接口':
                    data_format_text = 'api'
                data_formats.append(data_format_text.lower())
            links.append({'link': link['href'], 'data_formats': str(data_formats)})
        return links

    def result_list_anhui_chizhou(self, curl):
        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        metadata_list = []
        for dataset in soup.find('div', attrs={
            'id': 'listContent'
        }).find_all('div', attrs={'class': 'list-content-item'}):
            dataset_metadata = {}
            dataset_metadata["标题"] = dataset.find('div', attrs={'class': 'text ell'}).get_text().strip()
            dataset_metadata["数据格式"] = dataset.find('div',
                                                        attrs={'class': 'file-type-wrap'}).get_text().strip().lower()
            for field in dataset.find_all('div', attrs={'class': 'content-item ell'}):
                field_name = field.get_text().strip().split('：')[0]
                field_text = field.get_text().strip().split('：')[1]
                dataset_metadata[field_name] = field_text

            metadata_list.append(dataset_metadata)
        return metadata_list

    def result_list_jiangxi_jiangxi(self, curl):
        response = requests.post(curl['url'], json=curl['data'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        resultList = json.loads(response.text)['data']
        data_ids = [{'dataId': x['dataId'], 'filesType': x['filesType']} for x in resultList]
        return data_ids

    def result_list_jiangxi_ganzhou(self, curl):
        response = requests.post(curl['url'], json=curl['data'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        ids = []
        for title in soup.find_all('div', attrs={'class': 'com_shiye'}):
            id = title.find('a', attrs={'class': 'shiy_rigA1'}).get('id')
            ids.append(id)
        return ids

    def result_list_fujian_fujian(self, curl):
        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for title in soup.find_all('div', attrs={'class': 'mrline1-title'}):
            link = title.find('a', attrs={'href': re.compile("/oportal/catalog/*")})
            links.append(link['href'])
        return links

    def result_list_fujian_fuzhou(self, curl):
        response = requests.post(curl['url'], json=curl['data'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        resultList = json.loads(json.loads(response.text)['dataList'])['list']
        res_ids = [x['resId'] for x in resultList]
        return res_ids

    def result_list_fujian_xiamen(self, curl):
        response = requests.post(curl['url'], json=curl['data'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        resultList = json.loads(response.text)['data']['list']
        catalog_ids = [x['catalogId'] for x in resultList]
        return catalog_ids

    def result_list_guangdong_guangdong(self, curl):
        response = requests.post(curl['url'], json=curl['data'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        resultList = json.loads(response.text)['data']['page']['list']
        res_ids = [x['resId'] for x in resultList]
        return res_ids

    def result_list_guangxi_guangxi(self, curl):
        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        links = []

        for dataset in soup.find('div', attrs={'class': 'bottom-content'}).find('ul').find_all('li', recursive=False):
            link = dataset.find('div', attrs={
                'class': 'cata-title'
            }).find('a', attrs={'href': re.compile("/portal/catalog/*")})
            data_formats = []
            for data_format in dataset.find('div', attrs={'class': 'file-type'}).find_all('li'):
                data_format_text = data_format.get_text()
                if data_format_text == '接口':
                    data_format_text = 'api'
                data_formats.append(data_format_text.lower())
            links.append({'link': link['href'], 'data_formats': str(data_formats)})
        return links

    def result_list_hainan_hainan(self, curl):
        response = requests.post(curl['url'], data=curl['data'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        resultList = json.loads(response.text)['data']['content']
        res_ids = [x['id'] for x in resultList]
        return res_ids

    def result_list_chongqing_chongqing(self, curl):

        key_map = {
            'resourceName': "标题",
            'resourceDesc': "摘要",
            'organizationName': "资源提供方",
            'updateDate': "更新时间",
            'openAttr': "开放类型",
            'fileTypes': "资源格式",
            'renewCycle': "更新周期"
        }

        openAttr_map = {"CONDITIONAL": "有条件开放", "UNCONDITIONAL": "无条件开放"}
        renewCycle_map = {
            "REAL_TIME": "实时",
            "EVERY_DAY": "每日",
            "EVERY_WEEK": "每周",
            "EVERY_MONTH": "每月",
            "EVERY_QUARTER": "每季度",
            "HALF_YEAR": "每半年",
            "EVERY_YEAR": "每年",
            "IRREGULAR": "不定期",
            "OTHER": "其他"
        }
        metadatas = []
        response = requests.post(curl['url'],
                                 json=curl['data'],
                                 headers=curl['headers'],
                                 timeout=REQUEST_TIME_OUT * 1000)
        print(response)
        result_list_json = json.loads(response.text)['data']['result']['data']
        print(len(result_list_json))
        for detail_json in result_list_json:
            dataset_metadata = {}
            for key, value in key_map.items():
                if key == 'openAttr' and detail_json[key] is not None:
                    detail_json[key] = openAttr_map[detail_json[key]]
                if key == 'renewCycle' and detail_json[key] is not None:
                    detail_json[key] = renewCycle_map[detail_json[key]]
                if key == 'fileTypes':
                    if detail_json['shareType'] == 'FILE':
                        detail_json[key] = '[' + detail_json[key] + ']' if detail_json[key] is not None else '[]'
                    else:
                        detail_json[key] = '[api]'
                if key in ['updateDate'] and detail_json[key] is not None:
                    detail_json[key] = detail_json[key][:10]
                dataset_metadata[value] = detail_json[key]
            print(detail_json['tags'])
            dataset_metadata['行业分类'] = detail_json['tags']['INDUSTRY'] if 'INDUSTRY' in detail_json[
                'tags'] else None
            dataset_metadata['主题分类'] = detail_json['tags']['TOPIC'] if 'TOPIC' in detail_json['tags'] else None
            dataset_metadata['url'] = 'https://data.cq.gov.cn/rop/assets/detail?resId=' + detail_json['id']
            metadatas.append(dataset_metadata)
        return metadatas

    def result_list_ningxia_ningxia(self, curl):
        response = requests.get(curl['url'],
                                params=curl['queries'],
                                cookies=curl['cookies'],
                                headers=curl['headers'],
                                verify=False,
                                timeout=REQUEST_TIME_OUT)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for title in soup.find_all('div', attrs={'class': 'cata-title'}):
            link = title.find('a', attrs={'href': re.compile("/portal/catalog/*")})
            links.append(link['href'])
        return links

    def result_list_shaanxi_shaanxi(self, curl):
        response = requests.get(curl['url'],
                                params=curl['queries'],
                                headers=curl['headers'],
                                verify=False,
                                timeout=REQUEST_TIME_OUT)
        resultList = json.loads(response.text)[0]['result']
        ids = [x['id'] for x in resultList]
        return ids

    def result_list_sichuan_sichuan(self, curl):
        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for title in soup.find_all('div', attrs={'class': 'cata-title'}):
            link = title.find('a', attrs={'href': re.compile("/oportal/catalog/*")})
            links.append(link['href'])
        return links

    def result_list_guizhou_guizhou(self, curl):
        response = requests.post(curl['url'],
                                 json=curl['data'],
                                 headers=curl['headers'],
                                 verify=False,
                                 timeout=REQUEST_TIME_OUT)
        print(response)
        resultList = json.loads(response.text)['data']
        ids = [x['id'] for x in resultList]
        return ids

    def result_list_other(self):
        print("暂无该省")
