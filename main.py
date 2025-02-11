from langgraph.graph import StateGraph
from utils import generate_initial_state
from node_engine import SampleAgent
class CodeSwitchingAgent:
    def __init__(self):
        self.initial_state = generate_initial_state()

    def run(self):
        pass

    def _construct_graph(self):
        workflow = StateGraph()
        workflow.add_node("SampleAgent", SampleAgent)
        workflow.set_entry_point("SampleAgent")
        print(self.initial_state)
        return workflow.compile()
    
    def _run(self):
        self._construct_graph().invoke(self.initial_state)

if __name__ == "__main__":
    agent = CodeSwitchingAgent()
    agent._run()