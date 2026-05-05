"""
A2A Protocol Core - Agent Card & Message Schema
Google's Agent-to-Agent (A2A) Protocol Implementation
"""
from pydantic import BaseModel, Field
from typing import Any, Optional, Literal
from datetime import datetime
import uuid


# ─── Agent Card (A2A Discovery) ───────────────────────────────────────────────

class AgentCapability(BaseModel):
    name: str
    description: str
    input_schema: dict = {}
    output_schema: dict = {}


class AgentCard(BaseModel):
    """Standard A2A Agent Card for service discovery"""
    agent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    version: str = "1.0.0"
    framework: Literal["langchain", "crewai", "autogen", "google_adk"]
    endpoint: str
    capabilities: list[AgentCapability] = []
    metadata: dict = {}
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ─── A2A Message Protocol ─────────────────────────────────────────────────────

class A2AMessage(BaseModel):
    """Standard A2A message format"""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_agent: str
    to_agent: str
    task_id: str
    message_type: Literal["request", "response", "stream", "error", "status"]
    content: Any
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: dict = {}


class TaskRequest(BaseModel):
    """A2A Task Request"""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_type: str
    payload: dict
    priority: int = 1
    timeout_seconds: int = 120
    callback_url: Optional[str] = None


class TaskResponse(BaseModel):
    """A2A Task Response"""
    task_id: str
    status: Literal["pending", "running", "completed", "failed"]
    result: Optional[Any] = None
    error: Optional[str] = None
    agent_id: str
    framework: str
    execution_time_ms: Optional[float] = None


# ─── Agent Registry ───────────────────────────────────────────────────────────

class AgentRegistry:
    """In-memory Agent Registry for A2A Discovery"""

    def __init__(self):
        self._agents: dict[str, AgentCard] = {}

    def register(self, card: AgentCard) -> None:
        self._agents[card.agent_id] = card
        print(f"[Registry] ✓ Registered: {card.name} ({card.framework}) @ {card.endpoint}")

    def discover(self, framework: Optional[str] = None) -> list[AgentCard]:
        agents = list(self._agents.values())
        if framework:
            agents = [a for a in agents if a.framework == framework]
        return agents

    def get(self, agent_id: str) -> Optional[AgentCard]:
        return self._agents.get(agent_id)

    def list_all(self) -> dict:
        return {
            "total": len(self._agents),
            "agents": [
                {"id": a.agent_id, "name": a.name, "framework": a.framework}
                for a in self._agents.values()
            ]
        }


# Singleton registry
registry = AgentRegistry()
