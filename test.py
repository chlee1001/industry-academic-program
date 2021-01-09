import requests
import re
from bs4 import BeautifulSoup
from datetime import date, timedelta  # 최근 1년 날짜 구하기

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


dates = []


def getYearDate():
    for i in range(366):
        date_value = str(date.today() - timedelta(days=i))
        dates.append(date_value)

    # print(dates)


# URL = BASE_URL + '&regday=' + regday + '&itemcategorycode=' + str(itemcategorycode) + '&itemcode=' + str(
#     itemcode) + '&kincode=' + kincode + '&productrankcode=' + str(productrankcode) + '&convert_kg_yn=N'

# 테스트용... 실제로는 DB에 저장 된 값 이용할 예정
categoryCodes = dict()  # 부류
categoryCodes = {'100': '식량작물', '200': '채소류', '300': '특용작물', '400': '과일류', '600': '수산물'}

itemCodes = dict()  # 품목
itemCodes = {'111': '쌀', '112': '찹쌀', '141': '콩', '142': '팥', '143': '녹두', '144': '메밀', '151': '고구마', '152': '감자',
             '211': '배추', '212': '양배추', '213': '시금치', '214': '상추', '215': '얼갈이배추', '221': '수박', '222': '참외',
             '223': '오이', '224': '호박', '225': '토마토', '226': '딸기', '231': '무', '232': '당근', '233': '열무', '241': '건고추',
             '242': '풋고추', '243': '붉은고추', '244': '피마늘', '258': '깐마늘(국산)', '259': '깐마늘(수입)', '245': '양파', '246': '파',
             '247': '생강', '252': '미나리', '253': '깻잎', '255': '피망', '256': '파프리카', '257': '멜론', '422': '방울토마토',
             '312': '참깨', '313': '들깨', '314': '땅콩', '315': '느타리버섯', '316': '팽이버섯', '317': '새송이버섯', '411': '사과',
             '412': '배', '413': '복숭아', '414': '포도', '415': '감귤', '416': '단감', '418': '바나나', '419': '참다래', '420': '파인애플',
             '421': '오렌지', '424': '레몬', '425': '체리', '428': '망고', '611': '고등어', '613': '갈치', '615': '명태', '619': '물오징어',
             '638': '건멸치', '639': '북어', '640': '건오징어', '641': '김', '642': '건미역', '644': '굴', '653': '전복', '654': '새우'}

codes = dict()
codes = {'100': {'111': {'': '전체', '01': '일반계', '05': '햇일반계'}, '112': {'01': '일반계'},
                 '141': {'01': '흰 콩(국산)', '02': '콩나물콩', '03': '흰 콩(수입)'}, '142': {'00': '붉은 팥(국산)', '01': '붉은 팥(수입)'},
                 '143': {'00': '국산', '01': '수입'}, '144': {'01': '메밀(수입)'}, '151': {'00': '밤'},
                 '152': {'': '전체', '01': '수미', '02': '대지마'}},
         '200': {'211': {'': '전체', '01': '봄', '02': '고랭지', '03': '가을', '06': '월동'}, '212': {'00': '양배추'},
                 '213': {'00': '시금치'}, '214': {'01': '적', '02': '청'}, '215': {'00': '얼갈이배추'}, '221': {'00': '수박'},
                 '222': {'00': '참외'}, '223': {'01': '가시계통', '02': '다다기계통', '03': '취청'},
                 '224': {'01': '애호박', '02': '쥬키니'}, '225': {'00': '토마토'}, '226': {'00': '딸기'},
                 '231': {'': '전체', '01': '봄', '02': '고랭지', '03': '가을', '06': '월동'},
                 '232': {'01': '무세척', '02': '세척', '10': '세척(수입)'}, '233': {'00': '열무'},
                 '241': {'AA': '전체(화건)', '00': '화건', '01': '햇산화건', 'BB': '전체(양건)', '02': '양건', '03': '햇산양건',
                         '10': '수입'}, '242': {'00': '풋고추', '02': '꽈리고추', '03': '청양고추'}, '243': {'00': '붉은고추'},
                 '244': {'03': '한지', 'CC': '난지(전체)', '21': '햇난지(대서)', '22': '난지(대서)', '23': '햇난지(남도)', '24': '난지(남도)',
                         '04': '난지', '01': '한지1접', '02': '난지1접', '07': '햇난지1접'},
                 '258': {'': '전체', '01': '깐마늘(국산)', '03': '깐마늘(대서)', '04': '햇깐마늘(대서)', '05': '깐마늘(남도)',
                         '06': '햇깐마늘(남도)'}, '259': {'01': '깐마늘(수입)'},
                 '245': {'': '전체', '00': '양파', '02': '햇양파', '10': '수입'}, '246': {'00': '대파', '02': '쪽파'},
                 '247': {'00': '국산', '01': '수입'}, '252': {'00': '미나리'}, '253': {'00': '깻잎'}, '255': {'00': '청'},
                 '256': {'00': '파프리카'}, '257': {'00': '멜론'}, '422': {'01': '방울토마토', '02': '대추방울토마토'}},
         '300': {'312': {'01': '백색(국산)', '02': '중국', '03': '인도'}, '313': {'01': '국산', '02': '수입'},
                 '314': {'01': '국산', '02': '수입'}, '315': {'00': '느타리버섯', '01': '애느타리버섯'}, '316': {'00': '팽이버섯'},
                 '317': {'00': '새송이버섯'}},
         '400': {'411': {'05': '후지', '06': '쓰가루', '07': '홍로'}, '412': {'01': '신고', '04': '원황'},
                 '413': {'01': '백도', '05': '유명'},
                 '414': {'01': '캠벨얼리', '02': '거봉', '06': 'MBA', '08': '레드글로브 칠레', '09': '레드글로브 페루', '10': '톰슨 미국',
                         '11': '톰슨 호주', '07': '수입', '12': '샤인머스켓'}, '415': {'01': '노지', '02': '시설', '00': '감귤'},
                 '416': {'00': '단감'}, '418': {'02': '수입'}, '419': {'01': '국산', '02': '그린 뉴질랜드'}, '420': {'02': '수입'},
                 '421': {'03': '네이블 미국', '05': '네이블 EU', '06': '네이블 호주', '04': '발렌시아 미국'}, '424': {'00': '수입'},
                 '425': {'00': '수입'}, '428': {'00': '수입'}},
         '600': {'611': {'01': '생선', '02': '냉동', '04': '냉동(수입)'}, '613': {'01': '생선', '02': '냉동'},
                 '615': {'01': '생선', '02': '냉동'}, '619': {'01': '생선', '02': '냉동'}, '638': {'00': '건멸치'},
                 '639': {'01': '황태'}, '640': {'00': '건오징어'}, '641': {'00': '마른김'}, '642': {'00': '건미역'},
                 '644': {'00': '굴'}, '653': {'00': '전복'}, '654': {'01': '흰다리(수입)'}}}

productRankCode = ""


def getData(regday, itemCategoryCode, itemCode, kindCode):
    URL = BASE_URL + '&regday=' + regday + '&itemcategorycode=' + itemCategoryCode + '&itemcode=' + itemCode + '&kindcode=' + kindCode + '&productrankcode=' + str(
        productRankCode) + '&convert_kg_yn=N'
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
                print(regday, itemCategoryCode, itemCode, kindCode)
            # else:  # 구분, 날짜
            #     ths = tr.find_all('th')
            #     for i in range(2):
            #         print(ths[i].text, end="|")
            #     print()


getYearDate()

getData(dates[0])
# count = 0
# for date in dates:
#     if count > 10:
#         break
#
#     for itemCategoryCode in codes.keys():
#         for itemCode in codes[itemCategoryCode].keys():
#             for kindCode in codes[itemCategoryCode][itemCode].keys():
#                 getData(date, itemCategoryCode, itemCode, kindCode)
#     count += 1
