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
    conversation_type: str
    response: str
        
class Response(TypedDict):
    topic: str
    instances: list[str]
    conversation_type: str