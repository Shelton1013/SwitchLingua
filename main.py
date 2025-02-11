from langgraph.graph import StateGraph
from utils import generate_initial_state
from node_engine import RunSampleAgent
from node_models import AgentRunningState
class CodeSwitchingAgent:
    def __init__(self):
        self.initial_state = generate_initial_state()
        self.workflow = self._construct_graph()
        print(self.initial_state)

    def run(self):
        pass

    def _construct_graph(self):
        workflow = StateGraph(AgentRunningState)
        workflow.add_node("SampleAgent", RunSampleAgent)
        workflow.set_entry_point("SampleAgent")
        return workflow.compile()
    
    def _run(self):
        self.workflow.invoke(self.initial_state)

if __name__ == "__main__":
    agent = CodeSwitchingAgent()
    agent._run()