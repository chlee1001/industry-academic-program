import requests
import re
from bs4 import BeautifulSoup
from pymongo import MongoClient  # mongodb 모듈 지정

"""
날짜 상관없이
카테고리코드(부류) 가져오기 - getCategoryCode
각 카테고리코드에세 세부 아이템코드(품목) 가져오기 - getItemCode
세부 아이템 코드에서 세부 품종 코드가져오기 - getKindCode
그 세부 품종에서 등급은 [전체, 상품, 중품, 하품]이기 때문에 그냥 그대로 사용

완성 된 코드 모음은 DB에 저장
"""

ROOT_URL = "https://www.kamis.or.kr"
BASE_URL = ROOT_URL + "/customer/price/wholesale/item.do?action=priceinfo"

categoryCodes = dict()  # 부류
itemCodes = dict()  # 품목
codes = dict()  # 모든 코드

TregDay = '2021-01-08'


def getCategoryCode():
    smart_lists = []
    response = requests.get(BASE_URL)
    # print(response.status_code)
    if response.status_code == 200:
        text = response.text
        soup = BeautifulSoup(text, "html.parser")
        divs = soup.find_all('div', {'class': 'smart_list'}, id=False)
        # print(divs)
        for div in divs:
            smart_lists.append(div.find_all('li'))
        for idx, lists in enumerate(smart_lists):
            if idx == 0:
                for list in lists:
                    codeText = list.find('a').get_text()
                    code = re.findall("\d+", (list.find('a').get('onclick')))[0]
                    codes[code] = codeText
                    categoryCodes[code] = codeText


def getItemCode():
    for itemCategoryCode in codes.keys():
        smart_lists = []
        itemCode = dict()  # 품목

        URL = BASE_URL + '&regday=' + TregDay + '&itemcategorycode=' + itemCategoryCode + '&itemcode=&kindcode=&productrankcode=&convert_kg_yn=N'
        response = requests.get(URL)
        if response.status_code == 200:
            text = response.text
            soup = BeautifulSoup(text, "html.parser")
            divs = soup.find_all('div', {'class': 'smart_list'}, id=False)
            for div in divs:
                smart_lists.append(div.find_all('li'))
            for idx, lists in enumerate(smart_lists):
                # print(lists)
                if idx == 1:
                    for list in lists:
                        codeText = list.find('a').get_text()
                        code = re.findall("\d+", (list.find('a').get('onclick')))[0]
                        itemCode[code] = codeText
                        itemCodes[code] = codeText
                        # print(codeText, code)
            codes[itemCategoryCode] = itemCode


def getKindCode():
    for itemCategoryCode in codes.keys():
        for itemCode in codes[itemCategoryCode].keys():
            smart_lists = []
            kindCode = dict()  # 품종

            URL = BASE_URL + '&regday=' + TregDay + '&itemcategorycode=' + itemCategoryCode + '&itemcode=' + itemCode + '&kindcode=&productrankcode=&convert_kg_yn=N'
            response = requests.get(URL)
            if response.status_code == 200:
                text = response.text
                soup = BeautifulSoup(text, "html.parser")
                divs = soup.find_all('div', {'class': 'smart_list'}, id=False)
                for div in divs:
                    smart_lists.append(div.find_all('li'))
                for idx, lists in enumerate(smart_lists):
                    # print(lists)
                    if idx == 2:
                        for list in lists:
                            codeText = list.find('a').get_text()
                            code = (list.find('a').get('onclick')).split('(', 1)[1].split(')')[0].split(',')[0].split('\'')[1]
                            kindCode[code] = codeText
                            # print(codeText, code)
                codes[itemCategoryCode][itemCode] = kindCode


getCategoryCode()
getItemCode()
getKindCode()

print(categoryCodes)
print(itemCodes)
print(codes)

# mongodb 연결객체 생성
# client = MongoClient()
# client = MongoClient('192.168.19.2', '27017')  #접속IP, 포트
client = MongoClient('지우기')
db = client.KAMIS

# 컬렉션은 테이블같은 개념. sql에서는 table , mongodb는 컬렉션.
# members 컬렉션 없을 경우 생성됨.
category = db.categoryCodes
item = db.itemCodes
allCodes = db.codes

# # 정보 삽입 (반복해서 수행할 경우 같은 정보가 계속 인서트 됩니다.)
category.insert_one(categoryCodes)
item.insert_one(itemCodes)
allCodes.insert_one(codes)

# 전체검색
result = category.find()
for r in result:
    print(r)

result = item.find()
for r in result:
    print(r)

result = allCodes.find()
for r in result:
    print(r)