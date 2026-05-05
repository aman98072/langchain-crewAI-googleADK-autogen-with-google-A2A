"""
Google ADK Master Orchestrator - A2A Enabled
Role: Top-level orchestrator that delegates to all framework agents
"""
import time
import asyncio
from typing import Optional
from protocols.a2a_protocol import AgentCard, AgentCapability, TaskRequest, TaskResponse, registry


class GoogleADKOrchestrator:
    """
    Google ADK-based master orchestrator.
    Receives user tasks, decomposes them, and delegates to appropriate agents.
    Frameworks: LangChain → Research | CrewAI → Content | AutoGen → Code
    """

    AGENT_ID = "google-adk-master-001"
    FRAMEWORK = "google_adk"

    def __init__(
        self,
        langchain_agent=None,
        crewai_agent=None,
        autogen_agent=None,
    ):
        self.agent_id = self.AGENT_ID
        self.name = "Google ADK Master Orchestrator"

        # Connected framework agents
        self.langchain = langchain_agent
        self.crewai = crewai_agent
        self.autogen = autogen_agent

        self._setup_adk()
        self._register()

    def _setup_adk(self):
        """Initialize Google ADK runner"""
        # In production:
        # from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent
        # from google.adk.runners import Runner
        # from google.adk.sessions import InMemorySessionService
        #
        # self.session_service = InMemorySessionService()
        # self.orchestrator = LlmAgent(
        #     name="master_orchestrator",
        #     model="gemini-2.0-flash",
        #     instruction=ORCHESTRATOR_SYSTEM_PROMPT,
        #     tools=[delegate_to_langchain, delegate_to_crewai, delegate_to_autogen]
        # )
        # self.runner = Runner(agent=self.orchestrator,
        #     session_service=self.session_service)

        print("[Google ADK] Master orchestrator initialized")
        print(f"[Google ADK] Connected agents: LangChain={self.langchain is not None}, "
              f"CrewAI={self.crewai is not None}, AutoGen={self.autogen is not None}")

    def _register(self):
        """Register with A2A registry"""
        card = AgentCard(
            agent_id=self.agent_id,
            name=self.name,
            description="Google ADK master orchestrator. Intelligently routes tasks "
                        "to LangChain (research), CrewAI (content), or AutoGen (code) "
                        "based on task requirements.",
            framework=self.FRAMEWORK,
            endpoint="http://localhost:8000/a2a",
            capabilities=[
                AgentCapability(
                    name="orchestrate",
                    description="Decompose and route complex tasks across frameworks",
                    input_schema={"task": "str", "context": "dict"},
                    output_schema={"results": "list", "synthesis": "str"}
                ),
                AgentCapability(
                    name="pipeline",
                    description="Run multi-framework pipeline sequentially",
                    input_schema={"pipeline": "list", "shared_context": "dict"},
                    output_schema={"pipeline_results": "dict"}
                ),
            ]
        )
        registry.register(card)

    # ─── Core Routing Logic ────────────────────────────────────────────────────

    def _classify_task(self, task_description: str) -> str:
        """Classify which framework should handle this task"""
        task_lower = task_description.lower()

        if any(kw in task_lower for kw in ["code", "script", "function", "debug", "program", "api"]):
            return "autogen"
        elif any(kw in task_lower for kw in ["write", "create content", "article", "blog", "report"]):
            return "crewai"
        elif any(kw in task_lower for kw in ["research", "search", "find", "summarize", "analyze"]):
            return "langchain"
        else:
            return "crewai"  # Default: CrewAI for general tasks

    async def orchestrate(self, user_task: str, context: dict = {}) -> dict:
        """
        Main entry point: ADK orchestrates all frameworks.
        """
        start_time = time.time()
        print(f"\n[ADK] 🎯 New task received: {user_task}")

        framework = self._classify_task(user_task)
        print(f"[ADK] 🧠 Routing to: {framework.upper()}")

        result = await self._delegate(framework, user_task, context)

        total_time = (time.time() - start_time) * 1000
        return {
            "orchestrator": "Google ADK",
            "framework_used": framework,
            "task": user_task,
            "result": result,
            "total_execution_ms": total_time,
            "status": "completed"
        }

    async def run_pipeline(self, steps: list[dict]) -> dict:
        """
        Run a multi-framework pipeline.
        steps = [
            {"framework": "langchain", "task": "research", "payload": {...}},
            {"framework": "crewai", "task": "content_creation", "payload": {...}},
            {"framework": "autogen", "task": "code_generation", "payload": {...}},
        ]
        """
        print(f"\n[ADK] 🔄 Running pipeline with {len(steps)} steps")
        pipeline_results = {}
        shared_context = {}

        for i, step in enumerate(steps):
            framework = step["framework"]
            task_type = step["task"]
            payload = {**step.get("payload", {}), "shared_context": shared_context}

            print(f"[ADK] Step {i+1}/{len(steps)}: {framework} → {task_type}")

            request = TaskRequest(task_type=task_type, payload=payload)

            agent = self._get_agent(framework)
            if agent:
                response = await agent.execute_task(request)
                step_result = response.result or {"error": response.error}
            else:
                step_result = {"error": f"No agent connected for {framework}"}

            pipeline_results[f"step_{i+1}_{framework}"] = step_result
            # Pass results forward as context
            shared_context[framework] = step_result

        return {
            "pipeline_completed": True,
            "steps_executed": len(steps),
            "results": pipeline_results,
            "orchestrator": "Google ADK"
        }

    async def _delegate(self, framework: str, task: str, context: dict) -> dict:
        """Delegate task to appropriate framework agent"""
        agent = self._get_agent(framework)
        if not agent:
            return {"error": f"Agent not connected: {framework}"}

        # Map task description to task type
        task_type_map = {
            "autogen": "code_generation",
            "crewai": "content_creation",
            "langchain": "research",
        }
        request = TaskRequest(
            task_type=task_type_map.get(framework, "research"),
            payload={"description": task, "query": task, "topic": task, **context}
        )
        response = await agent.execute_task(request)
        return response.result or {"error": response.error}

    def _get_agent(self, framework: str):
        """Get agent instance by framework name"""
        return {
            "langchain": self.langchain,
            "crewai": self.crewai,
            "autogen": self.autogen,
        }.get(framework)

    async def execute_task(self, request: TaskRequest) -> TaskResponse:
        """A2A interface for external agents"""
        start_time = time.time()
        try:
            if request.task_type == "orchestrate":
                result = await self.orchestrate(
                    request.payload.get("task", ""),
                    request.payload.get("context", {})
                )
            elif request.task_type == "pipeline":
                result = await self.run_pipeline(
                    request.payload.get("pipeline", [])
                )
            else:
                result = await self.orchestrate(str(request.payload))

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
