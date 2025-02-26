import os
import dotenv
import jsonlines
from langchain_openai import ChatOpenAI
from prompt import SAMPLE_AGENT_PROMPT
from node_models import AgentRunningState, Response
from pprint import pprint

# for testing
# #
dotenv.load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("AIPROXY_API_KEY")

# SampleAgent = SAMPLE_AGENT_PROMPT | ChatOpenAI(model="gpt-4o", temperature=1)

def RunSampleAgent(state: AgentRunningState):
    SampleAgent = SAMPLE_AGENT_PROMPT | ChatOpenAI(model="gpt-4o", temperature=1, base_url="https://apivip.aiproxy.io/v1").with_structured_output(Response)
    response = SampleAgent.invoke(state)
    if response.get("type"):
        return {'response': ""}
    #print(response.content)
    #copy the state and add the response
    payload = state.copy()
    payload['response'] = response
    with jsonlines.open("result/simple_agent_result_new.jsonl", "a") as f:
        f.write(response)
    return {'response': response}
if __name__ == "__main__":
    # result = SampleAgent.invoke({"language_a": "Cantonese", "language_b": "English", "tense": "Present", "person": "First Person"})
    # print(result.content)
    pass