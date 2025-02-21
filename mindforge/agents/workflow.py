
from langgraph.graph import StateGraph, END
from state import AgentState
from agents import novabot


class Graph:
    def __init__(self):
        """Build the state graph for stock analysis."""

        self.workflow = StateGraph(AgentState)

        self.workflow.add_node("agent", novabot)
        self.workflow.set_entry_point("agent")

        self.workflow.add_edge("agent", END)

        self.app = self.workflow.compile()

    def create_app(self):
        return self.app