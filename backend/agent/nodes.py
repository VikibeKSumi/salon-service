from datetime import datetime
from zoneinfo import ZoneInfo
import json

from langgraph.prebuilt import ToolNode
from langgraph.graph import END
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import StructuredTool
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import ToolMessage
from langchain_core.runnables import Runnable

from agent.state import SalonState
from agent.build_tools import build_tools
from agent.prompt import AGENT_SYSTEM_PROMPT


class NodeBuild():
    def __init__(
            self,
            llm:BaseChatModel,
            tools_list: list[StructuredTool]
        ):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", AGENT_SYSTEM_PROMPT),
            MessagesPlaceholder("history")
        ])
        self.tools_list = tools_list
        self.llm_with_tools: Runnable = llm.bind_tools(tools=self.tools_list)
        self.chain = self.prompt | self.llm_with_tools

    def agent(self, state: SalonState):
        messages = state.get("messages", [])
        last = messages[-1]

        next_node = END #for generic 

        #response = llm_tools.invoke(input=prompt.invoke(input={"history": messages}))
        now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
        today_date = now.isoformat()
        today_day = now.strftime("%A")

        response = self.chain.invoke(
            {
                "history": messages,
                "today_date": today_date,
                "today_day": today_day
        })

        booking_info = None
        customer_info = None
        if response.tool_calls:
            next_node = "tools_node"
        elif isinstance(last, ToolMessage) and last.name == "create_bookings":
            result = json.loads(last.content)
            if result.get("success"):
                next_node = "email_node"
                booking_info = result["payload"]
            
        return {
            #accumulator
            "messages": [response],
            #router
            "next_node": next_node,
            #payload
            "booking_info": booking_info,
            #explanation
            "agent_response": "This is agent response",
        }

    def email(self, state: SalonState):
        ... 


    def tools(self):
        return ToolNode(tools=self.tools_list)
