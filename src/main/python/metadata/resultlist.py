import hashlib
import json
import re
import time
import urllib
import bs4

import requests
from requests.utils import add_dict_to_cookiejar
from bs4 import BeautifulSoup
from constants import REQUEST_TIME_OUT

import execjs


def getCookie(data):
    """
    通过加密对比得到正确cookie参数
    :param data: 参数
    :return: 返回正确cookie参数
    """
    chars = len(data['chars'])
    for i in range(chars):
        for j in range(chars):
            clearance = data['bts'][0] + data['chars'][i] + data['chars'][j] + data['bts'][1]
            encrypt = None
            if data['ha'] == 'md5':
                encrypt = hashlib.md5()
            elif data['ha'] == 'sha1':
                encrypt = hashlib.sha1()
            elif data['ha'] == 'sha256':
                encrypt = hashlib.sha256()
            encrypt.update(clearance.encode())
            result = encrypt.hexdigest()
            if result == data['ct']:
                return clearance


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
        # print(resultList)
        links = [x['url'] for x in resultList]
        return links

    def result_list_tianjin_tianjin(self, curl):
        response = requests.get(curl['dataset url'], timeout=REQUEST_TIME_OUT)
        resultList = json.loads(response.text)['dataList']
        # links = [x['href'] for x in resultList]
        link_format_data = [{'link': x['href'], 'format': x['documentType']} for x in resultList]
        response = requests.get(curl['interface url'], timeout=REQUEST_TIME_OUT)
        resultList = json.loads(response.text)['dataList']
        link_format_data.extend([{'link': x['href'], 'format': 'api'} for x in resultList])
        return link_format_data

    def result_list_hebei_hebei(self, curl):
        response = requests.post(curl['url'],
                                 cookies=curl['cookies'],
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

    def result_list_shanxi_datong(self, curl):
        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for li in soup.find('div', attrs={'class': 'm-cata-list'}).find('ul').find_all('li', recursive=False):
            url = li.find('div', attrs={
                'class': 'item-content'
            }).find('div', attrs={
                'class': 'item-title'
            }).find('a').get('href')
            links.append(url)
            # for info in li.find('div', attrs={'class': 'item-info'}).find_all('div'):
            #     text = info.get_text().strip()  # e.g. 开放状态：无条件开放
        return links

    def result_list_shanxi_changzhi(self, curl):
        response = requests.post(curl['url'],
                                 params=curl['queries'],
                                 cookies=curl['cookies'],
                                 headers=curl['headers'],
                                 data=curl['data'],
                                 timeout=REQUEST_TIME_OUT,
                                 verify=False)
        resultList = json.loads(response.text)['data']
        ids = [x['cata_id'] for x in resultList]
        return ids

    def result_list_shanxi_jincheng(self, curl):
        response = requests.post(curl['url'],
                                 cookies=curl['cookies'],
                                 headers=curl['headers'],
                                 data=curl['data'],
                                 timeout=REQUEST_TIME_OUT,
                                 verify=False)
        resultList = json.loads(json.loads(response.text)['jsonStr'])['obj']['pagingList']
        ids = [x['id'] for x in resultList]
        return ids

    def result_list_shanxi_yuncheng(self, curl):
        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        # link_format_data = []
        links = []
        for li in soup.find('div', attrs={'class': 'etab1'}).find('ul').find_all('li'):
            link = li.find('h2', attrs={'class': 'tit'}).find('a').get('href')
            # format = [x.get('class')[0] for x in li.find_all('b')]
            # link_format_data.append({'link': link, 'format': format})
            links.append(link)
        return links

    def result_list_neimenggu_neimenggu(self, curl):
        response = requests.post(curl['url'],
                                 headers=curl['headers'],
                                 data=curl['data'],
                                 timeout=REQUEST_TIME_OUT,
                                 verify=False)
        resultList = json.loads(response.text)['data']
        ids = [x['id'] for x in resultList]
        return ids

    def result_list_neimenggu_xinganmeng(self, curl):
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

    def result_list_liaoning_shenyang(self, curl):
        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for title in soup.find_all('div', attrs={'class': 'cata-title'}):
            link = title.find('a', attrs={'href': re.compile("/oportal/catalog/*")})
            links.append(link['href'])
        return links

    def result_list_heilongjiang_harbin(self, curl):
        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for title in soup.find_all('div', attrs={'class': 'cata-title'}):
            link = title.find('a', attrs={'href': re.compile("/oportal/catalog/*")})
            links.append(link['href'])
        return links

    def result_list_shanghai_shanghai(self, curl):
        response = requests.post(curl['url'], headers=curl['headers'], data=curl['data'], timeout=REQUEST_TIME_OUT)
        resultList = json.loads(response.text)['data']['content']
        dataset_ids = [{'datasetId': x['datasetId'], 'datasetName': x['datasetName']} for x in resultList]
        return dataset_ids

    def result_list_jiangsu_jiangsu(self, curl):
        response = requests.post(curl['url'],
                                 data=curl['data'],
                                 headers=curl['headers'],
                                 timeout=REQUEST_TIME_OUT,
                                 verify=False)
        resultList = json.loads(response.text)['custom']['resultList']
        rowGuid_tag_list = [(x['rowGuid'], [n['name'].replace("其他", 'file').lower() for n in x['tag']])
                            for x in resultList]
        return rowGuid_tag_list

    def result_list_jiangsu_wuxi(self, curl):
        response = requests.post(curl['url'],
                                 headers=curl['headers'],
                                 params=curl['params'],
                                 data=curl['data'],
                                 timeout=REQUEST_TIME_OUT)
        resultList = json.loads(response.text)['data']
        cata_ids = [x['cata_id'] for x in resultList]
        return cata_ids

    def result_list_jiangsu_xuzhou(self, curl):
        response = requests.post(curl['url'],
                                 headers=curl['headers'],
                                 json=curl['json_data'],
                                 timeout=REQUEST_TIME_OUT,
                                 verify=False)
        resultList = json.loads(response.text)['data']['rows']
        mlbhs = [x['mlbh'] for x in resultList]
        return mlbhs

    def result_list_jiangsu_suzhou(self, curl):
        response = requests.post(curl['url'],
                                 params=curl['params'],
                                 headers=curl['headers'],
                                 json=curl['json_data'],
                                 timeout=REQUEST_TIME_OUT)
        resultList = json.loads(response.text)['data']['records']
        ids = [x['id'] for x in resultList]
        return ids

    def result_list_jiangsu_nantong(self, curl):
        response = requests.get(curl['url'], params=curl['params'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        resultList = json.loads(response.text)['data']['content']
        ids = [x['id'] for x in resultList]
        return ids

    def result_list_jiangsu_lianyungang(self, curl):
        response = requests.get(curl['url'],
                                params=curl['params'],
                                headers=curl['headers'],
                                verify=False,
                                timeout=REQUEST_TIME_OUT)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        result_list = soup.find('div', attrs={'class': 'mainz mt30 jQtabcontent'}).find_all('li')
        dmids = []
        for li in result_list:
            title = li.find('h1')
            # s = title.get_text()
            dmid = title.attrs['onclick'].lstrip("view('").rstrip("')")
            dmids.append(dmid)
        return dmids

    def result_list_jiangsu_huaian(self, curl):
        response = requests.get(curl['url'], params=curl['params'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        result_list = json.loads(response.text)['data']['data']
        ids = [x['id'] for x in result_list]
        return ids

    def result_list_jiangsu_yancheng(self, curl):
        response = requests.get(curl['url'], params=curl['params'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        result_list = json.loads(response.text)['resultData']['list']
        catalogPks = [x['catalogPk'] for x in result_list]
        return catalogPks

    def result_list_jiangsu_zhenjiang(self, curl):
        response = requests.get(curl['url'], params=curl['params'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        result_list = json.loads(response.text)['data']['content']
        ids = [x['id'] for x in result_list]
        return ids

    def result_list_jiangsu_taizhou(self, curl):
        response = requests.get(curl['url'],
                                params=curl['params'],
                                headers=curl['headers'],
                                verify=False,
                                timeout=REQUEST_TIME_OUT)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        result_list = soup.find('div', attrs={
            'class': 'right-content-catalog'
        }).find('div', attrs={
            'class': 'bottom-content'
        }).find('ul').find_all('li', recursive=False)
        ids = []
        for li in result_list:
            id = li.find('div', attrs={
                'class': 'cata-title'
            }).find('input', attrs={
                'name': 'catalogidinput'
            }).attrs['value']
            ids.append(id)
        return ids

    def result_list_jiangsu_suqian(self, curl):
        response = requests.get(curl['url'], params=curl['params'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        result_list = soup.find('div', attrs={
            'class': 'right-content-catalog'
        }).find('div', attrs={
            'class': 'bottom-content'
        }).find('ul').find_all('li', recursive=False)
        id_infos = []
        for li in result_list:
            id = li.find('div', attrs={
                'class': 'cata-title'
            }).find('input', attrs={
                'name': 'catalogidinput'
            }).attrs['value']
            update_time = li.find('div', attrs={
                'class': 'cata-information'
            }).find('span', text='更新时间：').find_next('span').get_text().strip()
            id_infos.append((id, update_time))
        return id_infos

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

    def result_list_zhejiang_hangzhou(self, curl):
        response = requests.post(curl['url'], headers=curl['headers'], data=curl['data'], timeout=REQUEST_TIME_OUT)
        result_list = json.loads(response.text)['rows']
        id_formats = [(x['id'], x['source_type'].lower()) for x in result_list]
        return id_formats

    def result_list_zhejiang_ningbo(self, curl):
        response = requests.post(curl['url'],
                                 headers=curl['headers'],
                                 json=curl['json_data'],
                                 verify=False,
                                 timeout=REQUEST_TIME_OUT)
        result_list = json.loads(response.text)['list']['rows']
        uuids = [x['uuid'] for x in result_list]
        return uuids

    def result_list_zhejiang_wenzhou(self, curl):
        response = requests.post(curl['url'],
                                 headers=curl['headers'],
                                 data=curl['data'],
                                 verify=False,
                                 timeout=REQUEST_TIME_OUT)
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

    def result_list_zhejiang_jiaxing(self, curl):
        response = requests.post(curl['url'], headers=curl['headers'], data=curl['data'], timeout=REQUEST_TIME_OUT)
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

    def result_list_zhejiang_shaoxing(self, curl):
        response = requests.post(curl['url'], headers=curl['headers'], json=curl['json_data'], timeout=REQUEST_TIME_OUT)
        result_list = json.loads(response.text)['data']['rows']
        iids = [x['iid'] for x in result_list]
        return iids

    def result_list_zhejiang_jinhua(self, curl):
        response = requests.post(curl['url'],
                                 headers=curl['headers'],
                                 data=curl['data'],
                                 verify=False,
                                 timeout=REQUEST_TIME_OUT)
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

    def result_list_zhejiang_quzhou(self, curl):
        response = requests.post(curl['url'], headers=curl['headers'], data=curl['data'], timeout=REQUEST_TIME_OUT)
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

    def result_list_zhejiang_zhoushan(self, curl):
        response = requests.post(curl['url'],
                                 headers=curl['headers'],
                                 json=curl['json_data'],
                                 verify=False,
                                 timeout=REQUEST_TIME_OUT)
        result_list = json.loads(response.text)['data']['records']
        ids = [x['id'] for x in result_list]
        return ids

    def result_list_zhejiang_taizhou(self, curl):
        response = requests.post(curl['url'], headers=curl['headers'], json=curl['json_data'], timeout=REQUEST_TIME_OUT)
        result_list = json.loads(response.text)['data']['rows']
        iids = [x['iid'] for x in result_list]
        return iids

    def result_list_zhejiang_lishui(self, curl):
        response = requests.post(curl['url'],
                                 headers=curl['headers'],
                                 data=curl['data'],
                                 verify=False,
                                 timeout=REQUEST_TIME_OUT)
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
        # 使用session保持会话
        session = requests.session()
        res1 = session.get(curl['url'], headers=curl['headers'], params=curl['queries'])
        jsl_clearance_s = re.findall(r'cookie=(.*?);location', res1.text)[0]
        # 执行js代码
        jsl_clearance_s = str(execjs.eval(jsl_clearance_s)).split('=')[1].split(';')[0]
        # add_dict_to_cookiejar方法添加cookie
        add_dict_to_cookiejar(session.cookies, {'__jsl_clearance_s': jsl_clearance_s})
        res2 = session.get(curl['url'], headers=curl['headers'], params=curl['queries'])
        # 提取go方法中的参数
        data = json.loads(re.findall(r';go\((.*?)\)', res2.text)[0])
        jsl_clearance_s = getCookie(data)
        # 修改cookie
        add_dict_to_cookiejar(session.cookies, {'__jsl_clearance_s': jsl_clearance_s})
        response = session.get(curl['url'], headers=curl['headers'], params=curl['queries'])

        if response.status_code != requests.codes.ok:
            print("error " + str(response.status_code) + ": " + curl['url'])
            print(response.text)
            return dict()
        # print(response)
        resultList = json.loads(response.text)['data']['result']

        ids = [(str(x['id']), x['zyId']) for x in resultList]
        return ids

    def result_list_anhui_wuhu(self, curl):
        response = requests.post(curl['url'], data=curl['data'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)

        if response.status_code != requests.codes.ok:
            print("error " + str(response.status_code) + ": " + curl['url'])
            return dict()
        resultList = json.loads(response.text.replace('\\"', '"')[1:-1])['smcDataSetList']
        # 目前所有数据集中只出现了每日和每年
        frequency_mapping = {'1': "实时", '2': "每日", '3': "每周", '4': "每月", '5': "每半年", '6': "每年"}
        dataset_metadata = []
        for result in resultList:
            dataset_id = result['id']
            metadata_mapping = {
                "标题":
                result['datasetName'],
                "机构分类":
                result['isValid'],
                "url":
                "https://data.wuhu.cn/datagov-ops/data/toDetailPage?id=" + dataset_id,
                "领域名称":
                result['dataType'],
                "数据集创建时间":
                result['createDate'],
                "数据集更新时间":
                result['updateDate'].split(' ')[0],
                "开放类型":
                "无条件开放" if result['openType'] == '1' else "有条件开放",
                "更新频率":
                frequency_mapping[result['dataUpdateFrequency']],
                "数据简介":
                result['summary'],
                "资源格式": ['api'] if result['dataResourceType'] == '2' else
                [file['fileType'].split('.')[-1] for file in result['fileList']]
            }
            dataset_metadata.append(metadata_mapping)
        return dataset_metadata

    def result_list_anhui_bengbu(self, curl):
        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content.decode('utf-8')
        soup = BeautifulSoup(html, "html.parser")
        # soup = BeautifulSoup(html, "lxml")
        links = []

        for dataset in soup.find('div', attrs={'class': 'sj_list'}).find('ul').find_all('li', recursive=False):
            link = dataset.find('div', attrs={'class': 'sjinfo'}).find('a', attrs={'href': re.compile("site/tpl/.*")})
            links.append(link['href'])
        return links

    def result_list_anhui_huainan(self, curl):
        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        resultList = json.loads(response.text)['rows']
        data_ids = [x['dataId'] for x in resultList]
        return data_ids

    def result_list_anhui_huaibei(self, curl):
        response = requests.post(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)

        if response.status_code != requests.codes.ok:
            print("error " + str(response.status_code) + ": " + curl['url'])
            return dict()
        # print(response)
        resultList = json.loads(response.text)['result']['data']
        ids = [x['id'] for x in resultList]
        return ids

    def result_list_anhui_huangshan(self, curl):
        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content.decode('utf-8')
        soup = BeautifulSoup(html, "html.parser")
        # soup = BeautifulSoup(html, "lxml")
        links = []

        for dataset in soup.find('ul', attrs={'class': 'clearfix'}).find_all('li', recursive=False):
            div = dataset.find('div', attrs={
                'class': 'sjcon clearfix'
            }).find('div', attrs={'class': 'dataresources-con'})
            link = div.find('a', attrs={'href': re.compile("/site/tpl/.*")})
            depart = div.find('p', attrs={
                'class': 'xx clearfix'
            }).find('span', attrs={
                'class': 'n2'
            }).get_text().split("：")[-1].strip()
            cata = div.find('p', attrs={
                'class': 'xx clearfix'
            }).find('span', attrs={
                'class': 'n3'
            }).get_text().split("：")[-1].strip()
            format_list = []
            for data_format in div.find('p', attrs={
                    'class': 'zyzy clearfix'
            }).find('span', attrs={
                    'class': 'link'
            }).find_all('a', attrs={'class': 'j-login'}):
                format_list.append(data_format.find('em').get_text().lower().strip())
            if len(format_list) == 0:
                format_list = ['file']
            links.append((link['href'], depart, cata, format_list))
        return links

    def result_list_anhui_chuzhou(self, curl):
        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)

        if response.status_code != requests.codes.ok:
            print("error " + str(response.status_code) + ": " + curl['url'])
            return dict()
        resultList = json.loads(response.text)['content']
        dataset_metadata = []
        for result in resultList:
            metadata_mapping = {
                "标题": result['name'],
                "提供单位": result['companys']['title'],
                "开放主题": result['fields']['title'],
                "发布时间": result['createtime'].split(' ')[0],
                "更新时间": result['updatetime'].split(' ')[0],
                "开放类型": "无条件开放" if result['sharetype'] == '2' else "有条件开放",
                "描述": result['description'],
                "开放领域": result['themes']['title'],
                "关键词": result['keyword']
            }
            dataset_metadata.append(metadata_mapping)
        return dataset_metadata

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
            dataset_metadata["数据格式"] = dataset.find('div', attrs={'class': 'file-type-wrap'}).get_text().strip().lower()
            for field in dataset.find_all('div', attrs={'class': 'content-item ell'}):
                field_name = field.get_text().strip().split('：')[0]
                field_text = field.get_text().strip().split('：')[1]
                dataset_metadata[field_name] = field_text

            metadata_list.append(dataset_metadata)
        return metadata_list

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

    def result_list_shandong_common(self, curl, prefix):
        response = requests.get(curl['url'], params=curl['params'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for title in soup.find_all('div', attrs={'class': 'cata-title'}):
            link = title.find('a', attrs={'href': re.compile(f"/{prefix}/catalog/*")})
            file_type_elements = title.parent.find('div', attrs={'class': 'file-type'}).findChildren('li')
            data_formats = list(map(lambda x: x['class'][0].lower(), file_type_elements))  # class 标签内，“接口”就叫“api”
            if len(data_formats) == 0:
                data_formats.append("file")
            links.append({'link': link['href'], 'data_formats': data_formats})
        return links

    def result_list_shandong_shandong(self, curl):
        return self.result_list_shandong_common(curl, "portal")

    def result_list_shandong_jinan(self, curl):
        return self.result_list_shandong_common(curl, "jinan")

    def result_list_shandong_qingdao(self, curl):
        return self.result_list_shandong_common(curl, "qingdao")

    def result_list_shandong_zibo(self, curl):
        return self.result_list_shandong_common(curl, "zibo")

    def result_list_shandong_zaozhuang(self, curl):
        return self.result_list_shandong_common(curl, "zaozhuang")

    def result_list_shandong_dongying(self, curl):
        return self.result_list_shandong_common(curl, "dongying")

    def result_list_shandong_yantai(self, curl):
        return self.result_list_shandong_common(curl, "yantai")

    def result_list_shandong_weifang(self, curl):
        return self.result_list_shandong_common(curl, "weifang")

    def result_list_shandong_jining(self, curl):
        return self.result_list_shandong_common(curl, "jining")

    def result_list_shandong_taian(self, curl):
        return self.result_list_shandong_common(curl, "taian")

    def result_list_shandong_weihai(self, curl):
        return self.result_list_shandong_common(curl, "weihai")

    def result_list_shandong_rizhao(self, curl):
        return self.result_list_shandong_common(curl, "rizhao")

    def result_list_shandong_linyi(self, curl):
        return self.result_list_shandong_common(curl, "linyi")

    def result_list_shandong_dezhou(self, curl):
        return self.result_list_shandong_common(curl, "dezhou")

    def result_list_shandong_liaocheng(self, curl):
        return self.result_list_shandong_common(curl, "liaocheng")

    def result_list_shandong_binzhou(self, curl):
        return self.result_list_shandong_common(curl, "binzhou")

    def result_list_shandong_heze(self, curl):
        return self.result_list_shandong_common(curl, "heze")

    def result_list_hubei_wuhan(self, curl):
        response = requests.post(curl['url'],
                                 json=curl['data'],
                                 headers=curl['headers'],
                                 verify=False,
                                 timeout=REQUEST_TIME_OUT)
        resultList = json.loads(response.text)['data']
        cataIds = list(map(lambda x: x['cataId'], resultList['records']))
        return cataIds

    def result_list_hubei_huangshi(self, curl):
        response = requests.get(curl['url'], headers=curl['headers'], verify=False, timeout=REQUEST_TIME_OUT)
        data = json.loads(response.text)['data']['list']
        ids = list(map(lambda x: x['infoid'], data))
        return ids

    def result_list_hubei_yichang(self, curl):
        if curl['crawl_type'] == 'dataset':
            response = requests.post(curl['url'],
                                     json=curl['data'],
                                     headers=curl['headers'],
                                     verify=False,
                                     timeout=REQUEST_TIME_OUT)
            resultList = json.loads(response.text)['data']
            cataIds = list(map(lambda x: x['iid'], resultList['rows']))
            return cataIds
        else:
            response = requests.post(curl['url'], data=curl['data'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
            resultList = json.loads(response.text)['data']
            cataIds = list(map(lambda x: x['iid'], resultList['list']))
            return cataIds

    def result_list_hubei_ezhou(self, curl):

        response = requests.get(curl['url'], headers=curl['headers'], verify=False, timeout=REQUEST_TIME_OUT)
        soup = bs4.BeautifulSoup(response.text)
        ul = soup.find('ul', class_='sjj_right_list')
        links = []
        if not ul:
            return []
        for li in ul.find_all('li', class_='fbc'):
            h3 = li.find('h3')
            if h3 is not None:
                a = h3.find('a')
                # links.append(a['href'])
                links.append('/'.join(curl['url'].split('/')[:-1]) + (a['href'].lstrip('.')))
        return links

    def result_list_hubei_jingzhou(self, curl):
        response = requests.get(curl['url'],
                                params=curl['queries'],
                                headers=curl['headers'],
                                verify=False,
                                timeout=REQUEST_TIME_OUT)
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('div', class_='cata-title')
        ids = []
        for div in divs:
            if div:
                a = div.find('a')
                ids.append(a['href'].split('/')[-1])
        return ids

    def result_list_hubei_suizhou(self, curl):
        response = requests.post(curl['url'],
                                 data=curl['data'],
                                 headers=curl['headers'],
                                 verify=False,
                                 timeout=REQUEST_TIME_OUT)
        data = json.loads(response.text)
        ids = list(map(lambda x: x['id'], data['list']))
        return ids

    def result_list_hunan_yueyang(self, curl):
        response = requests.get(curl['url'],
                                params=curl['queries'],
                                headers=curl['headers'],
                                verify=False,
                                timeout=REQUEST_TIME_OUT)

        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('div', class_='szkf-box-list')
        ids = []
        for div in divs:
            a = div.find_next('div', class_='name').find_next('a')
            ids.append(a['href'].split('=')[1])
        return ids

    def result_list_hunan_changde(self, curl):
        response = requests.get(curl['url'],
                                params=curl['queries'],
                                headers=curl['headers'],
                                verify=False,
                                timeout=REQUEST_TIME_OUT)
        data = json.loads(response.text)
        cata_ids = list(map(lambda x: x['CATA_ID'], data['list']))
        return cata_ids

    def result_list_hunan_chenzhou(self, curl):
        response = requests.get(curl['url'],
                                params=curl['queries'],
                                headers=curl['headers'],
                                verify=False,
                                timeout=REQUEST_TIME_OUT)

        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table', class_='table-data')
        ids = []
        for table in tables:
            tr = table.find_all('tr')[-1]
            a = tr.find_next('a')
            ids.append(a['href'].split('=')[1])
        return ids

    def result_list_hunan_yiyang(self, curl):
        response = requests.get(curl['url'],
                                params=curl['queries'],
                                headers=curl['headers'],
                                verify=False,
                                timeout=REQUEST_TIME_OUT)

        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table', class_='table-data')
        ids = []
        for table in tables:
            tr = table.find_all('tr')[-1]
            a = tr.find_next('a')
            ids.append(a['href'].split('=')[1])
        return ids

    def result_list_guangdong_guangdong(self, curl):
        response = requests.post(curl['url'], json=curl['data'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        data = json.loads(response.text)['data']
        ids = list(map(lambda x: x['resId'], data['page']['list']))
        return ids

    def result_list_guangdong_guangzhou(self, curl):
        response = requests.post(curl['url'], json=curl['data'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        data = json.loads(response.text)['body']
        ids = list(map(lambda x: x['sid'], data))
        return ids

    def result_list_guangdong_shenzhen(self, curl):
        response = requests.post(curl['url'], data=curl['data'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        data = json.loads(response.text)
        if curl['crawl_type'] == 'dataset':
            data = json.loads(data['dataList'])['list']
        else:
            data = json.loads(data['apiList'])['list']
        ids = list(map(lambda x: x['resId'], data))
        return ids

    def result_list_guangdong_zhongshan(self, curl):
        response = requests.post(curl['url'], data=curl['data'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        dl = soup.find('dl')
        ids = []
        for dd in dl.find_all('dd'):
            href = dd.find('h2').find('a')['href']
            ids.append(href.split('\'')[1])
        return ids

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

    def result_list_guangxi_nanning(self, curl):

        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        links = []

        for dataset in soup.find('div', attrs={'class': 'bottom-content'}).find('ul').find_all('li', recursive=False):
            link = dataset.find('div', attrs={
                'class': 'cata-title'
            }).find('a', attrs={'href': re.compile("/catalog/*")})
            data_formats = []
            for data_format in dataset.find('div', attrs={'class': 'file-type'}).find_all('li'):
                data_format_text = data_format.get_text()
                if data_format_text == '接口':
                    data_format_text = 'api'
                data_formats.append(data_format_text.lower())
            links.append({'link': link['href'], 'data_formats': str(data_formats)})
        return links

    def result_list_guangxi_liuzhou(self, curl):

        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        links = []

        for dataset in soup.find('div', attrs={'class': 'bottom-content'}).find('ul').find_all('li', recursive=False):
            link = dataset.find('div', attrs={
                'class': 'cata-title'
            }).find('a', attrs={'href': re.compile("/catalog/*")})
            data_formats = []
            for data_format in dataset.find('div', attrs={'class': 'file-type'}).find_all('li'):
                data_format_text = data_format.get_text()
                if data_format_text == '接口':
                    data_format_text = 'api'
                data_formats.append(data_format_text.lower())
            links.append({'link': link['href'], 'data_formats': str(data_formats)})
        return links

    def result_list_guangxi_guilin(self, curl):

        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        links = []

        for dataset in soup.find('div', attrs={'class': 'bottom-content'}).find('ul').find_all('li', recursive=False):
            link = dataset.find('div', attrs={
                'class': 'cata-title'
            }).find('a', attrs={'href': re.compile("/catalog/*")})
            data_formats = []
            for data_format in dataset.find('div', attrs={'class': 'file-type'}).find_all('li'):
                data_format_text = data_format.get_text()
                if data_format_text == '接口':
                    data_format_text = 'api'
                data_formats.append(data_format_text.lower())
            links.append({'link': link['href'], 'data_formats': str(data_formats)})
        return links

    def result_list_guangxi_wuzhou(self, curl):

        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        links = []

        for dataset in soup.find('div', attrs={'class': 'bottom-content'}).find('ul').find_all('li', recursive=False):
            link = dataset.find('div', attrs={
                'class': 'cata-title'
            }).find('a', attrs={'href': re.compile("/catalog/*")})
            data_formats = []
            for data_format in dataset.find('div', attrs={'class': 'file-type'}).find_all('li'):
                data_format_text = data_format.get_text()
                if data_format_text == '接口':
                    data_format_text = 'api'
                data_formats.append(data_format_text.lower())
            links.append({'link': link['href'], 'data_formats': str(data_formats)})
        return links

    def result_list_guangxi_beihai(self, curl):

        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        links = []

        for dataset in soup.find('div', attrs={'class': 'bottom-content'}).find('ul').find_all('li', recursive=False):
            link = dataset.find('div', attrs={
                'class': 'cata-title'
            }).find('a', attrs={'href': re.compile("/catalog/*")})
            data_formats = []
            for data_format in dataset.find('div', attrs={'class': 'file-type'}).find_all('li'):
                data_format_text = data_format.get_text()
                if data_format_text == '接口':
                    data_format_text = 'api'
                data_formats.append(data_format_text.lower())
            links.append({'link': link['href'], 'data_formats': str(data_formats)})
        return links

    def result_list_guangxi_fangchenggang(self, curl):

        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        links = []

        for dataset in soup.find('div', attrs={'class': 'bottom-content'}).find('ul').find_all('li', recursive=False):
            link = dataset.find('div', attrs={
                'class': 'cata-title'
            }).find('a', attrs={'href': re.compile("/catalog/*")})
            data_formats = []
            for data_format in dataset.find('div', attrs={'class': 'file-type'}).find_all('li'):
                data_format_text = data_format.get_text()
                if data_format_text == '接口':
                    data_format_text = 'api'
                data_formats.append(data_format_text.lower())
            links.append({'link': link['href'], 'data_formats': str(data_formats)})
        return links

    def result_list_guangxi_qinzhou(self, curl):

        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        links = []

        for dataset in soup.find('div', attrs={'class': 'bottom-content'}).find('ul').find_all('li', recursive=False):
            link = dataset.find('div', attrs={
                'class': 'cata-title'
            }).find('a', attrs={'href': re.compile("/catalog/*")})
            data_formats = []
            for data_format in dataset.find('div', attrs={'class': 'file-type'}).find_all('li'):
                data_format_text = data_format.get_text()
                if data_format_text == '接口':
                    data_format_text = 'api'
                data_formats.append(data_format_text.lower())
            links.append({'link': link['href'], 'data_formats': str(data_formats)})
        return links

    def result_list_guangxi_guigang(self, curl):

        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        links = []

        for dataset in soup.find('div', attrs={'class': 'bottom-content'}).find('ul').find_all('li', recursive=False):
            link = dataset.find('div', attrs={
                'class': 'cata-title'
            }).find('a', attrs={'href': re.compile("/catalog/*")})
            data_formats = []
            for data_format in dataset.find('div', attrs={'class': 'file-type'}).find_all('li'):
                data_format_text = data_format.get_text()
                if data_format_text == '接口':
                    data_format_text = 'api'
                data_formats.append(data_format_text.lower())
            links.append({'link': link['href'], 'data_formats': str(data_formats)})
        return links

    def result_list_guangxi_yulin(self, curl):

        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        links = []

        for dataset in soup.find('div', attrs={'class': 'bottom-content'}).find('ul').find_all('li', recursive=False):
            link = dataset.find('div', attrs={
                'class': 'cata-title'
            }).find('a', attrs={'href': re.compile("/catalog/*")})
            data_formats = []
            for data_format in dataset.find('div', attrs={'class': 'file-type'}).find_all('li'):
                data_format_text = data_format.get_text()
                if data_format_text == '接口':
                    data_format_text = 'api'
                data_formats.append(data_format_text.lower())
            links.append({'link': link['href'], 'data_formats': str(data_formats)})
        return links

    def result_list_guangxi_baise(self, curl):

        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        links = []

        for dataset in soup.find('div', attrs={'class': 'bottom-content'}).find('ul').find_all('li', recursive=False):
            link = dataset.find('div', attrs={
                'class': 'cata-title'
            }).find('a', attrs={'href': re.compile("/catalog/*")})
            data_formats = []
            for data_format in dataset.find('div', attrs={'class': 'file-type'}).find_all('li'):
                data_format_text = data_format.get_text()
                if data_format_text == '接口':
                    data_format_text = 'api'
                data_formats.append(data_format_text.lower())
            links.append({'link': link['href'], 'data_formats': str(data_formats)})
        return links

    def result_list_guangxi_hezhou(self, curl):

        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        links = []

        for dataset in soup.find('div', attrs={'class': 'bottom-content'}).find('ul').find_all('li', recursive=False):
            link = dataset.find('div', attrs={
                'class': 'cata-title'
            }).find('a', attrs={'href': re.compile("/catalog/*")})
            data_formats = []
            for data_format in dataset.find('div', attrs={'class': 'file-type'}).find_all('li'):
                data_format_text = data_format.get_text()
                if data_format_text == '接口':
                    data_format_text = 'api'
                data_formats.append(data_format_text.lower())
            links.append({'link': link['href'], 'data_formats': str(data_formats)})
        return links

    def result_list_guangxi_hechi(self, curl):

        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        links = []

        for dataset in soup.find('div', attrs={'class': 'bottom-content'}).find('ul').find_all('li', recursive=False):
            link = dataset.find('div', attrs={
                'class': 'cata-title'
            }).find('a', attrs={'href': re.compile("/catalog/*")})
            data_formats = []
            for data_format in dataset.find('div', attrs={'class': 'file-type'}).find_all('li'):
                data_format_text = data_format.get_text()
                if data_format_text == '接口':
                    data_format_text = 'api'
                data_formats.append(data_format_text.lower())
            links.append({'link': link['href'], 'data_formats': str(data_formats)})
        return links

    def result_list_guangxi_laibin(self, curl):

        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        links = []

        for dataset in soup.find('div', attrs={'class': 'bottom-content'}).find('ul').find_all('li', recursive=False):
            link = dataset.find('div', attrs={
                'class': 'cata-title'
            }).find('a', attrs={'href': re.compile("/catalog/*")})
            data_formats = []
            for data_format in dataset.find('div', attrs={'class': 'file-type'}).find_all('li'):
                data_format_text = data_format.get_text()
                if data_format_text == '接口':
                    data_format_text = 'api'
                data_formats.append(data_format_text.lower())
            links.append({'link': link['href'], 'data_formats': str(data_formats)})
        return links

    def result_list_guangxi_chongzuo(self, curl):

        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        links = []

        for dataset in soup.find('div', attrs={'class': 'bottom-content'}).find('ul').find_all('li', recursive=False):
            link = dataset.find('div', attrs={
                'class': 'cata-title'
            }).find('a', attrs={'href': re.compile("/catalog/*")})
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
            dataset_metadata['行业分类'] = detail_json['tags']['INDUSTRY'] if 'INDUSTRY' in detail_json['tags'] else None
            dataset_metadata['主题分类'] = detail_json['tags']['TOPIC'] if 'TOPIC' in detail_json['tags'] else None
            dataset_metadata['url'] = 'https://data.cq.gov.cn/rop/assets/detail?resId=' + detail_json['id']
            metadatas.append(dataset_metadata)
        return metadatas

    def result_list_sichuan_sichuan(self, curl):
        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content.decode('utf-8')
        soup = BeautifulSoup(html, "html.parser")
        # soup = BeautifulSoup(html, "lxml")
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

    def result_list_sichuan_chengdu(self, curl):
        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content.decode('utf-8')
        soup = BeautifulSoup(html, "html.parser")
        # soup = BeautifulSoup(html, "lxml")
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

    def result_list_sichuan_panzhihua(self, curl):
        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)
        html = response.content.decode('utf-8')
        soup = BeautifulSoup(html, "html.parser")
        # soup = BeautifulSoup(html, "lxml")
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

    def result_list_sichuan_zigong(self, curl):
        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)

        # print(response)
        resultList = json.loads(response.text)['data']['rows']
        ids = [x['id'] for x in resultList]
        return ids

    def result_list_sichuan_luzhou(self, curl):
        response = requests.post(curl['url'], json=curl['data'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)

        # print(response)
        resultList = json.loads(response.text)['result']['rows']
        ids = [(x['id'], x['openType'], x['publishTime'], x['updateTime']) for x in resultList]
        return ids

    def result_list_sichuan_deyang(self, curl):
        response = requests.post(curl['url'], json=curl['data'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)

        # print(response)
        resultList = json.loads(response.text)['data']['rows']
        ids = [x['mlbh'] for x in resultList]
        return ids

    def result_list_sichuan_mianyang(self, curl):
        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)

        # print(response)
        resultList = json.loads(response.text)['elementthing']['listPage']['list']
        ids = [x['id'] for x in resultList]
        return ids

    def result_list_sichuan_guangyuan(self, curl):
        response = requests.post(curl['url'], json=curl['data'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)

        if response.status_code != requests.codes.ok:
            print("error " + str(response.status_code) + ": " + curl['url'])
            return dict()
        # print(response)
        resultList = json.loads(response.text)['data']['rows']
        ids = [x['ID'] for x in resultList]
        return ids

    def result_list_sichuan_suining(self, curl):
        response = requests.post(curl['url'], json=curl['data'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)

        if response.status_code != requests.codes.ok:
            print("error " + str(response.status_code) + ": " + curl['url'])
            return dict()
        # print(response)
        resultList = json.loads(response.text)['data']['rows']
        ids = [(x['mlbh'], x['wjlx']) for x in resultList]
        return ids

    def result_list_sichuan_neijiang(self, curl):
        response = requests.post(curl['url'],
                                 params=curl['queries'],
                                 json=curl['data'],
                                 headers=curl['headers'],
                                 timeout=REQUEST_TIME_OUT)

        if response.status_code != requests.codes.ok:
            print("error " + str(response.status_code) + ": " + curl['url'])
            return dict()
        # print(response)
        resultList = json.loads(response.text)['data']['content']
        ids = [str(x['id']) for x in resultList]
        return ids

    def result_list_sichuan_leshan(self, curl):
        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)

        if response.status_code != requests.codes.ok:
            print("error " + str(response.status_code) + ": " + curl['url'])
            return dict()
        # print(response)
        resultList = json.loads(response.text)['data']['rows']
        ids = [str(x['resourceId']) for x in resultList]
        return ids

    def result_list_sichuan_nanchong(self, curl):
        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)

        if response.status_code != requests.codes.ok:
            print("error " + str(response.status_code) + ": " + curl['url'])
            return dict()
        # print(response)
        resultList = json.loads(response.text)['data']
        ids = [str(x['ID']) for x in resultList]
        return ids
    
    def result_list_sichuan_meishan(self, curl):
        #print(curl['queries'])
        #print(curl['headers'])
        response = requests.post(curl['url'],
                                 data=curl['data'],
                                 headers=curl['headers'],
                                 timeout=REQUEST_TIME_OUT,
                                 stream=True,
                                 verify=False)
        resultList = json.loads(response.text)['result']['rows']
        links = [link for link in resultList]
        # html = response.content
        # soup = BeautifulSoup(html, "html.parser")
        # links = []
        # for dataset_test in soup.find('div', attrs={'class': 'dire-list-main'}).find_all('ul',attrs={}):#.find_all('li',attrs={}):#find_all('div', attrs={'class': 'tit'}):
        #     print(len(dataset_test))
        #     print('Find a dataset')
        # for dataset in soup.find('div', attrs={'class': 'dire-list-main'}).find('ul', attrs={'class': 'dlm-box'}).find_all('li'):
        #     link = dataset.find('div', attrs={'class': 'tit'}).find('h3').find('a', attrs={'href': re.compile("/portal/service_detail?id=*")})
        #     data_formats = []
        #     for data_format in dataset.find('div', attrs={'class': 'tit'}).find('h3').find_all('span'):
        #         data_format_text = data_format.get_text()
        #         if data_format_text == '接口':
        #             data_format_text = 'api'
        #         data_formats.append(data_format_text.lower())
        #     links.append({'link': link['href'], 'data_formats': str(data_formats)})
        # print(links)
        return links

    def result_list_sichuan_yibin(self, curl):
        while True:
            try:
                response = requests.get(curl['url'],
                                        params=curl['queries'],
                                        headers=curl['headers'],
                                        timeout=REQUEST_TIME_OUT,
                                        verify=False)
                break
            except:
                time.sleep(5)
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
                data_formats.append(data_format_text)
            links.append({'link': link['href'], 'data_formats': str(data_formats)})
        return links

    def result_list_sichuan_dazhou(self, curl):
        while True:
            try:
                response = requests.get(curl['url'],
                                        params=curl['queries'],
                                        headers=curl['headers'],
                                        timeout=REQUEST_TIME_OUT,
                                        verify=False)
                break
            except:
                time.sleep(5)
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
                data_formats.append(data_format_text)
            links.append({'link': link['href'], 'data_formats': str(data_formats)})
        return links

    def result_list_sichuan_yaan(self, curl):
        while True:
            try:
                response = requests.get(curl['url'],
                                        params=curl['queries'],
                                        headers=curl['headers'],
                                        timeout=REQUEST_TIME_OUT,
                                        verify=False)
                break
            except:
                time.sleep(5)
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
                data_formats.append(data_format_text)
            links.append({'link': link['href'], 'data_formats': str(data_formats)})
        return links

    def result_list_sichuan_bazhong(self, curl):
        while True:
            try:
                response = requests.post(curl['url'],
                                         params=curl['queries'],
                                         json=curl['data'],
                                         headers=curl['headers'],
                                         timeout=REQUEST_TIME_OUT,
                                         verify=False)
                break
            except:
                time.sleep(5)
        resultList = json.loads(response.text)['data']['data']
        #print(json.loads(response.text))
        links = [link['catalogInfo']['id'] for link in resultList]
        return links

    def result_list_sichuan_aba(self, curl):
        while True:
            try:
                response = requests.get(curl['url'],
                                        params=curl['queries'],
                                        headers=curl['headers'],
                                        timeout=REQUEST_TIME_OUT,
                                        verify=False)
                break
            except:
                time.sleep(5)
        resultList = json.loads(response.text)['data']['resultMap']['abaTableList']
        #print(json.loads(response.text))
        links = [link['tableId'] for link in resultList]
        return links

    def result_list_sichuan_ganzi(self, curl):
        while True:
            try:
                response = requests.post(curl['url'],
                                         json=curl['data'],
                                         headers=curl['headers'],
                                         timeout=REQUEST_TIME_OUT,
                                         verify=False)
                break
            except:
                time.sleep(5)
        resultList = json.loads(response.text)['data']['rows']
        #print(json.loads(response.text))
        links = [link['mlbh'] for link in resultList]
        return links

    def result_list_guizhou_guizhou(self, curl):
        while True:
            try:
                response = requests.post(curl['url'],
                                         json=curl['data'],
                                         headers=curl['headers'],
                                         verify=False,
                                         timeout=REQUEST_TIME_OUT)
                break
            except:
                time.sleep(5)
        #print(response)
        resultList = json.loads(response.text)['data']
        ids = [{'id': x['id'], 'resourceFormats': x['resourceFormats']} for x in resultList]
        return ids

    def result_list_guizhou_guiyang(self, curl):
        while True:
            try:
                response = requests.post(curl['url'],
                                         json=curl['data'],
                                         headers=curl['headers'],
                                         verify=False,
                                         timeout=REQUEST_TIME_OUT)
                break
            except:
                time.sleep(5)
        #print(response)
        resultList = json.loads(response.text)['data']
        ids = [{'id': x['id'], 'resourceFormats': x['resourceFormats']} for x in resultList]
        return ids

    def result_list_guizhou_liupanshui(self, curl):
        while True:
            try:
                response = requests.post(curl['url'],
                                         json=curl['data'],
                                         headers=curl['headers'],
                                         verify=False,
                                         timeout=REQUEST_TIME_OUT)
                break
            except:
                time.sleep(5)
        #print(response)
        resultList = json.loads(response.text)['data']
        ids = [{'id': x['id'], 'resourceFormats': x['resourceFormats']} for x in resultList]
        return ids

    def result_list_guizhou_zunyi(self, curl):
        while True:
            try:
                response = requests.post(curl['url'],
                                         json=curl['data'],
                                         headers=curl['headers'],
                                         verify=False,
                                         timeout=REQUEST_TIME_OUT)
                break
            except:
                time.sleep(5)
        #print(response)
        resultList = json.loads(response.text)['data']
        ids = [{'id': x['id'], 'resourceFormats': x['resourceFormats']} for x in resultList]
        return ids

    def result_list_guizhou_anshun(self, curl):
        while True:
            try:
                response = requests.post(curl['url'],
                                         json=curl['data'],
                                         headers=curl['headers'],
                                         verify=False,
                                         timeout=REQUEST_TIME_OUT)
                break
            except:
                time.sleep(5)
        #print(response)
        resultList = json.loads(response.text)['data']
        ids = [{'id': x['id'], 'resourceFormats': x['resourceFormats']} for x in resultList]
        return ids

    def result_list_guizhou_bijie(self, curl):
        while True:
            try:
                response = requests.post(curl['url'],
                                         json=curl['data'],
                                         headers=curl['headers'],
                                         verify=False,
                                         timeout=REQUEST_TIME_OUT)
                break
            except:
                time.sleep(5)
        #print(response)
        resultList = json.loads(response.text)['data']
        ids = [{'id': x['id'], 'resourceFormats': x['resourceFormats']} for x in resultList]
        return ids

    def result_list_guizhou_tongren(self, curl):
        while True:
            try:
                response = requests.post(curl['url'],
                                         json=curl['data'],
                                         headers=curl['headers'],
                                         verify=False,
                                         timeout=REQUEST_TIME_OUT)
                break
            except:
                time.sleep(5)
        #print(response)
        resultList = json.loads(response.text)['data']
        ids = [{'id': x['id'], 'resourceFormats': x['resourceFormats']} for x in resultList]
        return ids

    def result_list_guizhou_qianxinan(self, curl):
        while True:
            try:
                response = requests.post(curl['url'],
                                         json=curl['data'],
                                         headers=curl['headers'],
                                         verify=False,
                                         timeout=REQUEST_TIME_OUT)
                break
            except:
                time.sleep(5)
        #print(response)
        resultList = json.loads(response.text)['data']
        ids = [{'id': x['id'], 'resourceFormats': x['resourceFormats']} for x in resultList]
        return ids

    def result_list_guizhou_qiandongnan(self, curl):
        while True:
            try:
                response = requests.post(curl['url'],
                                         json=curl['data'],
                                         headers=curl['headers'],
                                         verify=False,
                                         timeout=REQUEST_TIME_OUT)
                break
            except:
                time.sleep(5)
        #print(response)
        resultList = json.loads(response.text)['data']
        ids = [{'id': x['id'], 'resourceFormats': x['resourceFormats']} for x in resultList]
        return ids

    def result_list_guizhou_qiannan(self, curl):
        while True:
            try:
                response = requests.post(curl['url'],
                                         json=curl['data'],
                                         headers=curl['headers'],
                                         verify=False,
                                         timeout=REQUEST_TIME_OUT)
                break
            except:
                time.sleep(5)
        #print(response)
        resultList = json.loads(response.text)['data']
        ids = [{'id': x['id'], 'resourceFormats': x['resourceFormats']} for x in resultList]
        return ids

    def result_list_shaanxi_shaanxi(self, curl):
        response = requests.get(curl['url'], params=curl['queries'], headers=curl['headers'], timeout=REQUEST_TIME_OUT)

        if response.status_code != requests.codes.ok:
            print("error " + str(response.status_code) + ": " + curl['url'])
            return dict()
        # print(response)
        resultList = json.loads(response.text)[0]['result']

        metadata_list = []

        for result in resultList:
            dataset_metadata = {}

            dataset_metadata["标题"] = result['sdataName']
            dataset_metadata["来源部门"] = result['sorgName']
            dataset_metadata["所属主题"] = result['sdataTopic']
            dataset_metadata["发布时间"] = result['spubDate'].split(' ')[0].strip()
            dataset_metadata["更新时间"] = result['spubDate'].split(' ')[0].strip()
            dataset_metadata["标签"] = result['keywords'] if 'keyword' in result else ""
            dataset_metadata["描述"] = result['sdataIntro']
            dataset_metadata["数据格式"] = result['sdataFormats']
            dataset_metadata["详情页网址"] = "http://www.sndata.gov.cn/info?id=" + result['id']

            metadata_list.append(dataset_metadata)
        return metadata_list

    def result_list_ningxia_ningxia(self, curl):
        response = requests.get(curl['url'],
                                params=curl['queries'],
                                headers=curl['headers'],
                                timeout=REQUEST_TIME_OUT,
                                verify=False)
        html = response.content.decode('utf-8')
        soup = BeautifulSoup(html, "html.parser")
        # soup = BeautifulSoup(html, "lxml")
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
                if data_format_text == '链接':
                    data_format_text = 'link'
                data_formats.append(data_format_text.lower())
            links.append({'link': link['href'], 'data_formats': str(data_formats)})
        return links

    def result_list_ningxia_yinchuan(self, curl):
        response = requests.post(curl['url'],
                                 params=curl['queries'],
                                 data=curl['data'],
                                 headers=curl['headers'],
                                 timeout=REQUEST_TIME_OUT)

        if response.status_code != requests.codes.ok:
            print("error " + str(response.status_code) + ": " + curl['url'])
            return dict()
        # print(response)
        resultList = json.loads(response.text)['data']
        ids = [(str(x['cata_id']), x['conf_catalog_format']) for x in resultList]
        return ids

    def result_list_xinjiang_wulumuqi(self, curl):
        response = requests.post(curl['url'],
                                 params=curl['queries'],
                                 data=curl['data'],
                                 headers=curl['headers'],
                                 timeout=REQUEST_TIME_OUT)

        if response.status_code != requests.codes.ok:
            print("error " + str(response.status_code) + ": " + curl['url'])
            return dict()
        # print(response)
        resultList = json.loads(response.text)['data']
        ids = [(str(x['cata_id']), x['conf_catalog_format']) for x in resultList]
        return ids

    def result_list_other(self):
        print("暂无该省")
