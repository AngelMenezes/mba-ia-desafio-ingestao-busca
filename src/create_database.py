import os
from pathlib import Path
import psycopg

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
for k in ("OPENAI_API_KEY", "PGVECTOR_URL","PGVECTOR_COLLECTION"):
    if not os.getenv(k):
        raise RuntimeError(f"Environment variable {k} is not set")

def create_database():
    import re    
    url = os.getenv("PGVECTOR_URL")
    if not url:
        raise RuntimeError("PGVECTOR_URL não definida.")
        
    match = re.match(r"postgresql\+psycopg://(.*?):(.*?)@(.*?):(\d+)/(.*?)\?", url)
    if not match:
        raise RuntimeError("Formato de PGVECTOR_URL inválido.")
    user, password, host, port, dbname = match.groups()
    
    conn_str = f"host={host} port={port} user={user} password={password} dbname=postgres"
    conn = psycopg.connect(conn_str)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = 'rag'")
    exists = cur.fetchone()
    if not exists:
        cur.execute("CREATE DATABASE rag")
        print("Banco 'rag' criado com sucesso.")
    else:
        print("Banco 'rag' já existe.")
    cur.close()
    conn.close()
	