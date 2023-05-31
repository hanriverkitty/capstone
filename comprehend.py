import pandas as pd
import boto3
import botocore
from iso639 import to_name, NonExistentLanguageError
import pymysql
from botocore.exceptions import ClientError

# AWS 계정 정보 입력
access_key = 'ACCESS_KEY'
secret_key = 'SECRET_KEY'
region_name = 'ap-northeast-2'

# MySQL 계정 정보 입력
mysql_host = 'host_name'
mysql_port = 'port_number'
mysql_user = 'user_name'
mysql_password = 'password'
mysql_dbname = 'dbname'

# Boto3 세션 생성
session = boto3.Session(
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name=region_name
)

comprehend = session.client('comprehend')
translate = session.client('translate')

# 엑셀 파일 읽기
df = pd.read_excel('testdate(twice_cant stop me).xlsx')

# 수정할 변수명 정의
col4_name = '댓글작성시간'
col6_name = '영상_이름'
col7_name = 'URL주소'
col8_name = '가수'
col9_name = '노래'

# 4, 6, 7열 데이터 추출
data = df.iloc[:, [3, 5, 6, 7, 8]].apply(lambda x: x.astype(str).str.strip(), axis=0)

# 번역 및 감정 분석을 위해 3열의 데이터만 따로 추출 (댓글만 진행)
comment_data = df.iloc[:, 2].apply(lambda x: str(x).strip())

# MySQL 연결
conn = pymysql.connect(
    host=mysql_host, port=mysql_port, user=mysql_user,
    password=mysql_password, db=mysql_dbname, charset='utf8mb4'
)

# 커서 생성
cursor = conn.cursor()

# 테이블 생성 쿼리
create_table_query = """
CREATE TABLE IF NOT EXISTS results (
  id INT AUTO_INCREMENT PRIMARY KEY,
  영상_이름 TEXT,
  가수 TEXT,
  노래 TEXT,
  URL주소 TEXT,
  댓글작성시간 TEXT,
  기존_댓글 TEXT,
  번역_댓글 TEXT,
  언어_코드 VARCHAR(10),
  언어_이름 VARCHAR(100),
  감정분석 VARCHAR(10),
  긍정 DOUBLE,
  부정 DOUBLE,
  중립 DOUBLE,
  혼합 DOUBLE
)
"""
#지원 언어 코드 함수
def is_language_supported(lang_code):
    supported_languages = ['af', 'am', 'ar', 'as', 'az', 'bg', 'bn', 'bs', 'ca', 'cs', 'cy', 'da', 'de', 'el', 'en',
                           'es', 'et', 'fa', 'fi', 'fil', 'fj', 'fr', 'fr-CA', 'ga', 'gu', 'he', 'hi', 'hr', 'ht',
                           'hu', 'hy', 'id', 'is', 'it', 'ja', 'ka', 'kk', 'km', 'kn', 'ko', 'ku', 'ky', 'lo', 'lt',
                           'lv', 'mg', 'mi', 'ml', 'mn', 'mr', 'ms', 'mt', 'my', 'ne', 'nl', 'no', 'ny', 'or', 'pa',
                           'pl', 'ps', 'pt', 'ro', 'ru', 'si', 'sk', 'sl', 'sm', 'sq', 'sr', 'sv', 'sw', 'ta', 'te',
                           'th', 'ti', 'tl', 'to', 'tr', 'uk', 'ur', 'vi', 'wo', 'xh', 'yo', 'zh', 'zh-TW', 'zu']
    return lang_code in supported_languages

def translate_text_with_error_handling(text, source_lang_code, target_lang_code):
    try:
        translate_response = translate.translate_text(Text=text, SourceLanguageCode=source_lang_code,
                                                     TargetLanguageCode=target_lang_code)
        translated_text = translate_response['TranslatedText']
        return translated_text
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'UnsupportedLanguagePairException':
            # 지원하지 않는 언어 코드인 경우, 무시하고 빈 문자열 반환
            return ''
        else:
            # 다른 예외 처리
            raise e
# 테이블 생성
cursor.execute(create_table_query)
conn.commit()

# 결과 저장을 위한 빈 리스트 생성
result_list = []

# 번역 및 감정 분석
for segment, col4, col6, col7, col8, col9 in zip(comment_data, data.iloc[:, 0], data.iloc[:, 1], data.iloc[:, 2], data.iloc[:, 3], data.iloc[:, 4]):
    if pd.isna(segment):
        continue
    try:
        # 번역 전 언어 감지
        source_lang_response = comprehend.detect_dominant_language(Text=str(segment))
        source_lang_code = source_lang_response['Languages'][0]['LanguageCode']

        if is_language_supported(source_lang_code):
            language_name = to_name(source_lang_code)
            # 번역
            target_lang_code = 'en'  # 영어로 번역
            translated_text = translate_text_with_error_handling(segment, source_lang_code, target_lang_code)

            if translated_text:
                # 감정 분석
                sentiment_response = comprehend.detect_sentiment(Text=translated_text, LanguageCode=target_lang_code)
                sentiment = sentiment_response['Sentiment']

                # 감정 점수 추출
                sentiment_score = sentiment_response['SentimentScore']
                positive = round(sentiment_response['SentimentScore']['Positive'] * 100, 2)
                negative = round(sentiment_response['SentimentScore']['Negative'] * 100, 2)
                neutral = round(sentiment_response['SentimentScore']['Neutral'] * 100, 2)
                mixed = round(sentiment_response['SentimentScore']['Mixed'] * 100, 2)
        
        # 기존 댓글 확인을 위한 SELECT 쿼리
        select_query = "SELECT * FROM results WHERE 기존_댓글 = %s"
        cursor.execute(select_query, segment)
        existing_data = cursor.fetchone()

        if existing_data:
            # 기존 댓글과 동일한 데이터가 이미 존재하는 경우 pass
            continue
        else:
            update_query = """
            UPDATE results SET
            영상_이름 = %s,
            가수 = %s,
            노래 = %s,
            URL주소 = %s,
            댓글작성시간 = %s,
            번역_댓글 = %s,
            언어_코드 = %s,
            언어_이름 = %s,
            감정분석 = %s,
            긍정 = %s,
            부정 = %s,
            중립 = %s,
            혼합 = %s
            WHERE 기존_댓글 = %s
            """

            # 변경된 데이터가 있을 경우 업데이트
            update_values = (col6, col8, col9, col7, col4, translated_text, source_lang_code, language_name, sentiment,
                            str(positive), str(negative), str(neutral), str(mixed), segment)
            cursor.execute(update_query, update_values)
            conn.commit()


            # 변경된 데이터가 없을 경우 새로 추가
            insert_query = """
            INSERT INTO results (영상_이름, 가수, 노래, URL주소, 댓글작성시간, 기존_댓글, 번역_댓글, 언어_코드, 언어_이름, 감정분석, 긍정, 부정, 중립, 혼합)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            # 변경된 데이터가 없을 경우 새로 추가
            insert_values = (col6, col8, col9, col7, col4, segment, translated_text, source_lang_code, language_name, sentiment,
                            str(positive), str(negative), str(neutral), str(mixed))
            cursor.execute(insert_query, insert_values)
            conn.commit()

            result_list.append((col6, col8, col9, col7, col4, segment, translated_text, source_lang_code, language_name,
                                sentiment, positive, negative, neutral, mixed))

    except NonExistentLanguageError:
        # 언어 감지 실패 시 처리할 내용
        pass
# 연결 종료
cursor.close()
conn.close()

# 결과 출력
result_df = pd.DataFrame(result_list, columns=[col6_name, col8_name, col9_name, col7_name, col4_name, '기존_댓글', '번역_댓글',
                                               '언어_코드', '언어_이름', '감정분석', '긍정', '부정', '중립', '혼합'])
print(result_df)
