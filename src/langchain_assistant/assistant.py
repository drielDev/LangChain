from langchain_groq import ChatGroq
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage
)
from pathlib import Path

from .config import (
    GROQ_API_KEY,
    MODEL_NAME,
    TEMPERATURE,
    MAX_HISTORY
)

from .prompt import SYSTEM_PROMPT


LOG_FILE = Path(__file__).with_name("logs.txt")


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


def _trim_history() -> None:
    if not isinstance(MAX_HISTORY, int) or MAX_HISTORY <= 0:
        return

    # 1 SystemMessage + (MAX_HISTORY * 2) messages (Human + AI per turn)
    max_messages = 1 + (MAX_HISTORY * 2)
    if len(conversation_history) <= max_messages:
        return

    conversation_history[:] = [conversation_history[0]] + conversation_history[-(max_messages - 1):]


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

        _trim_history()
        
        with LOG_FILE.open("a", encoding="utf-8") as log_file:
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