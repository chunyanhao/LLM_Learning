import asyncio
import os # 获取环境变量
import sys # 返回当前正在运行 client.py 的 Python interpreter 路径
# 用和当前程序同一个 Python environment 去启动 mathserver.py
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI

BASE_DIR = Path(__file__).resolve().parent


def create_mcp_client():
    # 创建一个 MCP client，而且这个 client 可以同时连接多个 MCP servers
    # 一个 client 可以管理多个 server connection
    return MultiServerMCPClient(
        {
            "math": {
                "command": sys.executable,
                "args": [str(BASE_DIR / "mathserver.py")],
                "transport": "stdio", #定义和这个server传输的方式
            },
            "weather": {
                "url": os.getenv("WEATHER_MCP_URL", "http://127.0.0.1:8000/mcp"),
                "transport": "streamable_http",#这个server有自己独立的http
            },
        }
    )


async def main():
    load_dotenv(BASE_DIR.parents[1] / ".env")
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("请在项目根目录的 .env 中设置 OPENAI_API_KEY。")

    client = create_mcp_client()
    tools = await client.get_tools() # await是async 函数的调用方法，async可以解决进程并发的问题concurrency，遇到需要等待的时候让出执行权，节省时间
    model = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o"))
    agent = create_agent(
        model=model,
        tools=tools, # 这句是整个 MCP demo 的核心， 相当于返回tools = [add，multiply,get_weather]
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
