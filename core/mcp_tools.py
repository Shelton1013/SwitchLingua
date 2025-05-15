# New file mcp_tools.py
from __future__ import annotations
from typing import Protocol, Dict, Any, runtime_checkable

###############################################################################
# Abstract Interface & Registry Mechanism
###############################################################################
@runtime_checkable
class BaseTool(Protocol):
    """All MCP tools must implement the run(state) -> dict interface"""
    name: str  # Unique identifier
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]: ...

# registry used to automatically collect tools
_REGISTRY: dict[str, BaseTool] = {}

def register(tool_cls):
    """class decorator – automatically add tools to registry"""
    instance = tool_cls()
    if not isinstance(instance, BaseTool):
        raise TypeError(f"{tool_cls} must implement the BaseTool interface")
    _REGISTRY[instance.name] = instance
    return tool_cls

def get_all_tools() -> dict[str, BaseTool]:
    return _REGISTRY

###############################################################################
# Example Tool – After development, developers only need to copy this template
###############################################################################
@register
class SampleWordCountTool:
    """Example: Count the total number of tokens in data_generation_result"""
    name = "word_count"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        instances = state.get("data_generation_result", [])
        token_cnt = sum(len(s.split()) for s in instances)
        return {self.name: token_cnt}

# You can write more tools, such as summarization, translation, entity extraction, etc.