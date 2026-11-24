from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage, SystemMessage
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from llm import llm
from tools import get_weather, calculate, search_knowledge_base

TOOLS = [get_weather, calculate, search_knowledge_base]
llm_with_tools = llm.bind_tools(TOOLS)

SYSTEM_PROMPT = """你是一个会使用工具的助手。
规则：
1. 查询天气必须调用 get_weather；
2. 涉及数字计算必须调用 calculate，不要心算；
3. 涉及 ReAct、RAG、智能体、工具调用等概念时，调用 search_knowledge_base；
4. 工具返回 error 时，先根据错误信息修正参数再试；
5. 资料不足时直接说明，不要编造。
"""

class State(TypedDict):
    messages:Annotated[list[AnyMessage],add_messages]

def agent_node(state:State):
    messages=[SystemMessage(content=SYSTEM_PROMPT)]+state["messages"]
    response=llm_with_tools.invoke(messages)
    return {"messages":[response]}

builder=StateGraph(State)
builder.add_node("agent",agent_node)
builder.add_node("tools",ToolNode(TOOLS))

builder.add_edge(START,"agent")
builder.add_conditional_edges("agent",tools_condition)
builder.add_edge("tools","agent")

graph=builder.compile()

def run_agent(user_input:str)-> str:
    result=graph.invoke({"messages":[("user",user_input)]})
    return result["messages"][-1].content
