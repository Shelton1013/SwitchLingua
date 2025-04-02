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
from tqdm import tqdm
import jsonlines as jsl
from datetime import datetime

logger.add(f"logs/code_switching_agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

MAX_REFINER_ITERATIONS = 1


def meet_criteria(state: AgentRunningState):
    if state["score"] < 8 and state["refine_count"] < MAX_REFINER_ITERATIONS:
        return "RefinerAgent"
    else:
        return "AcceptanceAgent"


class CodeSwitchingAgent:
    def __init__(self, scenario_k):
        self.state = AgentRunningState()
        self.state["refine_count"] = 0
        for key in scenario_k.keys():
            self.state[key] = scenario_k[key]
        self.state["news_article"] = ""
        self.state["news_hash"] = set()
        self.state["news_dict"] = {}
        self._init_news_db()
        # self.workflow: StateGraph = self._construct_graph()
        self.workflow_with_data_generation: StateGraph = (
            self._construct_graph_with_data_generation()
        )

    def _init_news_db(self):
        topics = [
            "business",
            "entertainment",
            "general",
            "health",
            "nation",
            "science",
            "sports",
            "technology",
            "world",
        ]
        for topic in topics:
            self.state["news_dict"][topic] = []
            with open(f"news/{topic}_HK_NEWS_mar31_LAST300DAYS.json") as f:
                for line in jsl.Reader(f):
                    self.state["news_dict"][topic].append(line.get("content"))

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
        # logger.info(f"🤖 Running scenario: {self.scenario_k}")
        try:
            return await self.workflow_with_data_generation.ainvoke(
                self.state, {"recursion_limit": 1e10}
            )
        except asyncio.TimeoutError:
            logger.warning(f"⏱️ Scenario timed out after 10 seconds: {self.scenario_k}")
            return ""


async def arun(scenario_k):
    agent_instance = CodeSwitchingAgent(scenario_k)
    await agent_instance.run()


async def main():
    config: dict = load_config("config_augmented.yaml")
    scenarios: list[AgentRunningState] = generate_scenarios(config["pre_execute"])
    # shuffle scenarios
    random.shuffle(scenarios)
    # make a for loop, each loop run 10 scenarios
    for i in range(0, len(scenarios), 40):

        tasks = [arun(scenario) for scenario in scenarios[i : i + 40]]
        results = []
        # 使用 asyncio.as_completed 來逐個等待任務完成
        try:
            for task in tqdm(
                asyncio.as_completed(tasks, timeout=2400), total=len(tasks)
            ):
                result = await task
                results.append(result)
        except asyncio.TimeoutError:
            logger.warning(f"⏱️ Scenario timed out after 2400 seconds: {i}")
            results.append(None)
            continue
    return results


if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
        except Exception as e:
            logger.error(f"🚨 Error: {e}")
            continue
    # config: dict = load_config()
    # scenarios: list[AgentRunningState] = generate_scenarios(
    #     config["pre_execute"]
    # )
    # print(len(scenarios))

    # all_results 包含了所有 scenario 的结果
