# Desafio MBA Engenharia de Software com IA - Full Cycle

Descreva abaixo como executar a sua solução.

# Passo 1 
Preencher as informações do .env

# Passo 2 
Ler um arquivo PDF e salvar suas informações em um banco de dados PostgreSQL com extensão pgVector.

python ingest.py

# Passo 3
Permitir que o usuário faça perguntas via linha de comando (CLI) e receba respostas baseadas apenas no conteúdo do PDF.

python chat.py

# Apagar o banco rag
docker exec -it postgres_rag psql -U postgres -c "DROP DATABASE rag;"