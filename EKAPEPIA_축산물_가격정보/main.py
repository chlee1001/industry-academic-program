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

tempDB = []  # DB에 저장하기 위한 필요정보를 임시저장하기 위함


def getData(id, kind, menuID):
    REQ_URL = ROOT_URL + kind + 'menuID=' + menuID + '&searchStartDate=' + '2021-01-20' + '&searchEndDate=' + searchEndDate  # searchStartDate에는 DB에 가장 최근 날짜
    now_date = ''
    response = requests.get(REQ_URL)
    if response.status_code == 200:
        text = response.text
        soup = BeautifulSoup(text, "html.parser")
        table = soup.find('div', {'class': 'table-wrap'})
        print(id)
        if table is not None and id != 4:
            tbody = table.find('tbody')
            trs = tbody.find_all('tr')

            if id == 0 or id == 1 or id == 3:  # 소(0), 돼지(1), 계란(3)
                for idx, tr in enumerate(trs):
                    price_list = []
                    now_date = tr.find('th').text.replace(" ", "").strip()
                    spans = tr.find_all('span', {'class': 'mr5'})

                    if not spans:  # 가격정보가 아닐 경우 패스
                        continue
                    for span in spans:
                        # print(span)
                        if len((span.text.split())) < 1:  # table에 가격 셀이 비어있는 경우 '-' 출력
                            price_list.append("-")
                        else:
                            price_list.append(span.text.split()[0])

                    # print(now_date, price_list)
                    tempDB.insert(0, (id, now_date, price_list))  # DB에 저장하기 위한 필요정보를 튜플 형태로 tempDB에 임시 저장
            else:  # 닭
                for idx, tr in enumerate(trs):
                    price_list = []
                    now_date = tr.find('th').text.replace(" ", "")
                    tds = tr.find_all('td', {'class': 'align_right'})
                    for td in tds:
                        if len((td.text.split())) < 1:  # table에 가격 셀이 비어있는 경우 '-' 출력
                            price_list.append("-")
                        else:
                            price_list.append(td.text.split()[0])
                    # print(now_date, price_list)
                    tempDB.insert(0, (id, now_date, price_list))  # DB에 저장하기 위한 필요정보를 튜플 형태로 tempDB에 임시 저장

        else:  # 오리는 사이트 코드 table태그에 문제가 있음...
            tbody = soup.find('tbody')
            trs = tbody.find_all('tr')
            for idx, tr in enumerate(trs):
                price_list = []
                now_date = tr.find('th').text.replace(" ", "").strip()
                tds = tr.find_all('td', {'class': 'align_right'})
                for td in tds:
                    if len((td.text.split())) < 1:  # table에 가격 셀이 비어있는 경우 '-' 출력
                        price_list.append("-")
                    else:
                        price_list.append(td.text.split()[0])
                # print(now_date, price_list)
                tempDB.insert(0, (id, now_date, price_list))  # DB에 저장하기 위한 필요정보를 튜플 형태로 tempDB에 임시 저장


species_id = ['소', '돼지', '닭', '계란', '오리']

result_db = {}


def scheme(idx, date, price_list):
    global result_db
    if idx == 0:
        result_db = {'Species': species_id[idx], date: {
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
        }}

    elif idx == 1:
        result_db = {'Species': species_id[idx], date: {
            "산지가격": {
                '농가수취가격(천원/110kg)': price_list[0],
            },
            "도매가격(탕박)": {
                '평균(원/kg)': price_list[1],
                '1등급(원/kg)': price_list[2]
            },
            "소비자가격": {
                '삼겹살(원/kg)': price_list[3]
            },
        }}
    elif idx == 2:
        result_db = {'Species': species_id[idx], date: {
            "산지매입": {
                '생계유통(대)': price_list[0],
                '위탁생계(중)': price_list[1],
            },
            "도매": {
                '(10호)': price_list[2],
                '(전체)': price_list[3]
            },
            '소매': price_list[4]
        }}
    elif idx == 3:
        result_db = {'Species': species_id[idx], date: {
            "산지가격": {
                "특란": {
                    '(원/30개)': price_list[0],
                    '(원/10)': price_list[1],
                }
            },
            "도매가격": {
                '특란(원/10개)': price_list[2],
            },
            "소비자가격": {
                '특란(원/30개)': price_list[3]
            },
        }}
    elif idx == 4:
        result_db = {'Species': species_id[idx], date: {
            '산지가격(20~26호)': price_list[0],
            '도매가격(20~26호)': price_list[1],
            # '소비자가격': price_list[2]
        }}

    return result_db


def saveDB(dbInfos):  # getData 함수를 이용해서 저장한 정보들을 DB에 저장
    for dbInfo in dbInfos:
        idx, date, price_list = dbInfo

        if bool(db.allDatas.find_one({'Species': species_id[idx]})):
            # print(scheme(idx, date, price_list))
            db.allDatas.update(
                {'Species': species_id[idx]},
                {"$set": scheme(idx, date, price_list)})
        else:
            db.allDatas.insert_one(scheme(idx, date, price_list))
            print("Complete Insert")
    print("Complete Update")


def main():
    global tempDB
    if len(list(db.allDatas.find())) == 0:  # 데이터가 DB에 없으면
        getSearchDate(0)
    else:
        getSearchDate(1)

    for i in range(5):  # 소, 돼지
        getData(i, kinds[i], menuIDs[i])
    saveDB(tempDB)  # getData 함수를 이용해서 저장한 정보들을 DB에 저장
    tempDB = []


if __name__ == '__main__':
    main()
