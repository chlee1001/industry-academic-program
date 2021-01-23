if table is not None:
    trs = table.find_all('tr')
    # tr0~2까지 정보...

    for idx, tr in enumerate(trs):
        if idx == 0:
            ths = tr.find_all('th')
            print(ths[1].text)

        elif idx == 1:
            ths = tr.find_all('th')
            print(ths[0].text)
        elif idx == 2:
            ths = tr.find_all('th')
            print(ths[0].text, end=" ")
            print("가격")
            print(ths[1].text, end=" ")
            print("가격")
            print(ths[2].text, end=" ")
            print("가격")

        elif idx == 3:
            # print(tr)
            spans = tr.find_all('span')
            for span in spans:
                if len((span.text.split())) < 1:  # table에 가격 셀이 비어있는 경우 '-' 출력
                    print("-")
                else:
                    print(span.text.split()[0])