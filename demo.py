"""
A2A Multi-Framework Demo
Demonstrates all 4 frameworks working together via A2A protocol
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from protocols.a2a_protocol import TaskRequest, registry
from agents.langchain_agent import LangChainA2AAgent
from agents.crewai_agent import CrewAIA2AAgent
from agents.autogen_agent import AutoGenA2AAgent
from agents.google_adk_agent import GoogleADKOrchestrator


def print_separator(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def print_result(response):
    print(f"  Status: {response.status}")
    print(f"  Framework: {response.framework}")
    print(f"  Time: {response.execution_time_ms:.1f}ms")
    if response.result:
        for k, v in response.result.items():
            if k not in ("shared_context",):
                print(f"  {k}: {v}")


async def demo():
    print("\n🚀 A2A MULTI-FRAMEWORK DEMO")
    print("   LangChain + CrewAI + AutoGen + Google ADK")

    # ── Initialize all agents ──────────────────────────────────────────────────
    print_separator("1. Initializing All Framework Agents")
    langchain = LangChainA2AAgent()
    crewai = CrewAIA2AAgent()
    autogen = AutoGenA2AAgent()
    orchestrator = GoogleADKOrchestrator(
        langchain_agent=langchain,
        crewai_agent=crewai,
        autogen_agent=autogen,
    )

    # ── Registry Discovery ─────────────────────────────────────────────────────
    print_separator("2. A2A Registry - Agent Discovery")
    all_agents = registry.discover()
    print(f"  Total registered agents: {len(all_agents)}")
    for agent in all_agents:
        print(f"  ✓ [{agent.framework.upper():12}] {agent.name}")
        print(f"    Endpoint: {agent.endpoint}")
        print(f"    Capabilities: {[c.name for c in agent.capabilities]}")

    # ── LangChain: Research ────────────────────────────────────────────────────
    print_separator("3. LangChain Agent - Research Task")
    lc_request = TaskRequest(
        task_type="research",
        payload={"query": "Latest AI agent frameworks 2025", "max_results": 5}
    )
    lc_response = await langchain.execute_task(lc_request)
    print_result(lc_response)

    # ── CrewAI: Content Creation ───────────────────────────────────────────────
    print_separator("4. CrewAI Agent - Content Creation")
    crew_request = TaskRequest(
        task_type="content_creation",
        payload={"topic": "A2A Protocol explained simply", "format": "blog", "length": 500}
    )
    crew_response = await crewai.execute_task(crew_request)
    print_result(crew_response)

    # ── AutoGen: Code Generation ───────────────────────────────────────────────
    print_separator("5. AutoGen Agent - Code Generation")
    ag_request = TaskRequest(
        task_type="code_generation",
        payload={
            "description": "FastAPI endpoint with JWT authentication",
            "language": "python",
            "framework": "fastapi"
        }
    )
    ag_response = await autogen.execute_task(ag_request)
    print_result(ag_response)

    # ── Google ADK: Auto-routing ───────────────────────────────────────────────
    print_separator("6. Google ADK - Smart Auto-Routing")

    tasks = [
        "Research the latest trends in multi-agent AI systems",
        "Write a blog post about the benefits of A2A protocol",
        "Generate Python code for an async HTTP client",
    ]

    for task in tasks:
        result = await orchestrator.orchestrate(task)
        print(f"\n  Task: {task[:50]}...")
        print(f"  → Routed to: {result['framework_used'].upper()}")
        print(f"  → Time: {result['total_execution_ms']:.1f}ms")

    # ── Pipeline: All 3 frameworks sequentially ────────────────────────────────
    print_separator("7. Multi-Framework Pipeline (ADK Coordinates All)")
    pipeline_result = await orchestrator.run_pipeline([
        {
            "framework": "langchain",
            "task": "research",
            "payload": {"query": "AI agent market 2025"}
        },
        {
            "framework": "crewai",
            "task": "content_creation",
            "payload": {"topic": "AI agent market analysis", "format": "report"}
        },
        {
            "framework": "autogen",
            "task": "code_generation",
            "payload": {"description": "Data visualization dashboard", "language": "python"}
        }
    ])

    print(f"  Pipeline completed: {pipeline_result['pipeline_completed']}")
    print(f"  Steps executed: {pipeline_result['steps_executed']}")
    for step_key in pipeline_result['results']:
        step = pipeline_result['results'][step_key]
        fw = step.get('framework', 'unknown')
        print(f"  ✓ {step_key} [{fw}] - SUCCESS")

    # ── Summary ────────────────────────────────────────────────────────────────
    print_separator("✅ Demo Complete - All Frameworks Integrated!")
    print("""
  Architecture Summary:
  ┌─────────────────────────────────────────┐
  │          Google ADK (Master)            │  ← Entry point
  │         Task Router & Orchestrator      │
  └──────┬──────────┬──────────┬────────────┘
         │          │          │
    ┌────▼───┐ ┌────▼───┐ ┌───▼────┐
    │LangChain│ │CrewAI  │ │AutoGen │
    │Research │ │Content │ │ Code   │
    └─────────┘ └────────┘ └────────┘
         ↕          ↕          ↕
    ────────── A2A Protocol ──────────
    (Agent Cards, Task Requests, Registry)
    """)


if __name__ == "__main__":
    asyncio.run(demo())
