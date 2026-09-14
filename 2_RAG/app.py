from pathlib import Path

from src.data_loader import load_all_documents
# from src.embedding import EmbeddingPipeline
from src.vectorstore import FaissVectorStore
from src.search import RAGSearch

if __name__ == "__main__":
    data_dir = Path(__file__).resolve().parent / "data"
    docs = load_all_documents(str(data_dir))

    # chunks = EmbeddingPipeline().chunk_documents(docs)
    # chunkvectors = EmbeddingPipeline().embed_chunks(chunks)

    # print(chunkvectors)

    store = FaissVectorStore('faiss_store')
    # store.build_from_documents(docs)
    store.load()

    rag_search = RAGSearch()
    query = "What is the main topic of the documents?"
    summary = rag_search.search_and_summarize(query, top_k=2)
    print('Summary:', summary)

    

