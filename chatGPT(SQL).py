from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.llms.openai import OpenAI
from langchain.agents import AgentExecutor
from langchain.chains import SQLDatabaseSequentialChain
from langchain import SQLDatabaseChain
from langchain.chains import SQLDatabaseSequentialChain
from sqlalchemy import create_engine

engine = create_engine(
    "mysql+pymysql://[id]:[pw]@[mysql주소]:[port]/[db_name]?charset=utf8",
    encoding="utf-8",
)
conn = engine.connect()


db = SQLDatabase.from_uri("sqlite:///../../../../notebooks/Chinook.db")
llm = OpenAI(temperature=0)
db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)
chain = SQLDatabaseSequentialChain.from_llm(llm, db, verbose=True)

db_chain.run("How many employees are there?")
