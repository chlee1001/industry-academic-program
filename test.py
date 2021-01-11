import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta  # 최근 1년 날짜 구하기
from pymongo import MongoClient

codes = dict()  # key모음
categoryCodes = dict()  # 부류
itemCodes = dict()  # 품목
# productRankCodes = ['1', '2']  # 상품, 중품 , 전체(0)은 뺌
productRankCodes = {'1': '상품',
                    '2': '중품'}


def getKeysfromDB():
    # mongodb 연결객체 생성
    client = MongoClient('주소지우기')
    db = client.KAMIS
    db_codes = db.codes.find({})
    db_categoryCodes = db.categoryCodes.find({})
    db_itemCodes = db.itemCodes.find({})
    for r in db_codes:
        global codes
        codes = r
    for r in db_categoryCodes:
        global categoryCodes
        categoryCodes = r
    for r in db_itemCodes:
        global itemCodes
        itemCodes = r


dates = []


def getYearDate():
    for i in range(366):
        date_value = str(date.today() - timedelta(days=i))
        dates.append(date_value)

    # print(dates)


ROOT_URL = "https://www.kamis.or.kr"
BASE_URL = ROOT_URL + "/customer/price/wholesale/item.do?action=priceinfo"

# 식량작물
# ?action=priceinfo&regday=2021-01-08&itemcategorycode=100&itemcode=111&kindcode=&productrankcode=0&convert_kg_yn=N

# 채소류 - 배추 -전체
# ?action=priceinfo&regday=2021-01-08&itemcategorycode=200&itemcode=211&kindcode=&productrankcode=&convert_kg_yn=N
# ?action=priceinfo&regday=2021-01-08&itemcategorycode=200&itemcode=211&kindcode=01&productrankcode=&convert_kg_yn=N

# 고려해야할 조건
# regday=yyyy-mm-dd     : 날짜
# itemcategorycode=#    : 부류
# itemcode=#            : 품목
# kincode=#             : 품종
# productrankcode=#     : 등급


# URL = BASE_URL + '&regday=' + regday + '&itemcategorycode=' + str(itemcategorycode) + '&itemcode=' + str(
#     itemcode) + '&kincode=' + kincode + '&productrankcode=' + str(productrankcode) + '&convert_kg_yn=N'

title = []


def getTitle(soup, title):
    print('-' * 30)
    title_category = categoryCodes[title[1]]
    title_item = itemCodes[title[2]]
    title_kind = codes[title[1]][title[2]][title[3]]
    title_rank = productRankCodes[title[4]]
    temps = soup.find('section', {'class': 'clear mt30'}) and soup.select('h3')
    for idx, temp in enumerate(temps):
        if idx == 5:
            weight = temp.text.split(':')[1].strip()
            # print(temp.text.strip(), end="")
    print(title[0], title_category, title_item, title_kind, title_rank, weight)


def getData(regday, itemCategoryCode, itemCode, kindCode, productRankCode):
    URL = BASE_URL + '&regday=' + regday + '&itemcategorycode=' + itemCategoryCode + '&itemcode=' + itemCode + '&kindcode=' + kindCode + '&productrankcode=' + productRankCode + '&convert_kg_yn=N'
    response = requests.get(URL)
    # print(response.status_code)
    if response.status_code == 200:
        text = response.text
        soup = BeautifulSoup(text, "html.parser")

        table = soup.find('table', {'class': 'wtable3'})
        if table is not None:
            trs = table.find_all('tr')
            if len(trs) > 2:
                global title
                title = [regday, itemCategoryCode, itemCode, kindCode, productRankCode]
                getTitle(soup, title)

                for idx, tr in enumerate(trs):
                    if idx > 0:  # 구분, Value
                        tds = tr.find_all('td')
                        # Table에서 colspan인 부분: 평균, 최고값, 최저값, 등락률
                        if tr.find('td', {'class': 'first cell_tit1'}) and tr.select('td[colspan]'):
                            for i in range(2):
                                print(tds[i].text, end=" ")
                            print()
                        # Table에서 rowspan인 부분: 지역별 가격
                        elif tr.find('td', {'class': 'first cell_tit1'}) and tr.select('td[rowspan]'):
                            for i in range(3):
                                print(tds[i].text, end=" ")
                            print()


getKeysfromDB()
getYearDate()

# getData(dates[0])
count = 0
for date in dates:
    if count > 0:
        break

    for idx, itemCategoryCode in enumerate(codes.keys()):
        if idx == 0:
            continue
        for itemCode in codes[itemCategoryCode].keys():
            for kindCode in codes[itemCategoryCode][itemCode].keys():
                if kindCode == '':  # 등급이 전체로 분류 된 것은 스킵
                    continue
                for productRankCode in productRankCodes.keys():
                    getData(date, itemCategoryCode, itemCode, kindCode, productRankCode)
    count += 1
