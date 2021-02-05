# 엠로 산학과제 - 시장가격조사

### **3. 수산물 가격정보** 크롤링

#### 1차 작업

    1. 기본 크롤링 셋팅완료
        - BeautifulSoup, Selenium (chromedriver_V.88)
    2. 검색에 필요한 날짜와 페이지 파라미터 찾음
        'searchDe','pageIndex'
    3. 1일치 자료 읽기 완료
        - 초기 BeautifulSoup를 이용해서 last Page 인덱스를 구한 후
        첫 페이지부터 끝까지 테이블 정보를 저장
        --> 하지만 하나씩 나열해놓으면 총 rows가 너무 많음