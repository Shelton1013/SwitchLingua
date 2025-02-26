from langgraph.graph import StateGraph
from loguru import logger
from utils import load_config, generate_scenarios
from node_engine import RunSampleAgent
from node_models import AgentRunningState
logger.add("logs/code_switching_agent.log")
class CodeSwitchingAgent:
    def __init__(self):
        self.config: dict = load_config()
        self.scenarios: list[AgentRunningState] = generate_scenarios(self.config['pre_execute'])
        self.workflow: StateGraph = self._construct_graph()
        # print(self.initial_state)

    def run(self):
        pass

    def _construct_graph(self) -> StateGraph:
        workflow = StateGraph(AgentRunningState)
        workflow.add_node("SampleAgent", RunSampleAgent)
        workflow.set_entry_point("SampleAgent")
        return workflow.compile()
    
    def run(self):
        for scenario in self.scenarios[:1]:
            logger.info(f"🤖 Running scenario: {scenario}")
            self.workflow.invoke(scenario)

if __name__ == "__main__":
    agent = CodeSwitchingAgent()
    agent.run()