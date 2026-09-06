from dotenv import load_dotenv
# 导入读取 .env 文件的函数。
from langchain_community.vectorstores import FAISS
# 导入 FAISS 向量数据库。
from langchain.agents import create_agent
from langchain_openai import OpenAIEmbeddings
# 导入 OpenAI 文本嵌入模型。
from langchain_core.tools import create_retriever_tool

load_dotenv()
# 加载 .env 中的 OPENAI_API_KEY。

embeddings = OpenAIEmbeddings(model="text-embedding-3-large",)

texts = [
    "I love apples.",
    "I enjoy oranges.",
    "I think pears taste very good.",
    "I hate bananas.",
    "I dislike raspberries.",
    "I despise mangos.",
    "I like strawberries.",
    "I love Linux.",
    "I hate Windows.",
]
# 创建用于相似度搜索的文本列表。

vector_store = FAISS.from_texts(
    texts, embedding=embeddings, ) # 将文本转换为向量并保存到 FAISS。

print( vector_store.similarity_search(
        "What fruits does the person like?",k=3, ))
print( vector_store.similarity_search(
        "What fruits does the person hate?", k=3  ))

retriever = vector_store.as_retriever(search_kwargs={"k": 3})
# 创建一个检索器，用于从向量数据库中检索与查询最相似的文本。

retriever_tool = create_retriever_tool(retriever, 
                                       name="kb_search", 
                                       description="search the small product/fruit knowledge base for information.")
# 创建一个工具，使用检索器来检索关于水果的信息.

agent = create_agent(
    model="gpt-4.1-mini",
    tools=[retriever_tool],
    system_prompt=(
        "You are a helpful assistant. For questions about Macs, apples, or laptops, "
        "first call the kb_search tool to retrieve context, then answer succinctly. Maybe you have to use it multiple times before answering."
    ),
    # 要求 Agent 回答前先调用 kb_search 检索知识库。
)
# 创建能够使用向量数据库检索工具的 Agent。

result = agent.invoke( {
        "messages": [ {
                "role": "user",
                "content":
                    "What three fruits does the person like and what three fruits "
                    "does the person dislike?" }]
    })
# 向 Agent 提问；Agent 可以调用 kb_search 检索向量数据库。

print(result)
# 打印包含工具调用和中间消息的完整运行结果。

print(result["messages"][-1].content)
# 只打印 Agent 返回的最后一条回答正文。
