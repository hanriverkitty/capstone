from fastapi import FastAPI, Request, Response
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from fastapi.responses import HTMLResponse, RedirectResponse
import requests
import json
from ignore import myToken,channel_id,user_id

app = FastAPI()
client = WebClient(token=myToken)
input_message=""


def post_message(text):
    response = client.chat_postMessage(
        channel=channel_id,
        text=text
    )
    return response

@app.post("/input/")
async def post_msg(request:Request):
    data = await request.json()
    if 'challenge' in data:
        print(data['challenge'])
        return data['challenge']
   
    if data['event']['type'] == 'app_mention':
        print(data['event']['user'])
        print(data['event']['text'])
        print(data)
        if data['event']['text']:
            text_index = data['event']['text'].find('>') + 2
            global input_message
            input_message = data['event']['text'][text_index:]
            print('\n'+input_message)
            client.chat_postMessage(channel=channel_id, text=input_message)
        return RedirectResponse("https://dd52-124-111-110-113.jp.ngrok.io/link/"+input_message)
    
    return 'OK'
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

@app.get("/")
def root():
    return post_message("안녕하세요.")


@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/{name}/name")
async def say_hello(name: str):
    # post_message(myToken,"#프로젝트","안녕하세요.")

    return get_message_ts()

@app.get("/link/{text}",response_class=RedirectResponse)
def read_root(response: Response,text:str):
    return input_message
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