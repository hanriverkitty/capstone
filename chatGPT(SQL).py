from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.llms.openai import OpenAI
from langchain.agents import AgentExecutor
from langchain.chains import SQLDatabaseSequentialChain
from langchain import SQLDatabaseChain
from langchain.chains import SQLDatabaseSequentialChain
from sqlalchemy import create_engine
import pymysql
import os
from ignore import OPENAI_API_KEY, sql_URL

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# connection = pymysql.connect(
#     host="",
#     port=,
#     user="",
#     password="",
#     database="",
#     charset="utf8",
# )

# engine = create_engine(
#     "sql_URL"
# )
# conn = engine.connect()


db = SQLDatabase.from_uri(sql_URL)
llm = OpenAI(temperature=0)
db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)
command = ""
while True:
    command = input()
    if command == "종료":
        break
    a = db_chain.run(command)
    print(a)
