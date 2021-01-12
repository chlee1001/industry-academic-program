import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta  # 최근 1년 날짜 구하기
from pymongo import MongoClient, ReturnDocument

# mongodb 연결객체 생성
client = MongoClient('주소지우기')
db = client.KAMIS

codes = dict()  # key모음
categoryCodes = dict()  # 부류
itemCodes = dict()  # 품목
# productRankCodes = ['1', '2']  # 상품, 중품 , 전체(0)은 뺌
productRankCodes = {'1': '상품',
                    '2': '중품'}


def getKeysfromDB():
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
    global weight
    print('-' * 30)
    title_category = title[1]
    title_item = title[2]
    title_kind = title[3]
    title_rank = productRankCodes[title[4]]
    temps = soup.find('section', {'class': 'clear mt30'}) and soup.select('h3')
    for idx, temp in enumerate(temps):
        if idx == 5:
            weight = temp.text.split(':')[1].strip()
            # print(temp.text.strip(), end="")

    print(title[0], title_category, title_item, title_kind, title_rank, weight)


def getData(regday, itemCategoryValue, itemValue, kindValue, productRankCode):
    itemCategoryCode = categoryCodes[itemCategoryValue]
    itemCode = itemCodes[itemValue]
    kindCode = codes[itemCategoryValue][itemValue][kindValue]

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
                title = [regday, itemCategoryValue, itemValue, kindValue, productRankCode]
                getTitle(soup, title)
                temp_dict = {}
                for idx, tr in enumerate(trs):
                    if idx > 0:  # 구분: Value
                        tds = tr.find_all('td')
                        # Table에서 colspan인 부분: 평균, 최고값, 최저값, 등락률
                        if tr.find('td', {'class': 'first cell_tit1'}) and tr.select('td[colspan]'):
                            temp_dict[tds[0].text] = tds[1].text
                        # Table에서 rowspan인 부분: 지역별 가격
                        elif tr.find('td', {'class': 'first cell_tit1'}) and tr.select('td[rowspan]'):
                            temp_dict[tds[0].text] = tds[2].text

                query = (itemCategoryValue + '.' + itemValue + '.' + kindValue + '.' + productRankCodes[
                    productRankCode])

                data = dict()
                temp1 = dict()
                temp2 = dict()
                temp3 = dict()
                temp3[productRankCodes[productRankCode]] = temp_dict
                temp2[kindValue] = temp3
                temp1[itemValue] = temp2
                data[itemCategoryValue] = temp1

                test = {'date': regday}

                saveDB(dict(test, **data), regday, temp_dict, query)


def saveDB(data, regday, values, query):
    datas = db.datas

    if bool(datas.find_one({'date': regday})):
        datas.update(
            {'date': regday},
            {"$set": {query: values}})
        print("Complete Update")
    else:
        datas.insert_one(data)
        print("Complete Insert")


getKeysfromDB()
codes.pop('_id')
categoryCodes.pop('_id')
itemCodes.pop('_id')
getYearDate()

# getData(dates[0])
count = 0
for date in dates:
    if count > 1:
        break

    for itemCategoryValue in categoryCodes:
        for itemValue in codes[itemCategoryValue].keys():
            for kindValue in codes[itemCategoryValue][itemValue].keys():
                if kindValue == '전체':  # 등급이 전체로 분류 된 것은 스킵
                    continue
                for productRankCode in productRankCodes.keys():
                    getData(date, itemCategoryValue, itemValue, kindValue, productRankCode)
    count += 1
