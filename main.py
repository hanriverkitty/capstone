from fastapi import FastAPI, Request, Response
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from langchain.sql_database import SQLDatabase
from langchain.llms.openai import OpenAI
from langchain import SQLDatabaseChain
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain import OpenAI, ConversationChain
from ignore import myToken, channel_id, user_id, ngrok_url, OPENAI_API_KEY, sql_URL
import subprocess
import asyncio
import os
from langchain.prompts.prompt import PromptTemplate


database_template = """Given an input question, first create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
Use the following format:

Question: "Question here"
SQLQuery: "SQL Query to run"
SQLResult: "Result of the SQLQuery"
Answer: "Final answer here"

Only use the following tables:

{table_info}

results 테이블의 열은 id, URL주소, 감정분석, 긍정, 기존_댓글, 댓글작성시간, 번역_댓글, 부정, 언어_이름, 언어_코드, 가수, 노래, 중립, 혼합 , 영상이름이 있습니다
감정분석의 결과로는 긍정,부정,혼합,중립이 있습니다
가수는 아이돌그룹의 이름입니다
질문을 할때 노래들이 사용됩니다
하나의 행은 한개의 댓글입니다
댓글내용은 기존_댓글 열을 의미합니다
번역댓글은 번역_댓글 열을 의미합니다
언어는 언어_이름 열을 의미합니다
모든 답변은 중복을 허락하지 않습니다
결과값이 많을 경우 한줄씩 출력해주세요

Question: {input}
"""
PROMPT = PromptTemplate(
    input_variables=["input", "table_info", "dialect"], template=database_template
)

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

client = WebClient(token=myToken)
is_run = False
database_connected = False


# html 파일 연결
@app.get("/html", response_class=HTMLResponse)
async def show_html(request: Request):
    return templates.TemplateResponse("js_test.html", {"request": request})


# slack에 메시지 보내기
def post_message(text):
    response = client.chat_postMessage(channel=channel_id, text=text)
    return response


# slack에서 보낸 메시지를 읽음
@app.post("/input/")
async def post_msg(request: Request):
    global is_run, database_connected, db_chain, group_name
    data = await request.json()
    # print(data)
    print(is_run)
    if "challenge" in data:
        print(data["challenge"] + "\n\n\n\n")
        return data["challenge"]

    # slack 봇이 언급되었는지 여부
    if (
        data["event"]["type"] == "app_mention"
        and data["event"]["user"] == "U04UQCS77J8"
    ):
        if is_run == False:
            # print(data["event"]["user"])
            # print(data["event"]["text"])
            # print(data)
            if data["event"]["text"]:
                text_index = data["event"]["text"].find(">") + 2
                input_message = data["event"]["text"][text_index:]
                # print("\n" + input_message)
                # while event_handler_running:
                #     time.sleep(1)
                # event_handler_running = True
                # client.chat_postMessage(channel=channel_id, text="https://www.youtube.com/results?search_query="+input_message)
                # search_url = "https://www.youtube.com/results?search_query="+input_message
                # client.chat_postMessage(
                #     channel=channel_id, text=input_message + " 그룹의 댓글 감정분석 결과를 알려드리겠습니다"
                # )
                # event_handler_running = False
                # subprocess.call("YoutubeComment.py",shell=True)
                # asyncio.create_task(run_youtube_comment())
                if input_message == "검색":
                    group_name = "검색"
                    print("검색")
                    is_run = True
                    asyncio.create_task(start_gpt())
                    return Response(status_code=200, content="HTTP 200 OK")

            return Response(status_code=200, content="HTTP 200 OK")
        elif is_run == True:
            if data["event"]["text"]:
                text_index = data["event"]["text"].find(">") + 2
                input_message = data["event"]["text"][text_index:]
                # print("\n" + input_message)
                asyncio.create_task(communication_gpt(input_message))
                # print(data["event"]["user"])
                # print(data["event"]["text"])
                # print(data)

                # while True:
                #     command = input()
                #     if command == "종료":
                #         is_run=False
                #         database_connected=False
                #         break
                #     a = db_chain.run(command)
                #     print(a)
                return Response(status_code=200, content="HTTP 200 OK")

    # RedirectResponse(ngrok_url+input_message)
    return Response(status_code=200, content="HTTP 200 OK")
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


async def communication_gpt(input_message):
    global db_chain, is_run, conversation
    input_message = input_message.lstrip()

    print("communication_gpt")
    if input_message == "종료":
        is_run = False
        client.chat_postMessage(channel=channel_id, text="대화를 종료합니다")
        return
    if input_message[0] == "1":
        input_message = input_message[1:].lstrip()
        answer = db_chain.run(input_message)
        client.chat_postMessage(channel=channel_id, text=answer)
    elif input_message[0] == "2":
        input_message = input_message[1:].lstrip()
        answer = conversation.predict(input=input_message)
        client.chat_postMessage(channel=channel_id, text=answer)
    else:
        client.chat_postMessage(channel=channel_id, text="번호를 붙여주세요")

    return


async def start_gpt():
    global is_run, database_connected, db, db_chain, llm, conversation
    is_run = True
    db = SQLDatabase.from_uri(sql_URL)
    llm = OpenAI(temperature=0)
    db_chain = SQLDatabaseChain.from_llm(llm, db, prompt=PROMPT, verbose=True)

    memory = ConversationBufferMemory()

    conversation = ConversationChain(
        llm=OpenAI(temperature=0),
        verbose=True,
        memory=memory,
    )

    client.chat_postMessage(
        channel=channel_id,
        text='두 가지 유형으로 질문이 가능합니다.\n1. 유튜브 댓글기반 검색\n2. GPT를 통한 검색\n원하시는 질문 앞에 번호를 붙여주세요.\n종료를 원하시면 "종료"를 입력해주세요.',
    )


async def run_youtube_comment():
    subprocess.call("YoutubeComment.py", shell=True)
    subprocess.call("comprehend.py", shell=True)
    client.chat_postMessage(channel=channel_id, text="감정분석의 결과가 만들어졌습니다")
    return


@app.get("/name")
async def say_hello():
    # post_message(myToken,"#프로젝트","안녕하세요.")

    return get_message_ts()


@app.get("/link/{text}")
def read_root(response: Response, text: str):
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
        if i["id"] == channel_id:
            result = i
    message = []
    message_obj = client.conversations_history(channel=channel_id)
    message = message_obj["messages"]
    message_total = []
    for i in message:
        if i["user"] == user_id:
            message_total.append(i["text"])

    print(message)
    print(result)
    return message_total
