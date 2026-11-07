from langgraph.graph import StateGraph, START, END
from langchain_core.tools import StructuredTool
from langgraph.checkpoint.memory import InMemorySaver
from agent.state import SalonState
from agent.nodes import (
    agent, email, tools, router_agent
)

class SalonAgent():

    def __init__(
            self,
            tools_list: list[StructuredTool]
        ):
        self.workflow = StateGraph(SalonState)
        self.tools_list = tools_list

    def create_nodes(self):
        self.workflow.add_node("agent_node", agent)
        self.workflow.add_node("email_node", email)
        self.workflow.add_node("tools_node", tools(tools_list=self.tools_list))

    def create_edges(self):
        self.workflow.add_edge(START, "agent_node")
        self.workflow.add_conditional_edges(
            "agent_node",
            router_agent,
            {
                "tools_node": "tools_node",
                "email_node": "email_node",
                END: END
            }
        )
        self.workflow.add_edge("tools_node", "agent_node")
        self.workflow.add_edge("email_node", END)


    def build_graph(self):
        return self.workflow.compile(checkpointer=InMemorySaver)

    def get_graph(self):
        self.create_nodes()
        self.create_edges()
        graph = self.build_graph()
        return graph
