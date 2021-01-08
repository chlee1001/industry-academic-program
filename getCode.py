import requests
import re
from bs4 import BeautifulSoup
from datetime import date, timedelta  # 최근 1년 날짜 구하기

ROOT_URL = "https://www.kamis.or.kr"
BASE_URL = "https://www.kamis.or.kr/customer/price/wholesale/item.do?action=priceinfo"

codes = dict()

productRankCodes = dict()  # 등급

TregDay = '2021-01-08'
TitemCategoryCode = ""
TitemCode = ""
TkindCode = ''
TproductRankCode = ""


def getCategoryCode(URL):
    smart_lists = []
    response = requests.get(URL)
    # print(response.status_code)
    if response.status_code == 200:
        text = response.text
        soup = BeautifulSoup(text, "html.parser")
        section = soup.find('section', {'class': 'smart_searchWrap type1'})
        divs = soup.find_all('div', {'class': 'smart_list'})
        for div in divs:
            smart_lists.append(div.find_all('li'))
        for idx, lists in enumerate(smart_lists):
            if idx == 6:
                for list in lists:
                    codeText = list.find('a').get_text()
                    code = re.findall("\d+", (list.find('a').get('onclick')))[0]
                    codes[code] = codeText


def getItemCode(BASE_URL):
    for itemCategoryCode in codes.keys():
        smart_lists = []
        itemCodes = dict()  # 품목

        URL = BASE_URL + '&regday=' + TregDay + '&itemcategorycode=' + itemCategoryCode + '&itemcode=' + TitemCode + '&kindcode=' + TkindCode + '&productrankcode=' + TproductRankCode + '&convert_kg_yn=N'
        response = requests.get(URL)
        # print(response.status_code)
        if response.status_code == 200:
            text = response.text
            soup = BeautifulSoup(text, "html.parser")
            section = soup.find('section', {'class': 'smart_searchWrap type1'})
            divs = soup.find_all('div', {'class': 'smart_list'})
            for div in divs:
                smart_lists.append(div.find_all('li'))
            for idx, lists in enumerate(smart_lists):
                # print(lists)
                if idx == 7:
                    for list in lists:
                        codeText = list.find('a').get_text()
                        code = re.findall("\d+", (list.find('a').get('onclick')))[0]
                        itemCodes[code] = codeText
                        # print(codeText, code)
            codes[itemCategoryCode] = itemCodes


getCategoryCode(BASE_URL)
getItemCode(BASE_URL)

for itemCategoryCode in codes.keys():
    for itemCode in codes[itemCategoryCode].keys():
        print(itemCategoryCode, itemCode)
        smart_lists = []
        kindCode = dict()  # 품종

        URL = BASE_URL + '&regday=' + TregDay + '&itemcategorycode=' + itemCategoryCode + '&itemcode=' + itemCode + '&kindcode=' + TkindCode + '&productrankcode=' + TproductRankCode + '&convert_kg_yn=N'
        response = requests.get(URL)
        # print(response.status_code)
        if response.status_code == 200:
            text = response.text
            soup = BeautifulSoup(text, "html.parser")
            section = soup.find('section', {'class': 'smart_searchWrap type1'})
            divs = soup.find_all('div', {'class': 'smart_list'})
            for div in divs:
                smart_lists.append(div.find_all('li'))
            for idx, lists in enumerate(smart_lists):
                # print(lists)
                if idx == 8:
                    for list in lists:
                        codeText = list.find('a').get_text()
                        code = (list.find('a').get('onclick')).split('(', 1)[1].split(')')[0].split(',', 1)[0]
                        kindCode[code] = codeText
                        print(codeText, code)
            codes[itemCategoryCode][itemCode] = kindCode

print(codes)
