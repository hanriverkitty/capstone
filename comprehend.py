import pandas as pd
import boto3
import os
from iso639 import to_name, NonExistentLanguageError
import pymysql

# AWS 계정 정보 입력
access_key = 'accesskey'
secret_key = 'secretkey'
region_name = 'region'

# MySQL 계정 정보 입력
mysql_host = 'localhost'
mysql_port = 3306
mysql_user = 'user'
mysql_password = 'password'
mysql_dbname = 'dbname'

# boto3 session 생성
session = boto3.Session(
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name=region_name
)

comprehend = session.client('comprehend')
translate = session.client('translate')

# xlsx 파일 읽기
df = pd.read_excel('test1.xlsx')

# 전치
#df = df.T
# 3행 데이터 추출
data = df.iloc[:, 2].apply(lambda x: str(x).strip())

# MySQL 연결
conn = pymysql.connect(host=mysql_host, port=mysql_port, user=mysql_user,
                       password=mysql_password, db=mysql_dbname, charset='utf8mb4')
cursor = conn.cursor()
print("sql connected")
# 테이블 생성 쿼리
create_table_query = """
CREATE TABLE IF NOT EXISTS results (
  id INT AUTO_INCREMENT PRIMARY KEY,
  기존_댓글 TEXT,
  번역_댓글 TEXT,
  언어_코드 VARCHAR(10),
  언어_이름 VARCHAR(100),
  감정분석 VARCHAR(10),
  긍정 FLOAT(4),
  부정 FLOAT(4),
  중립 FLOAT(4),
  혼합 FLOAT(4)
)
"""
print("table create")
cursor.execute(create_table_query)

# 결과 저장을 위한 빈 리스트 생성
result_list = []

# 번역 및 감정 분석
for segment in data:
    if pd.isna(segment):
        continue
    try:
        # 번역 전 언어 감지
        source_lang_response = comprehend.detect_dominant_language(Text=str(segment))
        source_lang_code = source_lang_response['Languages'][0]['LanguageCode']
        target_lang_code = 'ko'
        language_name = to_name(source_lang_code)
        if source_lang_code == 'ug':
            continue
    except NonExistentLanguageError:
        # 해당 언어가 지원되지 않으므로 무시하고 다음 데이터 처리
        continue

    translated_text_response = translate.translate_text(Text=str(segment),
                                                         SourceLanguageCode=source_lang_code,
                                                         TargetLanguageCode=target_lang_code)
    translated_text = translated_text_response['TranslatedText']
    
    # 감정 분석
    sentiment_response = comprehend.detect_sentiment(Text=translated_text_response['TranslatedText'], LanguageCode='ko')

    sentiment = sentiment_response['Sentiment']
    positive = round(sentiment_response['SentimentScore']['Positive'] * 100, 2)
    negative = round(sentiment_response['SentimentScore']['Negative'] * 100, 2)
    neutral = round(sentiment_response['SentimentScore']['Neutral'] * 100, 2)
    mixed = round(sentiment_response['SentimentScore']['Mixed'] * 100, 2)
    
    # 결과를 리스트에 저장
    result_list.append({'기존_댓글': segment,
                        '번역_댓글': translated_text,
                        '언어_코드': source_lang_code,
                        '언어_이름': language_name,
                        '감정분석': sentiment,
                        '긍정': positive,
                        '부정': negative,
                        '중립': neutral,
                        '혼합': mixed})
    
    # 결과를 MySQL DB에 저장
    query = f"INSERT INTO results (기존_댓글, 번역_댓글, 언어_코드, 언어_이름, 감정분석, 긍정, 부정, 중립, 혼합) VALUES (\"{segment}\", \"{translated_text}\", \"{source_lang_code}\", \"{language_name}\", \"{sentiment}\", \"{positive}\", \"{negative}\", \"{neutral}\", \"{mixed}\")"

    try:
        cursor.execute(query)
        conn.commit()
    except Exception as e:
        print(e)
        conn.rollback()
        
    # MySQL DB의 결과 추출
    select_query = "SELECT * FROM results"
    cursor.execute(select_query)
    result = cursor.fetchall()

    # 추출한 결과를 DataFrame으로 변환
    df = pd.DataFrame(list(result), columns=['id', '기존_댓글', '번역_댓글', '언어_코드', '언어_이름', '감정분석', '긍정', '부정', '중립', '혼합'])

    # csv 파일로 저장
    df.to_csv('result1.csv', index=False)

# MySQL 연결 종료
cursor.close()
conn.close()
print("over")