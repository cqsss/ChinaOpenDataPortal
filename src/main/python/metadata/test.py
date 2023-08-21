import requests

headers = {
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'Origin': 'https://data.cq.gov.cn',
    'Referer': 'https://data.cq.gov.cn/rop/assets',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'accept': '*/*',
    'content-type': 'application/json',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

json_data = {
    'operationName':
        None,
    'variables': {
        'input': {
            'offset': 0,
            'limit': 10,
            'keyword': '',
            'classificationId': None,
            'shareType': None,
            'ordFiled': None,
            'ordSort': None,
            'openAttr': None,
            'tags': {},
        },
    },
    'extensions': {},
    'query':
        'query ($input: ResourceProductPageInput) {\n  result: resourcesCatalogueList(input: $input) {\n    total\n    offset\n    limit\n    data {\n      id\n      resourceName\n      resourceDesc\n      organizationId\n      organizationName\n      classificationId\n      classificationName\n      updateDate\n      classType\n      shareType\n      openAttr\n      renewCycle\n      downloadCnt\n      visitCnt\n      districtNum\n      organClassNum\n      accessType\n      score\n      fileTypes\n      tags\n      interfaceNum\n      fileNum\n      datasetNum\n      __typename\n    }\n    __typename\n  }\n}\n',
}

response = requests.post('https://data.cq.gov.cn/rop-frontier/graphql', headers=headers, json=json_data)

# Note: json_data will not be serialized by requests
# exactly as it was in the original request.
# data = '{"operationName":null,"variables":{"input":{"offset":20,"limit":10,"keyword":"","classificationId":null,"shareType":null,"ordFiled":null,"ordSort":null,"openAttr":null,"tags":{}}},"extensions":{},"query":"query ($input: ResourceProductPageInput) {\\n  result: resourcesCatalogueList(input: $input) {\\n    total\\n    offset\\n    limit\\n    data {\\n      id\\n      resourceName\\n      resourceDesc\\n      organizationId\\n      organizationName\\n      classificationId\\n      classificationName\\n      updateDate\\n      classType\\n      shareType\\n      openAttr\\n      renewCycle\\n      downloadCnt\\n      visitCnt\\n      districtNum\\n      organClassNum\\n      accessType\\n      score\\n      fileTypes\\n      tags\\n      interfaceNum\\n      fileNum\\n      datasetNum\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}'
# response = requests.post('https://data.cq.gov.cn/rop-frontier/graphql', headers=headers, data=data)

print(response.text)
