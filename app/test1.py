# from langchain.llms import OpenAI
# llm = OpenAI(openai_api_key="ebcaf99a3b604cdc9f85866959888aee")
# llm.predict("中国的首都是哪里")

from langchain_community.llms.tongyi import Tongyi
llm = Tongyi(dashscope_api_key="sk-5b760d34a7e84439b709a6e2a5bfd2bc")
print(llm.predict("美国的首都在哪里"))

