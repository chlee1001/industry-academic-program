import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime  # 최근 1년 날짜 구하기
from pymongo import MongoClient

# mongodb 연결객체 생성
client = MongoClient('주소')
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
    print(searchEndDate)
    REQ_URL = ROOT_URL + kind + 'menuID=' + menuID + '&searchStartDate=' + '2021-01-22' + '&searchEndDate=' + '2021-01-22'
    now_date = ''
    response = requests.get(REQ_URL)
    if response.status_code == 200:
        text = response.text
        soup = BeautifulSoup(text, "html.parser")
        table = soup.find('div', {'class': 'table-wrap'})
        # print(table)
        if table is not None:
            trs = table.find_all('tr')
            # tr0~2까지 정보...

            table_list = []
            price_list = []
            division1 = []
            division2 = []
            division3 = []
            for idx, tr in enumerate(trs):
                if idx == 0:
                    ths = tr.find_all('th')
                    for i in range(len(ths) - 1):  # (0~2)
                        table_list.append(ths[i + 1].text)
                        division1.append(ths[i + 1].text)


                elif idx == 1:
                    ths = tr.find_all('th')
                    for i in range(len(ths)):  # (0~2)
                        table_list.append(ths[i].text)
                        division2.append(ths[i].text)
                elif idx == 2:
                    ths = tr.find_all('th')
                    for i in range(len(ths)):  # (0~2)
                        table_list.append(ths[i].text)
                        division3.append(ths[i].text)
                else:
                    # print(tr)
                    now_date = tr.find('th').text.replace(" ", "")
                    # print(now_date)
                    spans = tr.find_all('span')
                    for span in spans:
                        if len((span.text.split())) < 1:  # table에 가격 셀이 비어있는 경우 '-' 출력
                            price_list.append("-")
                        else:
                            price_list.append(span.text.split()[0])
            # print(table_list)
            # print(price_list)

            # for i in range(len(price_list)):
            #     test1[table_list[len(table_list) - len(price_list) + i]] = price_list[i]
            #     # print(table_list[len(table_list) - len(price_list) + i])
            #     # print(table_list[len(table_list) - len(price_list):])
            # print(test1)
            # for j in range(4):
            #     print(table_list[len(table_list) - len(price_list) - 4 + j])

            row_division1 = {}  # 경매가격
            row_division2 = {}  # 지육가격
            row_division3 = {}  # 부분육가격
            row_division4 = {}  # 한우등심

            # 개수는 colspan과 rowspan으로 일단 파악해보기.. 안되면 어쩔수 없고
            for i in range(3):
                row_division1[division3.pop(0)] = price_list.pop(0)
            for i in range(2):
                row_division2[division3.pop(0)] = price_list.pop(0)
            row_division3[division3.pop(0)] = price_list.pop(0)
            row_division4[division3.pop(0)] = price_list.pop(0)

            test1 = dict()
            test2 = dict()
            test3 = dict()
            test4 = dict()
            test1[division2[0]] = row_division1
            test2[division2[1]] = row_division2
            test3[division2[2]] = row_division3
            test4[division2[3]] = row_division4


            dic1 = {}  # 산지가격
            dic2 = {}  # 도매가격
            dic3 = {}  # 소비자가격
            dic1[division1[0]] = test1
            dic2[division1[1]] = test2, test3
            dic3[division1[2]] = test4


            result={}
            result[now_date] = dic1, dic2,dic3
            print(result)


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
