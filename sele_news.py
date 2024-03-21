import time
import pymysql
from selenium.webdriver import ChromeOptions
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ.get('DB_HOST')
# DB_PORT = os.environ.get('DB_PORT')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_DATABASE = os.environ.get('DB_DATABASE')

# MySQL 연결 설정
db = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE) # 사용 DB 지정 / 필요시 port=DB_PORT 추가
cursor = db.cursor() # DB와 연결된 커서 객체 생성

# 테이블 생성
create_table_query = '''
CREATE TABLE IF NOT EXISTS selenews (
    idx INT AUTO_INCREMENT PRIMARY KEY,
    image_url TEXT,
    title VARCHAR(255),
    url VARCHAR(255)
);
'''
# SQL 쿼리 실행
cursor.execute(create_table_query)

# 브라우저 꺼짐 방지 옵션
options = ChromeOptions()
options.add_experimental_option("detach", True)

# 불필요한 에러 메시지 삭제
options.add_experimental_option("excludeSwitches", ["enable-logging"])

# 크롬 드라이버 최신 버전 설정
service = ChromeService(ChromeDriverManager().install())

# 웹 드라이버 설정
driver = webdriver.Chrome(service=service, options=options)

url = 'https://www.naver.com'
driver.get(url)
time.sleep(2)

# 검색창에 '탄소중립' 입력
driver.find_element(By.ID, 'query').send_keys("탄소중립")
time.sleep(2)

# 검색 버튼 클릭(엔터 누르기)
# driver.find_element(By.CLASS_NAME, 'btn_search').send_keys(Keys.ENTER)
driver.find_element(By.CLASS_NAME, 'btn_search').click()
time.sleep(2)

# 뉴스 탭으로 이동
driver.find_element(By.XPATH, '//*[@id="lnb"]/div[1]/div/div[1]/div/div[1]/div[1]/a').click()
time.sleep(2)

# 스크롤 내리기(이미지 로딩)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

all_news = driver.find_elements(By.CLASS_NAME, 'news_contents')

for news in all_news:
    title = news.find_element(By.CLASS_NAME, 'news_tit').text
    url = news.find_element(By.CLASS_NAME, 'news_tit').get_attribute('href')
    try:
        image_element = driver.find_element(By.CLASS_NAME, "thumb")
        image_url = image_element.get_attribute('src')
    except:
        pass
    
    # 데이터 삽입 쿼리 실행
    insert_query = "INSERT INTO selenews (title, url, image_url) VALUES (%s, %s, %s);"
    cursor.execute(insert_query, (title, url, image_url))

driver.quit()

# DB 변경사항 저장
db.commit()

# 커서 및 연결 종료
cursor.close()
db.close()

