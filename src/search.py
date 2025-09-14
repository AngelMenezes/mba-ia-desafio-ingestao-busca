import os
from dotenv import load_dotenv
from ingest import build_embeddings, build_vector_store

from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""
load_dotenv()

def search_prompt(question=None):
    for k in ("OPENAI_API_KEY", "PGVECTOR_URL","PGVECTOR_COLLECTION"):
        if not os.getenv(k):
            raise RuntimeError(f"Environment variable {k} is not set")
        
    embeddings = build_embeddings()

    store = build_vector_store(embeddings)

    results = store.similarity_search_with_score(question, k=10)
    if not results or len(results) == 0:
        raise RuntimeError("Nenhum documento encontrado na busca semelhante.")
    
    sorted_results = sorted(results, key=lambda x: -x[1])
    context = "\n\n".join([doc.page_content for doc, _ in sorted_results])

    add_context = RunnableLambda(lambda summary: {"contexto": context, "pergunta": question})

    template_prompt = PromptTemplate(
        input_variables=["contexto", "pergunta"], 
        template=PROMPT_TEMPLATE
    )

    llm_en = ChatOpenAI(model="gpt-5-nano", temperature=0)
    chain = add_context | template_prompt | llm_en | StrOutputParser()

    return chain.invoke({"pergunta":question})
