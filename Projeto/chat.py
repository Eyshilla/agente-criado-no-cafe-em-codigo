import logging
import os
import sys

from dotenv import load_dotenv

from agent_factory import create_agent

EXIT_COMMANDS = {"sair", "exit", "quit"}

# Silencia os logs de retry do Strands; o erro real é exibido pelo handler abaixo
logging.getLogger("strands").setLevel(logging.CRITICAL)


def main() -> None:
    load_dotenv()

    if not os.getenv("OPENAI_API_KEY"):
        print("Erro: OPENAI_API_KEY não encontrada.")
        print("Crie um arquivo .env a partir do .env.example e preencha sua chave da OpenAI.")
        sys.exit(1)

    agent = create_agent()
    print("Chat iniciado. Digite 'sair' para encerrar.\n")

    while True:
        try:
            user_input = input("Você: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nAté logo!")
            break

        if not user_input:
            continue
        if user_input.lower() in EXIT_COMMANDS:
            print("Até logo!")
            break

        try:
            response = agent(user_input)
            print(f"\nAgente: {response}\n")
        except Exception as exc:
            print(f"\nErro ao chamar o modelo: {exc}\n")


if __name__ == "__main__":
    main()
