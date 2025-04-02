import os
import dotenv
import random
import jsonlines
from langchain_openai import ChatOpenAI
from prompt import (
    SAMPLE_AGENT_PROMPT,
    USE_TOOLS_PROMPT,
    DATA_GENERATION_PROMPT,
    FLUENCY_PROMPT,
    NATURALNESS_PROMPT,
    CS_RATIO_PROMPT,
    SOCIAL_CULTURAL_PROMPT,
    REFINER_PROMPT,
)
from node_models import (
    AgentRunningState,
    GenerationResponse,
    FluencyResponse,
    NaturalnessResponse,
    CSRatioResponse,
    SocialCulturalResponse,
)
from utils import weighting_scheme
from pprint import pprint
from copy import deepcopy

# for testing
# #
dotenv.load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("AIPROXY_API_KEY")

# SampleAgent = SAMPLE_AGENT_PROMPT | ChatOpenAI(model="gpt-4o", temperature=1)
MODEL = "gpt-4o"


def RunSampleAgent(state: AgentRunningState):
    SampleAgent = SAMPLE_AGENT_PROMPT | ChatOpenAI(
        model=MODEL, temperature=1, base_url="https://api.bianxie.ai/v1/"
    ).with_structured_output(GenerationResponse)
    response = SampleAgent.invoke(state)
    if response.get("type"):
        return {"response": ""}
    # print(response.content)
    # copy the state and add the responsev
    payload = state.copy()
    payload["response"] = response
    with jsonlines.open("result/simple_agent_result_new.jsonl", "a") as f:
        f.write(response)
    return {"response": response}


def RunUseToolsAgent(state: AgentRunningState):
    UseToolsAgent = USE_TOOLS_PROMPT | ChatOpenAI(
        model=MODEL, temperature=1, base_url="https://api.bianxie.ai/v1/"
    ).with_structured_output(GenerationResponse)
    random_news = []
    with jsonlines.open("news/news_data_till241201.jsonl") as f:
        for line in f:
            random_news.append(line)

    random_news = random.sample(random_news, 1)
    state["news_article"] = random_news[0]["title"] + "\n" + random_news[0]["content"]
    response = UseToolsAgent.invoke(state)
    payload = deepcopy(state)
    del payload["topic"]
    try:
        payload["news_generation_result"] = response["instances"]
        with jsonlines.open("result/use_tools_result_new.jsonl", "a") as f:
            f.write(payload)
    except Exception as e:
        print(response)
    return {"news_generation_result": response["instances"]}


def RunDataGenerationAgent(state: AgentRunningState):
    if state.get("topic") not in state["news_dict"]:
        state["news_article"] = ""
    else:
        if state.get("topic") in state["news_hash"]:
            state["news_article"] = random.choice(state["news_dict"][state["topic"]])
        else:
            state["news_article"] = random.choice(state["news_dict"][state["topic"]])
            state["news_hash"].add(state["topic"])
    DataGenerationAgent = DATA_GENERATION_PROMPT | ChatOpenAI(
        model=MODEL, temperature=0.7, base_url="https://api.bianxie.ai/v1/"
    ).with_structured_output(GenerationResponse)
    response = DataGenerationAgent.invoke(state)
    retry = 4
    if not response.get("instances"):
        while retry > 0:
            response = DataGenerationAgent.invoke(state)
            if response.get("instances"):
                break
            retry -= 1
    # payload = deepcopy(state)
    # try:
    #     payload["instances"] = response["instances"]
    #     with jsonlines.open("result/data_generation_result_new.jsonl", "a") as f:
    #         f.write(payload)
    # except Exception as e:
    #     print(response)
    return {"data_generation_result": response["instances"]}


def RunFluencyAgent(state: AgentRunningState):
    FluencyAgent = FLUENCY_PROMPT | ChatOpenAI(
        model=MODEL, temperature=0.1, base_url="https://api.bianxie.ai/v1/"
    ).with_structured_output(FluencyResponse)
    response = FluencyAgent.invoke(state)

    return {"fluency_result": response}


def RunNaturalnessAgent(state: AgentRunningState):
    NaturalnessAgent = NATURALNESS_PROMPT | ChatOpenAI(
        model=MODEL, temperature=0.1, base_url="https://api.bianxie.ai/v1/"
    ).with_structured_output(NaturalnessResponse)
    response = NaturalnessAgent.invoke(state)

    return {"naturalness_result": response}


def RunCSRatioAgent(state: AgentRunningState):
    CSRatioAgent = CS_RATIO_PROMPT | ChatOpenAI(
        model=MODEL, temperature=0.1, base_url="https://api.bianxie.ai/v1/"
    ).with_structured_output(CSRatioResponse)
    response = CSRatioAgent.invoke(state)

    return {"cs_ratio_result": response}


def RunSocialCulturalAgent(state: AgentRunningState):
    SocialCulturalAgent = SOCIAL_CULTURAL_PROMPT | ChatOpenAI(
        model=MODEL, temperature=0.1, base_url="https://api.bianxie.ai/v1/"
    ).with_structured_output(SocialCulturalResponse)
    response = SocialCulturalAgent.invoke(state)
    return {"social_cultural_result": response}


def SummarizeResult(state: AgentRunningState):
    summary = f"""
    data_generation_result: {state["data_generation_result"]}
    Fluency Result: {state["fluency_result"]}
    Naturalness Result: {state["naturalness_result"]}
    CSRatio Result: {state["cs_ratio_result"]}
    Social Cultural Result: {state["social_cultural_result"]}
    """
    state["summary"] = summary
    # print(summary)
    # with jsonlines.open("result/summary_result_new.jsonl", "a") as f:
    #     f.write(state)

    return {"score": weighting_scheme(state), "summary": summary}


def AcceptanceAgent(state: AgentRunningState):
    del state["news_article"]
    del state["news_hash"]
    del state["news_dict"]
    with jsonlines.open("budget_res/can_eng_Apr2nd_4o_augmented.jsonl", "a") as f:
        f.write(state)
    return


def RunRefinerAgent(state: AgentRunningState):

    RefinerAgent = REFINER_PROMPT | ChatOpenAI(
        model=MODEL, temperature=0.1, base_url="https://api.bianxie.ai/v1/"
    ).with_structured_output(GenerationResponse)
    response = RefinerAgent.invoke(state)

    return {"refiner_result": response, "refine_count": 1}


if __name__ == "__main__":
    FluencyAgent = FLUENCY_PROMPT | ChatOpenAI(
        model="gpt-4o", temperature=0.1, base_url="https://api.bianxie.ai/v1/"
    ).with_structured_output(FluencyResponse)
    response = FluencyAgent.invoke(state)
