from typing import TypedDict, Optional, Annotated
from operator import add

class GenerationResponse(TypedDict):
    instances: list[str]


class FluencyResponse(TypedDict):
    fluency_score: float
    errors: dict[str, str]
    summary: str


class NaturalnessResponse(TypedDict):
    naturalness_score: float
    observations: dict[str, str]
    summary: str


class CSRatioResponse(TypedDict):
    ratio_score: float
    computed_ratio: str
    notes: str


class SocialCulturalResponse(TypedDict):
    socio_cultural_score: float
    issues: str
    summary: str


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
    cs_function: str
    cs_type: str
    news_article: Optional[str] = None
    response: str
    data_generation_result: list[str]
    news_generation_result: list[str]

    fluency_result: FluencyResponse
    naturalness_result: NaturalnessResponse
    cs_ratio_result: CSRatioResponse
    social_cultural_result: SocialCulturalResponse

    summary: str
    score: float

    refine_count: Annotated[int, add]

    news_hash: set
    news_dict: dict
