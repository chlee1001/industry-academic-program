import requests
import re
from bs4 import BeautifulSoup
from datetime import date, timedelta  # 최근 1년 날짜 구하기

ROOT_URL = "https://www.kamis.or.kr"
BASE_URL = "https://www.kamis.or.kr/customer/price/wholesale/item.do?action=priceinfo"

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

regDay = '2021-01-08'
itemCategoryCode = 100
itemCode = 111
kinCode = ''
productRankCode = 0

dates = []


def getYearDate():
    for i in range(366):
        date_value = str(date.today() - timedelta(days=i))
        dates.append(date_value)

    # print(dates)


# URL = BASE_URL + '&regday=' + regday + '&itemcategorycode=' + str(itemcategorycode) + '&itemcode=' + str(
#     itemcode) + '&kincode=' + kincode + '&productrankcode=' + str(productrankcode) + '&convert_kg_yn=N'

def getItemCode(URL):
    response = requests.get(URL)
    # print(response.status_code)
    if response.status_code == 200:
        text = response.text
        soup = BeautifulSoup(text, "html.parser")
        divs = soup.find_all('div', {'class': 'smart_list searchCommArea'})
        temps = []
        for div in divs:
            # print(div)
            temps.append(div.find_all('li'))

        for idx, temp in enumerate(temps):
            if idx == 1:
                for test in temp:
                    codeText = test.find('a').get_text()
                    code = re.findall("\d+", (test.find('a').get('onclick')))[0]
                    itemCategoryCodes[code] = codeText


itemCategoryCodes = dict()  # 부류
itemCodes = dict()  # 품목
kinCodes = dict()  # 품종
productRankCodes = dict()  # 등급


def getData(regday):
    URL = BASE_URL + '&regday=' + regday + '&itemcategorycode=' + str(itemCategoryCode) + '&itemcode=' + str(
        itemCode) + '&kincode=' + kinCode + '&productrankcode=' + str(productRankCode) + '&convert_kg_yn=N'
    response = requests.get(URL)
    # print(response.status_code)
    if response.status_code == 200:
        text = response.text
        soup = BeautifulSoup(text, "html.parser")
        table = soup.find('table', {'class': 'wtable3'})

        trs = table.find_all('tr')
        flag = 0
        for idx, tr in enumerate(trs):
            if idx > 0:  # 구분, Value
                tds = tr.find_all('td')

                if tr.find('td', {'class': 'cell_tit2'}) and flag == 0:
                    flag = 1
                    for i in range(3):
                        print(tds[i].text, end=" ")
                    print()
                elif tr.find('td', {'class': 'cell_tit2'}) and flag == 1:
                    flag = 0
                    print("\t", end="")
                    for i in range(2):
                        print(tds[i].text, end=" ")
                    print()
                else:
                    for i in range(2):
                        print(tds[i].text, end=" ")
                    print()
            else:
                print(regday)
            # else:  # 구분, 날짜
            #     ths = tr.find_all('th')
            #     for i in range(2):
            #         print(ths[i].text, end="|")
            #     print()


getYearDate()

getItemCode(BASE_URL)
print(itemCategoryCodes)
print(itemCodes)
print(kinCodes)
print(productRankCodes)
# getData(dates[0])
# count = 0
# for date in dates:
#     if count > 10:
#         break
#     getData(date)
#     count += 1
