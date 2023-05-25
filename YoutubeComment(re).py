import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from openpyxl import Workbook
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from tqdm import tqdm
import time
import re
import datetime, timedelta


# 셀레니움 옵션 설정
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
# options.add_argument('headless') # 크롬 띄우는 창 없애기
options.add_argument("window-size=1920x1080")  # 크롬드라이버 창크기
options.add_argument("disable-gpu")  # 그래픽 성능 낮춰서 크롤링 성능 쪼금 높이기
options.add_argument(
    "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
)  # 네트워크 설정
options.add_argument("lang=ko_KR")  # 사이트 주언어
driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)

wb = Workbook(write_only=True)
ws = wb.create_sheet()


data_list = []
driver.get("https://www.youtube.com/watch?v=--FmExEAsM8")

URL = "https://www.youtube.com/watch?v=--FmExEAsM8"

# 스크롤 내리기

body = driver.find_element(By.TAG_NAME, "body")
time.sleep(1)

last_height = driver.execute_script("return document.documentElement.scrollHeight")

Title = driver.find_element(By.CSS_SELECTOR, "#title > h1 > yt-formatted-string")
b = Title.text
a = b.find("'")
singer = b[:a]
sing = b[a:]
time.sleep(0.5)

uploadDatebutton = driver.find_element(By.CSS_SELECTOR, "#bottom-row")
uploadDatebutton.click()
time.sleep(1)

uploadDate = driver.find_element(By.CSS_SELECTOR, "#info > span:nth-child(3)")
time.sleep(0.5)

driver.find_element(By.TAG_NAME, "html").send_keys(Keys.PAGE_DOWN)
time.sleep(1)

driver.find_element(By.TAG_NAME, "html").send_keys(Keys.PAGE_DOWN)
time.sleep(1)

comment_raw = driver.find_elements(
    By.CSS_SELECTOR, "#count > yt-formatted-string > span:nth-child(2)"
)
time.sleep(2)

datebutton = driver.find_element(By.CSS_SELECTOR, "#icon-label")
datebutton.click()
time.sleep(1)

Recentlybutton = driver.find_element(By.CSS_SELECTOR, "#menu > a:nth-child(2)")
Recentlybutton.click()
time.sleep(1)

k = 0
while k < 50:
    k += 1
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
    time.sleep(0.5)

    new_height = driver.execute_script("return document.documentElement.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

time.sleep(0.5)

try:
    driver.find_element(By.CSS_SELECTOR, "#dismiss-button > a").click()
except:
    pass

buttons = driver.find_elements(By.CSS_SELECTOR, "#more-replies > a")

time.sleep(1.5)

for button in buttons:
    button.send_keys(Keys.ENTER)
    time.sleep(1.5)
    button.click()

html_source = driver.page_source
soup = BeautifulSoup(html_source, "html.parser")

id_list = soup.select("div#header-author > h3 > #author-text > span")
comment_list = soup.select("yt-formatted-string#content-text")
date_list = soup.select("div#header-author > yt-formatted-string > a")

id_final = []
comment_final = []
date_final = []

for i in range(len(comment_list)):
    # if detect(str(comment_list[i])) != 'en' :
    temp_id = id_list[i].text
    temp_id = temp_id.replace("\n", "")
    temp_id = temp_id.replace("\t", "")
    temp_id = temp_id.replace("    ", "")
    id_final.append(temp_id)  # 댓글 작성자

    temp_comment = comment_list[i].text
    temp_comment = temp_comment.replace("\n", "")
    temp_comment = temp_comment.replace("\t", "")
    temp_comment = temp_comment.replace("    ", "")
    comment_final.append(temp_comment)  # 댓글 내용

    recentlyDate = date_list[i].text
    if recentlyDate.find("분") >= 0:
        date_num = int(re.sub(r"[^0-9]", "", recentlyDate))
        recentlyDate = datetime.datetime.now() - datetime.timedelta(minutes=date_num)
    elif recentlyDate.find("시간") >= 0:
        date_num = int(re.sub(r"[^0-9]", "", recentlyDate))
        recentlyDate = datetime.datetime.now() - datetime.timedelta(hours=date_num)
    elif recentlyDate.find("일") >= 0:
        date_num = int(re.sub(r"[^0-9]", "", recentlyDate))
        recentlyDate = datetime.datetime.now() - datetime.timedelta(days=date_num)
    elif recentlyDate.find("주") >= 0:
        date_num = int(re.sub(r"[^0-9]", "", recentlyDate)) * 7
        recentlyDate = datetime.datetime.now() - datetime.timedelta(days=date_num)
    elif recentlyDate.find("개월") >= 0:
        date_num = int(re.sub(r"[^0-9]", "", recentlyDate)) * 30
        recentlyDate = datetime.datetime.now() - datetime.timedelta(days=date_num)
    elif recentlyDate.find("년") >= 0:
        date_num = int(re.sub(r"[^0-9]", "", recentlyDate)) * 365
        recentlyDate = datetime.datetime.now() - datetime.timedelta(days=date_num)
    temp_date = recentlyDate.strftime("%Y-%m-%d")
    # temp_date = temp_date.replace('\n', '')
    # temp_date = temp_date.replace('\t', '')
    # temp_date = temp_date.replace('    ', '')
    date_final.append(temp_date)

uploadDate = uploadDate.text
Title = Title.text


pd_data = {
    "id": id_final,
    "texts": comment_final,
    "date": date_final,
    "uploadDate": uploadDate,
    "Title": Title,
    "URL": URL,
    "singer": singer,
    "sing": sing,
}
youtube_pd = pd.DataFrame(pd_data)
youtube_pd.add
youtube_pd.to_excel("testdate.xlsx")
