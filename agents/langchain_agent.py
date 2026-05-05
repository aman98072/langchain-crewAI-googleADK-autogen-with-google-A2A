"""
LangChain Agent - A2A Enabled
Role: Research & Tool-Calling Agent
"""
import time
import asyncio
from typing import Any
from protocols.a2a_protocol import AgentCard, AgentCapability, TaskRequest, TaskResponse, registry


class LangChainA2AAgent:
    """
    LangChain-based agent that exposes itself via A2A protocol.
    Specializes in: research, web search, document analysis.
    """

    AGENT_ID = "langchain-research-agent-001"
    FRAMEWORK = "langchain"

    def __init__(self, llm_api_key: str = ""):
        self.agent_id = self.AGENT_ID
        self.name = "LangChain Research Agent"
        self._setup_agent(llm_api_key)
        self._register()

    def _setup_agent(self, api_key: str):
        """Initialize LangChain tools and agent"""
        # In production: use actual LangChain tools
        # from langchain_openai import ChatOpenAI
        # from langchain.agents import AgentExecutor, create_openai_tools_agent
        # from langchain_community.tools import DuckDuckGoSearchRun

        self.tools = [
            {"name": "web_search", "description": "Search the web for information"},
            {"name": "summarize", "description": "Summarize long documents"},
            {"name": "extract_entities", "description": "Extract key entities from text"},
        ]
        print(f"[LangChain] Agent initialized with {len(self.tools)} tools")

    def _register(self):
        """Register this agent with A2A registry"""
        card = AgentCard(
            agent_id=self.agent_id,
            name=self.name,
            description="Research agent powered by LangChain. Handles web search, "
                        "document analysis, and entity extraction.",
            framework=self.FRAMEWORK,
            endpoint="http://localhost:8001/a2a",
            capabilities=[
                AgentCapability(
                    name="research",
                    description="Deep research on any topic",
                    input_schema={"query": "str", "max_results": "int"},
                    output_schema={"summary": "str", "sources": "list"}
                ),
                AgentCapability(
                    name="summarize",
                    description="Summarize documents or text",
                    input_schema={"text": "str", "max_words": "int"},
                    output_schema={"summary": "str"}
                ),
            ]
        )
        registry.register(card)

    async def execute_task(self, request: TaskRequest) -> TaskResponse:
        """Execute an A2A task request"""
        start_time = time.time()

        try:
            result = await self._route_task(request)
            return TaskResponse(
                task_id=request.task_id,
                status="completed",
                result=result,
                agent_id=self.agent_id,
                framework=self.FRAMEWORK,
                execution_time_ms=(time.time() - start_time) * 1000
            )
        except Exception as e:
            return TaskResponse(
                task_id=request.task_id,
                status="failed",
                error=str(e),
                agent_id=self.agent_id,
                framework=self.FRAMEWORK,
            )

    async def _route_task(self, request: TaskRequest) -> dict:
        """Route task to appropriate LangChain chain"""
        task_type = request.task_type

        if task_type == "research":
            return await self._research(request.payload.get("query", ""))
        elif task_type == "summarize":
            return await self._summarize(request.payload.get("text", ""))
        else:
            raise ValueError(f"Unsupported task type: {task_type}")

    async def _research(self, query: str) -> dict:
        """Simulate LangChain research chain"""
        await asyncio.sleep(0.1)  # Simulate LLM call
        return {
            "query": query,
            "summary": f"[LangChain] Research findings for: {query}",
            "sources": ["source1.com", "source2.com"],
            "framework": "LangChain",
            "chain_used": "ReAct + DuckDuckGo"
        }

    async def _summarize(self, text: str) -> dict:
        """Simulate LangChain summarization chain"""
        await asyncio.sleep(0.05)
        return {
            "summary": f"[LangChain] Summary: {text[:100]}...",
            "word_count": len(text.split()),
            "framework": "LangChain"
        }
