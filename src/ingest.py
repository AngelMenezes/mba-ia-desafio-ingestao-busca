import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_postgres import PGVector

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
for k in ("OPENAI_API_KEY", "PGVECTOR_URL","PGVECTOR_COLLECTION"):
    if not os.getenv(k):
        raise RuntimeError(f"Environment variable {k} is not set")
    
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# PDF_PATH = os.getenv("PDF_PATH")
# PGVECTOR_URL = os.getenv("PGVECTOR_URL")
# PG_VECTOR_COLLECTION = os.getenv("PGVECTOR_COLLECTION")

def load_pdf(pdf_path: Path):
    loader = PyPDFLoader(str(pdf_path))
    docs = loader.load()
    return docs

def split_docs(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        add_start_index=False
    )
    splits = splitter.split_documents(docs)
    if not splits:
        raise SystemExit(0)
    return splits

def enrich_documents(splits):
    if not splits:
        raise SystemExit(0)
    
    enriched = [
        Document(
            page_content=d.page_content,
            metadata={k: v for k, v in d.metadata.items() if v not in ("", None)}
        ) 
        for d in splits
    ]
    return enriched

def build_embeddings():
    model_name = os.getenv("OPENAI_MODEL", "text-embedding-3-small")
    embeddings = OpenAIEmbeddings(model=model_name)
    return embeddings    

def build_vector_store(embeddings):
    collection = os.getenv("PGVECTOR_COLLECTION")
    conn = os.getenv("PGVECTOR_URL")
    store = PGVector(
        embeddings=embeddings,
        collection_name=collection,
        connection=conn,
        use_jsonb=True
    )
    return store

def ingest_pdf():
    PDF_PATH = os.getenv("PDF_PATH")
    if not PDF_PATH:
        raise ValueError("Defina a variável de ambiente PDF_PATH com o caminho do PDF.")
    
    docs = load_pdf(Path(PDF_PATH))
    splits = split_docs(docs)
    enriched = enrich_documents(splits)

    ids = [f"doc-{i}" for i in range(len(enriched))]

    embeddings = build_embeddings()

    store = build_vector_store(embeddings)
    store.add_documents(documents=enriched, ids=ids)

if __name__ == "__main__":
    ingest_pdf()