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

logger.add("logs/code_switching_agent.log")

MAX_REFINER_ITERATIONS = 1


def meet_criteria(state: AgentRunningState):
    if state["score"] < 8 and state["refine_count"] < MAX_REFINER_ITERATIONS:
        return "RefinerAgent"
    else:
        return "AcceptanceAgent"


class CodeSwitchingAgent:
    def __init__(self,scenario_k):
        self.state = AgentRunningState()
        self.state["refine_count"] = 0
        for key in scenario_k.keys():
            self.state[key] = scenario_k[key]
        self.state["news_article"] = ""
        #self.workflow: StateGraph = self._construct_graph()
        self.workflow_with_data_generation: StateGraph = (
            self._construct_graph_with_data_generation()
        )

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
        #logger.info(f"🤖 Running scenario: {self.scenario_k}")
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

# async def main():
#     config: dict = load_config()
#     scenarios: list[AgentRunningState] = generate_scenarios(
#         config["pre_execute"]
#     )
#     #shuffle scenarios
#     random.shuffle(scenarios)
#     tasks = [arun(scenario) for scenario in scenarios[:10]]
#     results = []
#     # 使用 asyncio.as_completed 來逐個等待任務完成
#     for task in tqdm(asyncio.as_completed(tasks), total=len(tasks)):
#         result = await task
#         results.append(result)
#     return results


    
# if __name__ == "__main__":
#     asyncio.run(main())
#     # config: dict = load_config()
#     # scenarios: list[AgentRunningState] = generate_scenarios(
#     #     config["pre_execute"]
#     # )
#     # print(len(scenarios))



import math
from concurrent.futures import ProcessPoolExecutor
# 假设 arun(scenario) 是你之前定义的异步函数，用来处理单个 scenario
async def run_scenarios_group(scenarios):
    tasks = [arun(scenario) for scenario in scenarios]
    results = []
    # 利用 asyncio.as_completed 配合 tqdm 展示进度
    for task in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Group Progress"):
        result = await task
        results.append(result)
    return results

def process_group(scenarios):
    # 每个进程内独立启动一个事件循环来处理该组 scenario
    return asyncio.run(run_scenarios_group(scenarios))

if __name__ == "__main__":
    config = load_config()
    scenarios = generate_scenarios(config["pre_execute"])
    #shuffle scenarios
    random.shuffle(scenarios)
    scenarios = scenarios[:10000]
    
    # 设置进程数量，根据机器核数或实际情况调整
    num_processes = 32
    group_size = math.ceil(len(scenarios) / num_processes)
    # 将 scenario 划分为多个组
    groups = [scenarios[i:i + group_size] for i in range(0, len(scenarios), group_size)]
    print(len(groups))
    all_results = []
    # 使用 ProcessPoolExecutor 启动多个进程
    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        futures = [executor.submit(process_group, group) for group in groups]
        for future in tqdm(futures, desc="Total Progress"):
            group_results = future.result()
            all_results.extend(group_results)
    
    # all_results 包含了所有 scenario 的结果