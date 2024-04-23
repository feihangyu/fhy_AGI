from operator import itemgetter
# from  modelscope_agent.agent_types import AgentType
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_community.utilities import SQLDatabase
import os
os.environ["DASHSCOPE_API_KEY"] = "sk-5b760d34a7e84439b709a6e2a5bfd2bc"
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain.chains import LLMChain, create_sql_query_chain
from langchain_core.prompts import PromptTemplate
from langchain_community.llms.tongyi import Tongyi
from langchain_core.pydantic_v1 import BaseModel

# pg_dev
connection_string = (
    "postgresql+psycopg2://anvelink:Xiaoan123@pgm-wz93yqidbgm11r5feo.pg.rds.aliyuncs.com:5432/vectordb"
)

# 使用 from_uri 方法创建 SQLDatabase 实例
db = SQLDatabase.from_uri(connection_string)
llm = Tongyi()
chain = create_sql_query_chain(llm,db)

# 1、生成sql语句
response = chain.invoke({"question": "查询表xa_ads_day_service_pay_order_count_llm的数据量"})
print(response)

# 2、执行sql语句
execute_query = QuerySQLDataBaseTool(db=db)
chain2 = chain | execute_query
response2 = chain2.invoke({"question": "查询表xa_ads_day_service_pay_order_count_llm的数据量,只要sql语句"})
print(response2)

# 3、采用提示词模板，规范输入和输出
answer_prompt = PromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, and SQL result, answer the user question.
Question: {question}
SQL Query: {query}
SQL Result: {result}
Answer: """
)

answer = answer_prompt | llm | StrOutputParser()
chain3 = (
        RunnablePassthrough.assign(query=chain).assign(
            result=itemgetter("query") | execute_query
        )
        | answer
)

response3 = chain3.invoke({"question": "查询表xa_ads_day_service_pay_order_count_llm的数据量,只要sql语句"})
print(response3)

# 4、使用agent
from langchain.agents import load_tools, BaseSingleActionAgent, AgentExecutor
from langchain.agents import initialize_agent
from langchain.agents import AgentType
os.environ["SERPAPI_API_KEY"] = "90027a8908012eda4e5a2e548cae5ba3c8d8d741a94753750a0c1859c1b43643"

tools = load_tools(["serpapi", "llm-math"], llm=llm)
# 使用ReAct框架，来抉择使用什么工具，这个抉择的标准是基于对于每一个tool的描述决定的
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
agent.run("Who is Leo DiCaprio's girlfriend? What is her current age raised to the 0.43 power?")

print('5、自定义agent')
# 5、自定义agent
from typing import List, Tuple, Any, Union
from langchain.schema import AgentAction, AgentFinish
class FakeAgent(BaseSingleActionAgent):
    @property
    def input_keys(self):
        return ["input"]

    def plan(
            self, intermediate_steps: List[Tuple[AgentAction, str]], **kwargs: Any
    ) -> Union[AgentAction, AgentFinish]:

        return AgentAction(tool="Search", tool_input=kwargs["input"], log="")
    async def aplan(
            self, intermediate_steps: List[Tuple[AgentAction, str]], **kwargs: Any
    ) -> Union[AgentAction, AgentFinish]:
        return AgentAction(tool="Search", tool_input=kwargs["input"], log="")

agent = FakeAgent()

agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True)

agent_executor.run("How many people live in canada as of 2023?")



# ###############################
#
# agent_executor = create_sql_agent(llm, db=db, agent_type="zero-shot-react-description", verbose=True)
#
# response4 = agent_executor.invoke(
#     "查询表xa_ads_day_service_pay_order_count_llm的数据量,只要sql语句"
# )
# print(response4)

# Large database
# class Table(BaseModel):
#     """Table in SQL database."""
#
#     name: str = Field(description="Name of table in SQL database.")
#


# execute_query = QuerySQLDataBaseTool(db=db)

# chain = create_sql_query_chain(llm,db) | execute_query

#
# res = chain.invoke({"question": "查询表xa_ads_day_service_pay_order_count_llm的数据量"})
# print(res)

# print(db.run(res))

# # 定义处理函数，提取 SQL 查询语句
# def process_output(output):
#     # 提取 SQL 查询语句
#     # sql_query = output.split(": ")[-1]
#     sql_query = output.splitlines()[0]
#     return sql_query
#
# # 使用 RunnableLambda 创建自定义处理器
# output_processor = RunnableLambda(process_output)
#
# # 将自定义处理器添加到链中
# chain = chain | output_processor
#
# # 调用 SQL 查询链并传入输入参数
# res = chain.invoke({"question": "查询表qa_sql的数据量"})
#
# # 打印输出结果的 SQL 查询语句
# print(res)
# sql_result = db.run(res)
# print("结果是:"+sql_result)



