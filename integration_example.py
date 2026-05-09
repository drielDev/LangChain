from src.langchain_assistant import (
    generate_response,
    reset_conversation
)


def main():

    print("Sistema iniciado.")

    while True:

        user_input = input("\nUsuário: ")

        if user_input.lower() == "sair":
            break

        if user_input.lower() == "reset":
            reset_conversation()
            print("Memória resetada.")
            continue

        response = generate_response(user_input)

        print(f"\nAssistente: {response}")


if __name__ == "__main__":
    main()