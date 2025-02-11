from typing import TypedDict

class AgentRunningState(TypedDict):
    pre_execute: dict
    on_execute: dict
