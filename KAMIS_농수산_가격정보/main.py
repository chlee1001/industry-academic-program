from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime  # 최근 1년 날짜 구하기
from pymongo import MongoClient, ReturnDocument

# mongodb 연결객체 생성
client = MongoClient('주소')
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


def getYearDate(flag):
    global last, first

    t = ['월', '화', '수', '목', '금', '토', '일']  # 요일 반환 (0:월, 1:화, 2:수, 3:목, 4:금, 5:토, 6:일)

    if flag == 0:
        targetDay = date(2020, 1, 1)
        values = (date.today() - targetDay).days
        for i in range(values + 1):
            date_value = date.today() - timedelta(days=i)
            if t[date_value.weekday()] == '토' or t[date_value.weekday()] == '일':  # 주말에는 사이트에 업데이트가 없기 때문에 스킵
                continue
            dates.insert(0, str(date_value))
        # print(dates)
    else:  # 크롤링중 에러가 난 날짜부터 다시 시작하기 위함 또는 매일매일 최신화되는데...몇일 건너뛰었을 경우
        all_datas = db.allDatas.aggregate([
            {'$sort': {'date': 1}},
            {'$group': {'_id': None, 'first': {'$first': '$date'}, 'last': {'$last': '$date'}}}
        ])
        for r in all_datas:
            last = r['last']
            first = r['first']
            # print(last, first)

        strpDateTimeLast = datetime.strptime(last, "%Y-%m-%d")
        strpDateTimeFirst = datetime.strptime(first, "%Y-%m-%d")

        eOb = (strpDateTimeLast - strpDateTimeFirst).days
        targetDay = date(2020, 1, 1)
        values = (date.today() - targetDay).days
        for i in range(values - eOb + 1):
            date_value = date.today() - timedelta(days=i)
            if t[date_value.weekday()] == '토' or t[date_value.weekday()] == '일':  # 주말에는 사이트에 업데이트가 없기 때문에 스킵
                continue
            dates.insert(0, str(date_value))
        print(dates)


ROOT_URL = "https://www.kamis.or.kr"
BASE_URL = ROOT_URL + "/customer/price/wholesale/item.do?action=priceinfo"

# 고려해야할 조건
# regday=yyyy-mm-dd     : 날짜
# itemcategorycode=#    : 부류
# itemcode=#            : 품목
# kindcode=#             : 품종
# productrankcode=#     : 등급


# URL = BASE_URL + '&regday=' + regday + '&itemcategorycode=' + str(itemcategorycode) + '&itemcode=' + str(
#     itemcode) + '&kindcode=' + kindcode + '&productrankcode=' + str(productrankcode) + '&convert_kg_yn=N'

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
    global response
    retries_number = 5
    backoff_factor = 0.5
    status_forcelist = (500, 400)

    retry = Retry(
        total=retries_number,
        read=retries_number,
        connect=retries_number,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )

    try:
        session = Session()
        session.mount("http://", HTTPAdapter(max_retries=retry))
        response = session.get(URL, timeout=80)
    except:
        print("에러")

    # response = requests.get(URL)
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
    all_datas = db.allDatas

    if bool(all_datas.find_one({'date': regday})):
        all_datas.update(
            {'date': regday},
            {"$set": {query: values}})
        print("Complete Update")

    else:
        all_datas.insert_one(data)
        print("Complete Insert")


def main():
    getKeysfromDB()
    codes.pop('_id')
    categoryCodes.pop('_id')
    itemCodes.pop('_id')

    if len(list(db.allDatas.find())) == 0:  # 데이터가 DB에 없으면
        getYearDate(0)
    else:
        getYearDate(1)

    for date in dates:
        for itemCategoryValue in categoryCodes:
            for itemValue in codes[itemCategoryValue].keys():
                for kindValue in codes[itemCategoryValue][itemValue].keys():
                    if kindValue == '전체':  # 등급이 전체로 분류 된 것은 스킵
                        continue
                    for productRankCode in productRankCodes.keys():
                        getData(date, itemCategoryValue, itemValue, kindValue, productRankCode)
        # dates.pop(0)  # 업데이트 완료 시 그 해당 날짜 리스트에서 제거 (코드삭제)


if __name__ == '__main__':
    main()
