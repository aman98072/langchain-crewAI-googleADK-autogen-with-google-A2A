"""
CrewAI Agent - A2A Enabled
Role: Multi-Agent Crew Orchestrator
"""
import time
import asyncio
from protocols.a2a_protocol import AgentCard, AgentCapability, TaskRequest, TaskResponse, registry


class CrewAIA2AAgent:
    """
    CrewAI-based agent that manages specialized sub-crews.
    Specializes in: multi-step tasks, role delegation, content creation.
    """

    AGENT_ID = "crewai-orchestrator-001"
    FRAMEWORK = "crewai"

    def __init__(self):
        self.agent_id = self.AGENT_ID
        self.name = "CrewAI Orchestrator"
        self._setup_crew()
        self._register()

    def _setup_crew(self):
        """Initialize CrewAI agents and tasks"""
        # In production:
        # from crewai import Agent, Task, Crew, Process
        #
        # self.researcher = Agent(role='Researcher', goal='Find accurate info',
        #     backstory='Expert researcher', tools=[search_tool])
        # self.writer = Agent(role='Writer', goal='Create compelling content',
        #     backstory='Professional writer')
        # self.analyst = Agent(role='Analyst', goal='Analyze and synthesize data',
        #     backstory='Data analyst')

        self.crew_members = [
            {"role": "Researcher", "specialty": "information gathering"},
            {"role": "Writer", "specialty": "content creation"},
            {"role": "Analyst", "specialty": "data analysis"},
            {"role": "QA Reviewer", "specialty": "quality assurance"},
        ]
        print(f"[CrewAI] Crew initialized with {len(self.crew_members)} agents")

    def _register(self):
        """Register with A2A registry"""
        card = AgentCard(
            agent_id=self.agent_id,
            name=self.name,
            description="CrewAI orchestrator managing specialized sub-crews for "
                        "complex multi-step tasks requiring role-based collaboration.",
            framework=self.FRAMEWORK,
            endpoint="http://localhost:8002/a2a",
            capabilities=[
                AgentCapability(
                    name="content_creation",
                    description="Create high-quality content using researcher+writer crew",
                    input_schema={"topic": "str", "format": "str", "length": "int"},
                    output_schema={"content": "str", "quality_score": "float"}
                ),
                AgentCapability(
                    name="analysis_report",
                    description="Generate comprehensive analysis reports",
                    input_schema={"data": "dict", "report_type": "str"},
                    output_schema={"report": "str", "insights": "list"}
                ),
                AgentCapability(
                    name="competitive_research",
                    description="Multi-agent competitive analysis",
                    input_schema={"company": "str", "competitors": "list"},
                    output_schema={"analysis": "dict"}
                ),
            ]
        )
        registry.register(card)

    async def execute_task(self, request: TaskRequest) -> TaskResponse:
        """Execute via CrewAI crew"""
        start_time = time.time()
        try:
            result = await self._run_crew(request)
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

    async def _run_crew(self, request: TaskRequest) -> dict:
        """Simulate CrewAI crew execution"""
        task_type = request.task_type
        payload = request.payload

        await asyncio.sleep(0.15)  # Simulate crew coordination

        if task_type == "content_creation":
            return {
                "content": f"[CrewAI] High-quality content about: {payload.get('topic')}",
                "quality_score": 0.92,
                "crew_used": ["Researcher", "Writer", "QA Reviewer"],
                "process": "sequential",
                "framework": "CrewAI"
            }
        elif task_type == "analysis_report":
            return {
                "report": f"[CrewAI] Analysis report generated",
                "insights": ["insight_1", "insight_2", "insight_3"],
                "crew_used": ["Researcher", "Analyst"],
                "framework": "CrewAI"
            }
        elif task_type == "competitive_research":
            company = payload.get("company", "")
            competitors = payload.get("competitors", [])
            return {
                "analysis": {
                    "company": company,
                    "competitors_analyzed": competitors,
                    "strengths": ["Market position", "Technology"],
                    "weaknesses": ["Pricing", "Support"],
                },
                "framework": "CrewAI",
                "crew_used": ["Researcher", "Analyst", "Writer"]
            }
        else:
            raise ValueError(f"Unknown task: {task_type}")
