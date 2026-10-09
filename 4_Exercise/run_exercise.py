"""Stream real LLM runs and save inspectable tool calls, results and answers."""

import argparse
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from analyst_tools import BASE_DIR
from analyst_graph import build_graph

CASES = [
    ("retrieval", "What was US inflation in 2024?"),
    ("comparison", "Compare GDP growth in the US, Germany and Japan in 2024."),
    ("calculation", "How much did US inflation change between 2023 and 2024?"),
    ("research", "Why was Germany's growth weaker than the US in 2024?"),
    ("agentic", "Identify which of the US, Germany and Japan performed worst in 2024, then research possible reasons and provide an analyst-style conclusion."),
    ("missing_data", "Compare China's productivity growth in 2024 using only the dataset. If unavailable, explain the limitation."),
]


def run_turn(graph, query, thread_id):
    config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 24}
    events, path = [], []
    for event in graph.stream({"messages": [{"role": "user", "content": query}]},
                              config, stream_mode="updates"):
        serializable = {}
        for node, update in event.items():
            path.append(node)
            serializable[node] = {key: [message.model_dump(mode="json") for message in value]
                                  if key == "messages" else value for key, value in update.items()}
            for message in update.get("messages", []):
                if isinstance(message, AIMessage) and message.tool_calls:
                    print(f"  {node}: {[call['name'] for call in message.tool_calls]}", flush=True)
                elif node == "tools":
                    print(f"  tools: {message.name}", flush=True)
        events.append(serializable)
    state = graph.get_state(config).values
    return {"query": query, "thread_id": thread_id, "node_path": path,
            "answer": state["messages"][-1].content, "validation": state["validation"],
            "tool_calls_used": state["tool_calls_used"], "events": events}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", help="Run one custom question instead of the full suite")
    args = parser.parse_args()
    load_dotenv(BASE_DIR / ".env")
    load_dotenv(BASE_DIR.parent / ".env")
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("Set OPENAI_API_KEY in root .env or 4_Exercise/.env")
    graph = build_graph()
    (BASE_DIR / "architecture.mmd").write_text(graph.get_graph().draw_mermaid())
    results = {"executed_at": datetime.now(ZoneInfo("America/New_York")).isoformat(),
               "model": os.getenv("OPENAI_MODEL", "gpt-4.1-mini"), "mode": "live OpenAI + Tavily",
               "dataset": "Illustrative practice values, not verified economic statistics", "runs": []}
    output = BASE_DIR / "results" / ("custom_run.json" if args.query else "live_runs.json")
    cases = [("custom", args.query)] if args.query else CASES + [
        ("memory_first", "Compare Germany and the US GDP growth in 2024."),
        ("memory_followup", "Which one had higher inflation in that year?"),
    ]
    for name, query in cases:
        print(f"\n{name}: {query}", flush=True)
        thread_id = "memory-demo" if name.startswith("memory_") else name
        try:
            result = {"name": name, **run_turn(graph, query, thread_id)}
            print(result["answer"], flush=True)
            print("Validation:", result["validation"], flush=True)
        except Exception as exc:
            # Record type only: service exception strings can include credential-bearing URLs.
            result = {"name": name, "query": query, "error_type": type(exc).__name__}
            print(f"Run failed: {type(exc).__name__}", flush=True)
        results["runs"].append(result)
        output.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nSaved: {output}")
    if any("error_type" in run for run in results["runs"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
