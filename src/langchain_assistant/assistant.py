from langchain_groq import ChatGroq
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage
)

from .config import (
    GROQ_API_KEY,
    MODEL_NAME,
    TEMPERATURE,
    MAX_HISTORY
)

from .prompt import SYSTEM_PROMPT


# =========================
# MODEL CONFIG
# =========================

llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name=MODEL_NAME,
    temperature=TEMPERATURE
)


# =========================
# MEMORY
# =========================

conversation_history = [
    SystemMessage(content=SYSTEM_PROMPT)
]


# =========================
# MAIN FUNCTIONS
# =========================

def generate_response(user_input: str) -> str:
    """
    Generate contextual response for the user.
    """
    if not user_input.strip():
        return "Por favor, digite uma pergunta válida."

    try:

        # save user message
        conversation_history.append(
            HumanMessage(content=user_input)
        )

        # generate response
        response = llm.invoke(conversation_history)

        # save assistant response
        conversation_history.append(
            AIMessage(content=response.content)
        )
        
        with open("logs.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"USER: {user_input}\n")
            log_file.write(f"BOT: {response.content}\n\n")
            
        return response.content

    except Exception as e:
        return f"Erro ao gerar resposta: {str(e)}"


def reset_conversation() -> None:
    """
    Reset conversation history.
    """

    global conversation_history

    conversation_history = [
        SystemMessage(content=SYSTEM_PROMPT)
    ]