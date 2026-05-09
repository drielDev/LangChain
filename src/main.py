from langchain_assistant import (
    generate_response,
    reset_conversation
)


print("Assistente iniciado!")

while True:

    user_input = input("\nVocê: ")

    if user_input.lower() == "sair":
        break

    if user_input.lower() == "reset":
        reset_conversation()
        print("Conversa resetada.")
        continue

    response = generate_response(user_input)

    print(f"\nAssistente: {response}")