from dataclasses import dataclass

import requests
# 用来向天气网站发送 HTTP 请求。
from pathlib import Path
from dotenv import load_dotenv
# 读取 .env 文件中的环境变量，api_key。

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
# 读取项目根目录中的 .env 文件，把里面的配置加载为环境变量。

from langchain.agents import create_agent
# 创建 LangChain Agent
from langchain.chat_models import init_chat_model
# 初始化聊天模型
from langchain.tools import ToolRuntime, tool 
#创建工具并访问工具运行上下文。
from langgraph.checkpoint.memory import InMemorySaver
# 临时保存 Agent 的对话状态。

@dataclass
# 将 Context 类定义为数据类。

class Context:
    # 保存 Agent 运行时所需的上下文数据。
    user_id: str
    # 保存当前用户的唯一标识。

@dataclass
# 将 ResponseFormat 类定义为数据类。

class ResponseFormat:
    # 定义 Agent 最终响应必须遵循的数据结构。
    summary: str
    temperature_celsius: float
    temperature_fahrenheit: float
    humidity: float 


@tool("get_weather", description="Return weather information for a given city", return_direct=False)


def get_weather(city: str):
    # 定义查询天气的函数；city: str 表示 city 参数应该是字符串。

    response = requests.get(f"https://wttr.in/{city}?format=j1", timeout=10)
    # 向 wttr.in 发送请求，查询指定城市的天气，并设置最长等待时间为 10 秒。

    return response.json()
    # 把网站返回的 JSON 天气数据转换成 Python 对象并返回。

@tool( "locate_user", description="Look up a user's city based on the context",)
# 把 locate_user 函数注册为 Agent 可以调用的工具。

def locate_user(runtime: ToolRuntime[Context]):
    # 定义查询用户城市的工具，根据user_id 匹配城市,并通过 ToolRuntime 获取运行上下文。
    match runtime.context.user_id:
        case "ABC123":
            return "Vienna"
        case "XYZ456":
            return "London"
        case "HJKL111":
            return "Paris"
        case _:
            return "Unknown"

model = init_chat_model("gpt-4.1-mini", temperature=0.3)
checkpointer = InMemorySaver()


agent = create_agent(
# 开始创建 LangChain Agent，并将创建结果保存到 agent 变量。

    model=model,
    # 指定Agent使用的 OpenAI 模型。

    tools=[get_weather, locate_user],
    # 把 get_weather 工具提供给Agent，让它可以主动查询天气。

    system_prompt="You are a helpful weather assistant, who always cracks jokes and is humorous while remaining helpful.",
    # 设置系统提示词，要求Agent成为一个幽默但有帮助的天气助手。
    context_schema=Context,
    response_format=ResponseFormat,
    checkpointer=checkpointer,
)
# 完成Agent的创建.

config = {
    "configurable": {
        "thread_id": '1'  } }

response = agent.invoke(
    {
# 调用Agent，并把完整的运行结果保存到 response 变量。

    "messages": [
    # messages 是发送给Agent的对话消息列表。
        {
        # 创建一条新的对话消息。
            "role": "user",
            # 表示这条消息来自用户。
            "content": "What is the weather like in Vienna?"
            # 用户询问奥地利维也纳的天气情况。
        }
    ]

    }, 
    config=config, 
    context=Context(user_id="ABC123"))
# 完成本次Agent调用。


print(response['structured_response'])
print(response['structured_response'].summary)
print(response['structured_response'].temperature_celsius)
