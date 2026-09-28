import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI

BASE_DIR = Path(__file__).resolve().parent


def create_mcp_client():
    return MultiServerMCPClient(
        {
            "math": {
                "command": sys.executable,
                "args": [str(BASE_DIR / "mathserver.py")],
                "transport": "stdio",
            },
            "weather": {
                "url": os.getenv("WEATHER_MCP_URL", "http://127.0.0.1:8000/mcp"),
                "transport": "streamable_http",
            },
        }
    )


async def main():
    load_dotenv(BASE_DIR.parents[1] / ".env")
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("请在项目根目录的 .env 中设置 OPENAI_API_KEY。")

    client = create_mcp_client()
    tools = await client.get_tools()
    model = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o"))
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=(
            "Use the math tools for calculations and the weather tool for weather. "
            "The weather tool returns demo data, not a live forecast; say so."
        ),
    )

    math_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what's (3+5)*12?"}]}
    )
    print("Math response:", math_response["messages"][-1].content)

    weather_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what's the weather in seattle"}]}
    )
    print("Weather response:", weather_response["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
