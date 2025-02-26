import asyncio
from langgraph.graph import StateGraph
from loguru import logger
from utils import load_config, generate_scenarios
from node_engine import RunSampleAgent
from node_models import AgentRunningState

logger.add("logs/code_switching_agent.log")


class CodeSwitchingAgent:
    def __init__(self):
        self.config: dict = load_config()
        self.scenarios: list[AgentRunningState] = generate_scenarios(
            self.config["pre_execute"]
        )
        self.workflow: StateGraph = self._construct_graph()
        # print(self.initial_state)

    def _construct_graph(self) -> StateGraph:
        workflow = StateGraph(AgentRunningState)
        workflow.add_node("SampleAgent", RunSampleAgent)
        workflow.set_entry_point("SampleAgent")
        return workflow.compile()

    async def run(self):
        async def run_scenario(scenario):
            logger.info(f"🤖 Running scenario: {scenario}")
            try:
                return await asyncio.wait_for(
                    self.workflow.ainvoke(scenario), timeout=10
                )
            except asyncio.TimeoutError:
                logger.warning(f"⏱️ Scenario timed out after 10 seconds: {scenario}")
                return ""

        tasks = [run_scenario(scenario) for scenario in self.scenarios[:50]]
        results = await asyncio.gather(*tasks)
        return results


if __name__ == "__main__":
    agent = CodeSwitchingAgent()
    asyncio.run(agent.run())
