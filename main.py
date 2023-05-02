from fastapi import FastAPI, Request, Response, status
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from fastapi.responses import HTMLResponse, RedirectResponse
import requests
import json
from ignore import myToken,channel_id,user_id, ngrok_url
import subprocess
import time
import asyncio

app = FastAPI()
client = WebClient(token=myToken)


#slack에 메시지 보내기
def post_message(text):
    response = client.chat_postMessage(
        channel=channel_id,
        text=text
    )
    return response

#slack에서 보낸 메시지를 읽음
@app.post("/input/")
async def post_msg(request:Request):
    data = await request.json()
    print(data)
    if 'challenge' in data:
        print(data['challenge']+"\n\n\n\n")
        return Response(status_code=200,content="HTTP 200 OK")

   #slack 봇이 언급되었는지 여부
    if data['event']['type'] == 'app_mention' and data['event']['user']=='U04UQCS77J8':
        print(data['event']['user'])
        print(data['event']['text'])
        print(data)
        if data['event']['text']:
            text_index = data['event']['text'].find('>') + 2
            input_message = data['event']['text'][text_index:]
            print('\n'+input_message)
            # while event_handler_running:
            #     time.sleep(1)
            # event_handler_running = True
            #client.chat_postMessage(channel=channel_id, text="https://www.youtube.com/results?search_query="+input_message)
            # search_url = "https://www.youtube.com/results?search_query="+input_message
            client.chat_postMessage(channel=channel_id,text=input_message)
            # event_handler_running = False
            #subprocess.call("YoutubeComment.py",shell=True)
            asyncio.create_task(run_youtube_comment())
        return Response(status_code=200,content="HTTP 200 OK")
    
    #RedirectResponse(ngrok_url+input_message)
    return Response(status_code=200,content="HTTP 200 OK")
    event = data["event"]
    if event["type"] == "message":
        text = event["text"]
        channel = event["channel"]
        user = event["user"]
        # 이벤트 처리 로직 작성

        try:
            response = client.chat_postMessage(channel=channel_id, text="메시지를 받았습니다!")
        except SlackApiError as e:
            print("Error sending message: {}".format(e))
    return {"ok": True}


async def run_youtube_comment():
    subprocess.call("YoutubeComment.py", shell=True)


@app.get("/name")
async def say_hello():
    # post_message(myToken,"#프로젝트","안녕하세요.")

    return get_message_ts()

@app.get("/link/{text}")
def read_root(response: Response,text:str):
    return text
    response.headers["target"] = "_blank"
    return text
    '''
    html_content = """
    <html>
        <body>
            <p>Click <a href="&{input_message}" target="_blank">here</a> to open Google in a new tab.</p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)
    '''
    
def get_message_ts():
        """
        슬랙 채널 내 메세지 조회
        """
        response = client.conversations_list()
        conversations = response["channels"]
        # conversations_history() 메서드 호출
        # result = self.client.conversations_history(channel=channel_id)
        # 채널 내 메세지 정보 딕셔너리 리스트
        # messages = result.data['messages']
        # 채널 내 메세지가 query와 일치하는 메세지 딕셔너리 쿼리
        # message = list(filter(lambda m: m["text"]==query, messages))[0]
        # 해당 메세지ts 파싱
        # message_ts = message["ts"]\
        for i in conversations:
           
            if i['id']==channel_id:
                result = i
        message=[]
        message_obj = client.conversations_history(channel=channel_id)
        message =  message_obj["messages"]
        message_total = []
        for i in message:
            if i['user']==user_id:
                message_total.append(i['text'])
            
        print(message)
        print(result)
        return message_total