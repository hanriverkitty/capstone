from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain import OpenAI, LLMChain, PromptTemplate

template = """나는 초보 프로그래머야.
{chat_history}
Human: {question}
AI:
"""
prompt_template = PromptTemplate(
    input_variables=["chat_history", "question"], template=template
)
memory = ConversationBufferMemory(memory_key="chat_history")

llm_chain = LLMChain(
    llm=OpenAI(),
    prompt=prompt_template,
    verbose=True,
    memory=memory,
)

llm_chain.predict(question="어떤것을 공부해야될까?")

result = llm_chain.predict(question="백엔드 프로그래머가 뭐야?")
print(result)
