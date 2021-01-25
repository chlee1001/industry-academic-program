from pymongo import MongoClient

# mongodb 연결객체 생성
client = MongoClient('주소')
db = client.EKAPEPIA

# beef = {'Species': '소'}
# fork = {'Species': '돼지'}
# chicken = {'Species': '닭'}
# egg = {'Species': '계란'}
# duck = {'Species': '오리'}

species_id = ['소', '돼지', '닭', '계란', '오리']

sample_data = '2020-01-03'  # 날짜는 받아오고..
sample_price_list = ['-', '-', '-', '-', '-', '-', '-']

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


if bool(db.allDatas.find_one({'Species': species_id[1]})):
    print(scheme(0, sample_data, sample_price_list))

    db.allDatas.update(
        {'Species': species_id[1]},
        {"$set": scheme(0, sample_data, sample_price_list)})
    print("Complete Update")
else:

    db.allDatas.insert_one(scheme(1, sample_data, sample_price_list))
    print("Complete Insert")
