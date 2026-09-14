from pathlib import Path
from typing import List, Any
from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders.excel import UnstructuredExcelLoader
from langchain_community.document_loaders import JSONLoader


def load_all_documents(data_dir: str) -> List[Any]:
    """
    Load all supported files from the data directory and convert to LangChain document structure.
    Supported: PDF, TXT, CSV, SQL (read as text, never executed).
    """
    # Resolve relative paths from the current working directory.
    data_path = Path(data_dir).resolve()
    print(f"[DEBUG] Data path: {data_path}")
    if not data_path.exists():
        raise FileNotFoundError(f"Data directory does not exist: {data_path}")
    if not data_path.is_dir():
        raise NotADirectoryError(f"Expected a data directory: {data_path}")
    documents = []

    # PDF files
    pdf_files = list(data_path.glob("**/*.pdf"))
    print(f"[DEBUG] Found {len(pdf_files)} PDF files: {[str(f) for f in pdf_files]}")
    for pdf_file in pdf_files:
        print(f"[DEBUG] Loading PDF: {pdf_file}")
        try:
            # 创建一个加载器对象，此时还没有加载出文档内容
            loader = PyPDFLoader(str(pdf_file))
            # 这一行才真正读取 PDF、提取文本
            loaded = loader.load()
            print(f"[DEBUG] Loaded {len(loaded)} PDF docs from {pdf_file}")
            documents.extend(loaded)
        except Exception as e:
            print(f"[ERROR] Failed to load PDF {pdf_file}: {e}")
    

    # TXT files
    txt_files = list(data_path.glob("**/*.txt"))
    print(f"[DEBUG] Found {len(txt_files)} TXT files")
    for txt_file in txt_files:
        try:
            loader = TextLoader(str(txt_file), encoding="utf-8-sig")
            loaded = loader.load()
            print(f"[DEBUG] Loaded {len(loaded)} TXT docs from {txt_file}")
            documents.extend(loaded)
        except Exception as e:
            print(f"[ERROR] Failed to load TXT {txt_file}: {e}")

    # CSV files: CSVLoader creates one document per data row.
    csv_files = list(data_path.glob("**/*.csv"))
    print(f"[DEBUG] Found {len(csv_files)} CSV files")
    for csv_file in csv_files:
        try:
            loader = CSVLoader(str(csv_file), encoding="utf-8-sig")
            loaded = loader.load()
            print(f"[DEBUG] Loaded {len(loaded)} CSV docs from {csv_file}")
            documents.extend(loaded)
        except Exception as e:
            print(f"[ERROR] Failed to load CSV {csv_file}: {e}")

    # SQL files: read scripts as reference text; do not execute SQL.
    sql_files = list(data_path.glob("**/*.sql"))
    print(f"[DEBUG] Found {len(sql_files)} SQL files")
    for sql_file in sql_files:
        try:
            loader = TextLoader(str(sql_file), encoding="utf-8-sig")
            loaded = loader.load()
            print(f"[DEBUG] Loaded {len(loaded)} SQL docs from {sql_file}")
            documents.extend(loaded)
        except Exception as e:
            print(f"[ERROR] Failed to load SQL {sql_file}: {e}")

    return documents # list
