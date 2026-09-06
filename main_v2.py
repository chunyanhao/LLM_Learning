import requests
# 导入 requests 库，用来向天气网站发送 HTTP 请求。
from dotenv import load_dotenv
# 导入 load_dotenv，用来读取 .env 文件中的环境变量，api_key。


from langchain.chat_models import init_chat_model
# 导入创建聊天模型的函数。

from langchain.messages import AIMessage, HumanMessage, SystemMessage
# 导入系统消息、用户消息和 AI 消息类型。

load_dotenv()
# 读取 .env 中的 OPENAI_API_KEY。

model = init_chat_model(
    model="gpt-4.1-mini",
    temperature=0.1,
)
# 创建聊天模型；较低的 temperature 会让回答更加稳定。

for chunk in model.stream("What is Python?"):
    print(chunk.text, end="", flush=True)
# 流式输出 AI 的回答，实时打印每个文本块。