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
    REQ_URL = ROOT_URL + kind + 'menuID=' + menuID + '&searchStartDate=' + '2021-01-20' + '&searchEndDate=' + searchEndDate  # searchStartDate에는 DB에 가장 최근 날짜
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
            for idx, tr in enumerate(trs):
                if idx == 0:
                    ths = tr.find_all('th')
                    for i in range(len(ths) - 1):  # (0~2)
                        table_list.append(ths[i + 1].text)

                elif idx == 1:
                    ths = tr.find_all('th')
                    for i in range(len(ths)):  # (0~2)
                        table_list.append(ths[i].text)

                elif idx == 2:
                    ths = tr.find_all('th')
                    for i in range(len(ths)):  # (0~2)
                        table_list.append(ths[i].text)

                else:
                    # print(tr)
                    price_list = []
                    now_date = tr.find('th').text.replace(" ", "")

                    spans = tr.find_all('span', {'class': 'mr5'})
                    for span in spans:
                        # print(span)
                        if len((span.text.split())) < 1:  # table에 가격 셀이 비어있는 경우 '-' 출력
                            price_list.append("-")
                        else:
                            price_list.append(span.text.split()[0])

                    print(now_date)
                    print(price_list)
                    saveDB(id, now_date, price_list)


species_id = ['소', '돼지', '닭', '계란', '오리']



test = {}


def scheme(idx, date, price_list):
    if idx == 0:
        test = {'Species': species_id[idx]}
        test[date] = {
            "산지가격": {
                "가축시장 경매가격(천원/마리)": {
                    '암송아지(6~7개월)': price_list[0],
                    '숫송아지(6~7개월)': price_list[1],
                    '농가수취가격(600kg)': price_list[2]
                }
            },
            "도매가격": {
                "지육가격(한우)(원/kg)": {
                    '평균': price_list[3],
                    '1등급': price_list[4]
                },
                "부분육가격(한우, 등심)(원/kg)": {
                    '1등급': price_list[5]
                }
            },
            "소비자가격": {
                '한우, 등심(원/kg)': {
                    '1등급': price_list[6]
                }
            },
        }
        return test
    elif idx == 1:
        test = {'Species': species_id[idx]}
        test[date] = {
            "산지가격": {
                "가축시장 경매가격(천원/마리)": {
                    '암송아지(6~7개월)': price_list[0],
                    '숫송아지(6~7개월)': price_list[1],
                    '농가수취가격(600kg)': price_list[2]
                }
            },
            "도매가격": {
                "지육가격(한우)(원/kg)": {
                    '평균': price_list[3],
                    '1등급': price_list[4]
                },
                "부분육가격(한우, 등심)(원/kg)": {
                    '1등급': price_list[5]
                }
            },
            "소비자가격": {
                '한우, 등심(원/kg)': {
                    '1등급': price_list[6]
                }
            },
        }
        return test


def saveDB(idx, date, price_list):
    print("Save DB")
    if bool(db.allDatas.find_one({'Species': species_id[idx]})):
        print(scheme(idx, date, price_list))

        db.allDatas.update(
            {'Species': species_id[idx]},
            {"$set": scheme(idx, date, price_list)})
        print("Complete Update")
    else:

        db.allDatas.insert_one(scheme(idx, date, price_list))
        print("Complete Insert")


def main():
    if len(list(db.allDatas.find())) == 0:  # 데이터가 DB에 없으면
        getSearchDate(0)
    else:
        getSearchDate(1)
    for i in range(1):
        getData(i, kinds[i], menuIDs[i])


if __name__ == '__main__':
    main()
