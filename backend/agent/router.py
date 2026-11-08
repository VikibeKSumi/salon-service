from agent.state import SalonState

def router_agent(state: SalonState):
        next = state.get("next_node", "")
        return next