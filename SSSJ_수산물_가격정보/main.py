from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import time
from datetime import date, timedelta, datetime  # 최근 1년 날짜 구하기
from pymongo import MongoClient

# # mongodb 연결객체 생성
# client = MongoClient('주소')
# db = client.EKAPEPIA

PATH = 'chromedriver.exe'
wd = webdriver.Chrome(executable_path=PATH)
URL = 'https://www.susansijang.co.kr/nsis/miw/ko/info/miw3110'

have_made_scheme = 0

saving_data = []


def get_date():
    dates = []
    firstDate = date(2020, 1, 1)
    countDate = (date.today() - firstDate).days
    for i in range(countDate + 1):
        date_value = date.today() - timedelta(days=i)
        if date_value.weekday() == '6':  # 일요일에는 사이트에 업데이트가 없기 때문에 스킵
            continue
        dates.insert(0, str(date_value))
    return dates


def get_last_page(date):
    result = requests.get(f"{URL}?searchDe={date}")
    soup = BeautifulSoup(result.text, "html.parser")
    pagination = soup.find("div", {"class": "paginate"})
    a_tags = pagination.find_all('a')
    if not a_tags:  # 조회 된 정보가 없을 시 당연히 페이지가 없기 때문에 패스
        return 0
    last = a_tags[-1]
    max_page = int((last.get('onclick').split('(')[1].split(')')[0]))
    return max_page


def make_scheme(rows):
    for row in rows:
        datas = row.split(' ')
        result = {
            '어종': datas[0],
            '산지': datas[1],
            '규격': datas[2],
            '포장': datas[3],
            '수량': datas[4],
            '낙찰고가': datas[5],
            '낙찰저가': datas[6],
            '평균가': datas[7],
        }
        # print(result)
        saving_data.append(result)


def saveDB():
    global saving_data
    print(saving_data)
    saving_data = []


def crawling():
    dates = get_date()

    heads = []
    bodys = []

    for date in dates:
        last_page = get_last_page(date)
        for page in range(1, last_page + 1):  # 1페이지부터 마지막 페이지까지
            print(f"Scrapping : Date {date}, Page {page}")  # 스크랩 중인 날짜와 페이지
            wd.get(f"{URL}?searchDe={date}&pageIndex={page}")
            time.sleep(1)  # 1초에 한번씩

            table = wd.find_element_by_class_name('print_table')
            # # 우선 DB구조가 만들어지지 않았으면 테이블 헤드 구하기
            # if not have_made_scheme:
            thead = table.find_element_by_tag_name("thead")
            head = thead.find_elements_by_tag_name("th")
            for index, value in enumerate(head):
                heads.append(value.text)
            # print(heads)

            # 그 다음 테이블 몸통
            tbody = table.find_element_by_tag_name("tbody")
            rows = tbody.find_elements_by_tag_name("tr")
            for index, value in enumerate(rows):
                bodys.append(value.text)

            # print(bodys[0].split(' '))
            make_scheme(bodys)
        saveDB()

    # date = '2021-02-05'
    # page = 1
    # print(f"Scrapping : Date {date}, Page {page}")  # 스크랩 중인 날짜와 페이지
    # wd.get(f"{URL}?searchDe={date}&pageIndex={page}")
    # time.sleep(1)  # 1초에 한번씩


crawling()
