from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain import OpenAI, LLMChain, ConversationChain
from ignore import OPENAI_API_KEY
import os

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

memory = ConversationBufferMemory()

conversation = ConversationChain(
    llm=OpenAI(temperature=0),
    verbose=True,
    memory=memory,
)

while True:
    command = input()
    result = conversation.predict(input=command)
    print(result)
