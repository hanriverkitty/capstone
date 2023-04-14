import pandas as pd
import schedule
from bs4 import BeautifulSoup
from selenium import webdriver
from openpyxl import Workbook
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from tqdm import tqdm
import time
import re
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException


# 셀레니움 옵션 설정
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches',['enable-logging'])
# options.add_argument('headless') # 크롬 띄우는 창 없애기
options.add_argument('window-size=1920x1080') # 크롬드라이버 창크기
options.add_argument("disable-gpu") #그래픽 성능 낮춰서 크롤링 성능 쪼금 높이기
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36") # 네트워크 설정
options.add_argument("lang=ko_KR") # 사이트 주언어
driver = webdriver.Chrome(ChromeDriverManager().install(),
    chrome_options=options)

wb = Workbook(write_only=True)
ws = wb.create_sheet()


data_list = []
driver.get("https://www.youtube.com/watch?v=11cta61wi0g")

# 스크롤 내리기

body = driver.find_element(By.TAG_NAME,'body')
time.sleep(5)

last_height = driver.execute_script("return document.documentElement.scrollHeight")

driver.find_element(By.TAG_NAME,'html').send_keys(Keys.PAGE_DOWN)
time.sleep(5)

comment_raw = driver.find_elements(By.CSS_SELECTOR,"#count > yt-formatted-string > span:nth-child(2)")
time.sleep(2)

datebutton = driver.find_element(By.CSS_SELECTOR,'#icon-label')
datebutton.click()
time.sleep(5)
Recentlybutton =  driver.find_element(By.CSS_SELECTOR,'#menu > a:nth-child(2) > tp-yt-paper-item > tp-yt-paper-item-body > div.item.style-scope.yt-dropdown-menu')
Recentlybutton.click()
time.sleep(5)


while True:
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
    time.sleep(1.5)

    new_height = driver.execute_script("return document.documentElement.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

time.sleep(1.5)

try:
    driver.find_element(By.CSS_SELECTOR,'#dismiss-button > a').click()
except:
    pass

buttons = driver.find_elements(By.CSS_SELECTOR,'#more-replies > a')

time.sleep(1.5)

for button in buttons:
    button.send_keys(Keys.ENTER)
    time.sleep(1.5)
    button.click()

html_source = driver.page_source
soup = BeautifulSoup(html_source, 'html.parser')

id_list = soup.select("div#header-author > h3 > #author-text > span")
comment_list = soup.select("yt-formatted-string#content-text")
date_list = soup.select("div#header-author > yt-formatted-string > a") 

id_final = []
comment_final = []
date_final = []

for i in range(len(comment_list)):
    
    
    #if detect(str(comment_list[i])) != 'en' :
        temp_id = id_list[i].text
        temp_id = temp_id.replace('\n', '')
        temp_id = temp_id.replace('\t', '')
        temp_id = temp_id.replace('    ', '')
        id_final.append(temp_id) # 댓글 작성자

        temp_comment = comment_list[i].text
        temp_comment = temp_comment.replace('\n', '')
        temp_comment = temp_comment.replace('\t', '')
        temp_comment = temp_comment.replace('    ', '')
        comment_final.append(temp_comment) # 댓글 내용

        temp_date = date_list[i].text
        temp_date = temp_date.replace('\n', '')
        temp_date = temp_date.replace('\t', '')
        temp_date = temp_date.replace('    ', '')
        #temp_date = datetime.strptime(temp_date, '%Y-%m-%d').date()
        date_final.append(temp_date)


pd_data = {"id" : id_final , "texts" : comment_final,  "date" : date_final}
youtube_pd = pd.DataFrame(pd_data)
youtube_pd.to_excel('test1.xlsx')