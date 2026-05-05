"""
A2A Multi-Framework FastAPI Server
Production-ready REST API exposing all framework agents
"""
import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from protocols.a2a_protocol import TaskRequest, registry
from agents.langchain_agent import LangChainA2AAgent
from agents.crewai_agent import CrewAIA2AAgent
from agents.autogen_agent import AutoGenA2AAgent
from agents.google_adk_agent import GoogleADKOrchestrator

# ─── App Setup ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="A2A Multi-Framework API",
    description="Production A2A server: LangChain + CrewAI + AutoGen + Google ADK",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Agent Initialization ─────────────────────────────────────────────────────

langchain_agent = LangChainA2AAgent()
crewai_agent = CrewAIA2AAgent()
autogen_agent = AutoGenA2AAgent()
orchestrator = GoogleADKOrchestrator(
    langchain_agent=langchain_agent,
    crewai_agent=crewai_agent,
    autogen_agent=autogen_agent,
)

AGENT_MAP = {
    "langchain": langchain_agent,
    "crewai": crewai_agent,
    "autogen": autogen_agent,
    "google_adk": orchestrator,
}


# ─── Health & Discovery Endpoints ─────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "healthy", "agents_registered": len(registry._agents)}


@app.get("/.well-known/agent.json")
async def agent_discovery():
    """A2A standard discovery endpoint"""
    return registry.list_all()


@app.get("/agents")
async def list_agents(framework: str = None):
    """List all registered agents, optionally filter by framework"""
    agents = registry.discover(framework=framework)
    return {"agents": [a.dict() for a in agents]}


@app.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get agent card by ID"""
    card = registry.get(agent_id)
    if not card:
        raise HTTPException(404, f"Agent {agent_id} not found")
    return card.dict()


# ─── Task Execution Endpoints ──────────────────────────────────────────────────

@app.post("/a2a/task")
async def execute_task(request: TaskRequest, framework: str = "google_adk"):
    """Execute a task on a specific framework agent"""
    agent = AGENT_MAP.get(framework)
    if not agent:
        raise HTTPException(400, f"Unknown framework: {framework}. Options: {list(AGENT_MAP.keys())}")

    response = await agent.execute_task(request)
    return response.dict()


@app.post("/orchestrate")
async def orchestrate(body: dict):
    """
    Main endpoint: ADK orchestrates task across frameworks.
    Body: {"task": "your task description", "context": {}}
    """
    task = body.get("task", "")
    context = body.get("context", {})
    if not task:
        raise HTTPException(400, "task field is required")
    return await orchestrator.orchestrate(task, context)


@app.post("/pipeline")
async def run_pipeline(body: dict):
    """
    Run multi-framework pipeline.
    Body: {"pipeline": [{"framework": "langchain", "task": "research", "payload": {...}}, ...]}
    """
    pipeline = body.get("pipeline", [])
    if not pipeline:
        raise HTTPException(400, "pipeline array is required")
    return await orchestrator.run_pipeline(pipeline)


# ─── Framework-Specific Endpoints ─────────────────────────────────────────────

@app.post("/langchain/research")
async def langchain_research(body: dict):
    """LangChain: Research endpoint"""
    request = TaskRequest(task_type="research", payload=body)
    response = await langchain_agent.execute_task(request)
    return response.dict()


@app.post("/crewai/create")
async def crewai_create(body: dict):
    """CrewAI: Content creation endpoint"""
    request = TaskRequest(task_type="content_creation", payload=body)
    response = await crewai_agent.execute_task(request)
    return response.dict()


@app.post("/autogen/code")
async def autogen_code(body: dict):
    """AutoGen: Code generation endpoint"""
    request = TaskRequest(task_type="code_generation", payload=body)
    response = await autogen_agent.execute_task(request)
    return response.dict()


# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8009,
        reload=True,
        log_level="info"
    )
