
from agent.state import SalonState
from agent.build_tools import build_tools
from langgraph.prebuilt import ToolNode
from langchain_core.tools import StructuredTool


def agent(state: SalonState):
    ...

def router_agetn(state: SalonState):
    ...

def email(state: SalonState):
    ... 


def tools(tools_list: list[StructuredTool]):
    return ToolNode(tools=tools_list)
