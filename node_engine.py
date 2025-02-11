import os
import dotenv
from langchain_openai import ChatOpenAI
from prompt import SAMPLE_AGENT_PROMPT
from node_models import AgentRunningState

# for testing
# #
# dotenv.load_dotenv()

# os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# SampleAgent = SAMPLE_AGENT_PROMPT | ChatOpenAI(model="gpt-4o", temperature=1)

def RunSampleAgent(state: AgentRunningState):
    SampleAgent = SAMPLE_AGENT_PROMPT | ChatOpenAI(model="gpt-4o", temperature=1)
    return SampleAgent.invoke({"language_a": "Cantonese", "language_b": "English", "tense": "Present", "person": "First Person"})
if __name__ == "__main__":
    # result = SampleAgent.invoke({"language_a": "Cantonese", "language_b": "English", "tense": "Present", "person": "First Person"})
    # print(result.content)
    pass