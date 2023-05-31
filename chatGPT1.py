from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain import OpenAI, LLMChain, ConversationChain
from ignore import OPENAI_API_KEY
import os

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# memory = ConversationBufferMemory()

# conversation = ConversationChain(
#     llm=OpenAI(temperature=0),
#     verbose=True,
#     memory=memory,
# )
llm = OpenAI(temperature=0.9)

command = "2 it's so cute, sir.Nayeon I love you oooooooIts been 2 years and yet this song is still so iconicIncredible how I still remember the danceSending love beautiful sweetheartsCongratulations DahyunAcckk the fact ! that this music has been included in NETFLIX SERIES \"XO KITTY\" makes me so proud of my gurlsHappy Birthday Dahyun I hope you had a great day and night, and wish you all the best always. Thank you for being my idol, role model and someone for me to look up too. You and Twice helped me through a very hard time in my life, thank you. Take care always, :한국:A song that's always been goodDa-hyeon's rap is goodIt never gets bad here, it ages like wine I never get tiredTwice l love youHappy Birthday DahyunMomo is the best!I love itTwice I love themThis has to be one of the best songs ever\n\n이 글에 적힌 트와이스 멤버의 이름을 알려줘"
print(llm(command))
