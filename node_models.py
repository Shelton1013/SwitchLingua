from typing import TypedDict

class AgentRunningState(TypedDict):
    topic: str
    tense: str
    perspective: str
    cs_ratio: str
    gender: str
    age: str
    education_level: str
    first_language: str
    second_language: str
    response: str
        
