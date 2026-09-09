from pathlib import Path
from dotenv import load_dotenv
# 导入 load_dotenv，用来读取项目根目录中的 .env 文件。

from langchain_community.vectorstores import FAISS
# 导入 FAISS 向量数据库集成，用来存储和搜索文本向量。
from langchain_openai import OpenAIEmbeddings
# 导入 OpenAIEmbeddings，用来把文本转换为向量。

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
# 在创建嵌入模型前加载 OPENAI_API_KEY。

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
# 创建 OpenAI 嵌入模型。

texts = [  # 创建需要转换成向量并保存的文本列表。
    "Apple makes very good computers.",
    "I believe Apple is innovative!",
    "I love apples.",
    "I am a fan of MacBooks.",
    "I enjoy oranges.",
    "I like Lenovo Thinkpads.",
    "I think pears taste very good.",
]

vector_store = FAISS.from_texts(texts, embeddings)
# 把文本转换为向量，并将向量保存在 FAISS 向量数据库中。

print(vector_store.similarity_search("Apples are my favorite food", k=3))
