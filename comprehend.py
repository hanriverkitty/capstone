import pandas as pd
import boto3
import os
from iso639 import to_name, NonExistentLanguageError
from ignore import Access_key,Secret_access_key

# boto3 session 생성
session = boto3.Session(
    region_name='ap-northeast-2',
    aws_access_key_id=Access_key,
    aws_secret_access_key=Secret_access_key)
comprehend = boto3.client('comprehend', region_name='ap-northeast-2')
translate = boto3.client('translate', region_name='ap-northeast-2')
print(Access_key+"\n"+Secret_access_key)
# xlsx 파일 읽기
df = pd.read_excel('test1.xlsx')

# 전치
df = df.T

# 3행 데이터 추출
data = df.iloc[2].apply(lambda x: str(x).strip())

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
        target_lang_code = 'en'
        language_name = to_name(source_lang_code)
    except NonExistentLanguageError:
        language_name = source_lang_code
    translated_text_response = translate.translate_text(Text=str(segment),
                                                         SourceLanguageCode=source_lang_code,
                                                         TargetLanguageCode=target_lang_code)
    translated_text = translated_text_response['TranslatedText']

    # 감정 분석
    sentiment_response = comprehend.detect_sentiment(Text=translated_text_response['TranslatedText'], LanguageCode='en')

    sentiment = sentiment_response['Sentiment']
    positive = round(sentiment_response['SentimentScore']['Positive'] * 100, 2)
    negative = round(sentiment_response['SentimentScore']['Negative'] * 100, 2)
    neutral = round(sentiment_response['SentimentScore']['Neutral'] * 100, 2)
    mixed = round(sentiment_response['SentimentScore']['Mixed'] * 100, 2)

    # 결과를 리스트에 저장
    result_list.append({'Input Text': segment,
                        'Translated Text': translated_text,
                        'Detected Source Language': source_lang_code,
                        'Detected Source Language Name': language_name,
                        'Sentiment': sentiment,
                        'Positive': positive,
                        'Negative': negative,
                        'Neutral': neutral,
                        'Mixed': mixed})

# 결과를    데이터프레임으로 변환하여 xlsx 파일로 저장
result_df = pd.DataFrame(result_list)
result_dir = os.path.join(os.path.expanduser("./"), "comprehend_results")
os.makedirs(result_dir, exist_ok=True)
result_path = os.path.join(result_dir, "result_.xlsx")

if os.path.exists(result_path):
    # 파일이 이미 존재하면 파일명에 숫자를 붙여서 중복을 피한다.
    i = 1
    while os.path.exists(result_path):
        result_path = os.path.join(result_dir, "result_" + str(i) + ".xlsx")
        i += 1

result_df.to_excel(result_path, index=False)
print("Results saved at", result_path)
print("over")