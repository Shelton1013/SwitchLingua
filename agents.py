import asyncio
from langgraph.graph import StateGraph, START, END
from loguru import logger
from utils import load_config, generate_scenarios
from node_engine import (
    RunSampleAgent,
    RunUseToolsAgent,
    RunDataGenerationAgent,
    RunUseToolsAgent,
    SummarizeResult,
    RunFluencyAgent,
    RunNaturalnessAgent,
    RunCSRatioAgent,
    RunSocialCulturalAgent,
    RunRefinerAgent,
    AcceptanceAgent,
)
from node_models import AgentRunningState
import random

logger.add("logs/code_switching_agent.log")


def meet_criteria(state: AgentRunningState):
    if state["score"] < 8:
        return "Refiner"
    else:
        return "AcceptanceAgent"


class CodeSwitchingAgent:
    def __init__(self):
        self.config: dict = load_config()
        self.scenarios: list[AgentRunningState] = generate_scenarios(
            self.config["pre_execute"]
        )
        self.workflow: StateGraph = self._construct_graph()
        self.workflow_with_data_generation: StateGraph = (
            self._construct_graph_with_data_generation()
        )
        # print(self.initial_state)

    def _construct_graph(self) -> StateGraph:
        workflow = StateGraph(AgentRunningState)
        workflow.add_node("SampleAgent", RunSampleAgent)
        workflow.add_node("UseToolsAgent", RunUseToolsAgent)
        # workflow.set_entry_point("SampleAgent")
        workflow.add_edge(START, "SampleAgent")
        workflow.add_edge(START, "UseToolsAgent")
        workflow.add_edge("SampleAgent", END)
        workflow.add_edge("UseToolsAgent", END)
        return workflow.compile()

    def _construct_graph_with_data_generation(self) -> StateGraph:
        workflow = StateGraph(AgentRunningState)
        workflow.add_node("DataGenerationAgent", RunDataGenerationAgent)
        workflow.add_node("FluencyAgent", RunFluencyAgent)
        workflow.add_node("NaturalnessAgent", RunNaturalnessAgent)
        workflow.add_node("CSRatioAgent", RunCSRatioAgent)
        workflow.add_node("SocialCulturalAgent", RunSocialCulturalAgent)
        workflow.add_node("SummarizeResult", SummarizeResult)
        workflow.add_node("RefinerAgent", RunRefinerAgent)
        workflow.add_node("AcceptanceAgent", AcceptanceAgent)
        # workflow.add_node("NewsGenerationAgent", RunUseToolsAgent)
        workflow.add_edge(START, "DataGenerationAgent")
        # workflow.add_edge(START, "NewsGenerationAgent")
        workflow.add_edge("DataGenerationAgent", "FluencyAgent")
        workflow.add_edge("DataGenerationAgent", "NaturalnessAgent")
        workflow.add_edge("DataGenerationAgent", "CSRatioAgent")
        workflow.add_edge("DataGenerationAgent", "SocialCulturalAgent")
        workflow.add_edge(
            ["FluencyAgent", "NaturalnessAgent", "CSRatioAgent", "SocialCulturalAgent"],
            "SummarizeResult",
        )
        workflow.add_conditional_edges("SummarizeResult", meet_criteria)
        workflow.add_edge("RefinerAgent", "SummarizeResult")
        workflow.add_edge("AcceptanceAgent", END)
        graph = workflow.compile()
        # workflow.add_edge("NewsGenerationAgent", END)
        return graph

    async def run(self):
        async def run_scenario(scenario):
            logger.info(f"🤖 Running scenario: {scenario}")
            try:
                return await asyncio.wait_for(
                    self.workflow_with_data_generation.ainvoke(scenario), timeout=500
                )
            except asyncio.TimeoutError:
                logger.warning(f"⏱️ Scenario timed out after 10 seconds: {scenario}")
                return ""

        # randomly select 50 scenarios
        random.shuffle(self.scenarios)
        tasks = [run_scenario(scenario) for scenario in self.scenarios[:100]]
        results = await asyncio.gather(*tasks)
        return results


if __name__ == "__main__":
    agent = CodeSwitchingAgent()
    asyncio.run(agent.run())
