import requests
from pathlib import Path
# 导入 requests 库，用来向天气网站发送 HTTP 请求。
from dotenv import load_dotenv
# 导入 load_dotenv，用来读取 .env 文件中的环境变量，api_key。

from langchain.agents import create_agent
# 导入 create_agent，用来创建一个 LangChain Agent。
from langchain.tools import tool
# 导入 tool decorator，用来把普通 Python 函数转换成Agent可以调用的工具。


@tool("get_weather", description="Return weather information for a given city", return_direct=False)
# 把下面的 get_weather 函数注册为名为 get_weather 的 LangChain tool，并提供描述信息。return_direct=False 表示tool的返回值不会直接返回给用户，而是经过Agent处理后再返回。

def get_weather(city: str):
    # 定义查询天气的函数；city: str 表示 city 参数应该是字符串。

    response = requests.get(f"https://wttr.in/{city}?format=j1", timeout=10)
    # 向 wttr.in 发送请求，查询指定城市的天气，并设置最长等待时间为 10 秒。

    return response.json()
    # 把网站返回的 JSON 天气数据转换成 Python 对象并返回。


load_dotenv(Path(__file__).resolve().parent.parent / ".env")
# 读取项目根目录中的 .env 文件，把里面的配置加载为环境变量。

agent = create_agent(
# 开始创建 LangChain Agent，并将创建结果保存到 agent 变量。

    model="gpt-4.1-mini",
    # 指定Agent使用的 OpenAI 模型。

    tools=[get_weather],
    # 把 get_weather 工具提供给Agent，让它可以主动查询天气。

    system_prompt="You are a helpful weather assistant, who always cracks jokes and is humorous while remaining helpful.",
    # 设置系统提示词，要求Agent成为一个幽默但有帮助的天气助手。

)
# 完成Agent的创建.


response = agent.invoke({
# 调用Agent，并把完整的运行结果保存到 response 变量。

    "messages": [
    # messages 是发送给Agent的对话消息列表。

        {
        # 创建一条新的对话消息。

            "role": "user",
            # 表示这条消息来自用户。

            "content": "What is the weather like in Vienna?",
            # 用户询问奥地利维也纳的天气情况。

        }
        # 完成这一条用户消息。

    ]
    # 完成消息列表。

})
# 完成本次Agent调用。


print(response)
# 打印完整响应，包括用户消息、工具调用、天气工具结果和模型回答。


print(response["messages"][-1].content)
# 获取消息列表中的最后一条消息，并只打印Agent最终回答的正文。