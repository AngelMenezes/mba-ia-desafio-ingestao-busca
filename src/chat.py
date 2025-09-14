from search import search_prompt

def main():
    question = input("PERGUNTA: ")
    resposta = search_prompt(question)

    if not resposta:
        print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
        return
    
    print("RESPOSTA: ", resposta)

if __name__ == "__main__":
    main()