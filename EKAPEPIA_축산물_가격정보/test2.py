import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime  # 최근 1년 날짜 구하기
from pymongo import MongoClient

# mongodb 연결객체 생성
client = MongoClient('mongodb://chlee1001:dlcogus@192.168.1.2:27017')
db = client.EKAPEPIA

searchStartDate = '2020-01-01'
searchEndDate = '2020-01-01'


def getSearchDate(flag):
    global searchStartDate, searchEndDate
    endDate = date.today() - timedelta(days=1)  # 하루전

    if flag == 0:  # DB에 데이터가 없을 경우에는 기준일(20.01.01)부터
        searchStartDate = '2020-01-01'
        searchEndDate = str(endDate)
    else:
        all_datas = db.allDatas.aggregate([
            {'$sort': {'date': 1}},
            {'$group': {'_id': None, 'first': {'$first': '$date'}, 'last': {'$last': '$date'}}}
        ])
        for r in all_datas:
            searchStartDate = r['last']
            searchEndDate = str(endDate)


ROOT_URL = "https://www.ekapepia.com/priceStat"
# REQ_URL =Root_URL + "/distrPriceBeef.do?menuId=menu100033&searchStartDate=2020-01-10&searchEndDate=2021-01-20"


# 소, 돼지, 닭, 계란, 오리 순
kinds = ['/distrPriceBeef.do?', '/distrPricePork.do?', '/poultry/periodMarketPrice.do?', '/distrPriceEgg.do?',
         '/distrPriceDuck.do?']
menuIDs = ['menu100033', 'menu100034', 'menu100039', 'menu100155', 'menu100151']


def getData(id, kind, menuID):
    REQ_URL = ROOT_URL + kind + 'menuID=' + menuID + '&searchStartDate=' + searchEndDate + '&searchEndDate=' + searchEndDate

    response = requests.get(REQ_URL)
    if response.status_code == 200:
        text = response.text
        soup = BeautifulSoup(text, "html.parser")
        table = soup.find('div', {'class': 'table-wrap'})
        # print(table)
        if table is not None:
            trs = table.find_all('tr')
            for i in range(len(trs) - 1):
                ths = trs[0].find_all('th')
                for j in range(len(ths)):
                    print(ths[j + 1].text)


def saveDB():
    print("Save DB")


def main():
    if len(list(db.allDatas.find())) == 0:  # 데이터가 DB에 없으면
        getSearchDate(0)
    else:
        getSearchDate(1)
    for i in range(1):
        getData(i, kinds[i], menuIDs[i])


if __name__ == '__main__':
    main()
