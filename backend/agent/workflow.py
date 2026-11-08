from langgraph.graph import StateGraph, START, END
from langchain_core.language_models import BaseChatModel
from langgraph.checkpoint.memory import InMemorySaver
from agent.state import SalonState
from agent.nodes import NodeBuild
from agent.router import router_agent
from agent.build_tools import build_tools
from capability_services.capability_services import CapabilityService

class SalonAgent():

    def __init__(
            self,
            capability_service: CapabilityService,
            llm: BaseChatModel
        ):
        self.workflow = StateGraph(SalonState)
        self.capability_service = capability_service
        self.node_build = NodeBuild(llm=llm, tools_list=self.get_tools_list())

    def get_tools_list(self):
        return build_tools(capability_service=self.capability_service, agent_name="salon_service_agent")
    
    def create_nodes(self):
        self.workflow.add_node("agent_node", self.node_build.agent)
        self.workflow.add_node("email_node", self.node_build.email)
        self.workflow.add_node("tools_node", self.node_build.tools())

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
        return self.workflow.compile(checkpointer=InMemorySaver())

    def get_graph(self):
        self.create_nodes()
        self.create_edges()
        graph = self.build_graph()
        return graph
