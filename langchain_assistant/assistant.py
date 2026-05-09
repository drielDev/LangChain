from langchain_groq import ChatGroq
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
)
from pathlib import Path
from typing import Optional

from .config import (
    GROQ_API_KEY,
    MODEL_NAME,
    TEMPERATURE,
    MAX_HISTORY,
)

from .prompt import SYSTEM_PROMPT


LOG_FILE = Path(__file__).with_name("logs.txt")


llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name=MODEL_NAME,
    temperature=TEMPERATURE,
)


class AssistantSession:
    def __init__(
        self,
        *,
        llm_instance=llm,
        system_prompt: str = SYSTEM_PROMPT,
        max_history: int = MAX_HISTORY,
        log_file: Optional[Path] = LOG_FILE,
    ) -> None:
        self.llm = llm_instance
        self.system_prompt = system_prompt
        self.max_history = max_history
        self.log_file = log_file

        self.conversation_history = [
            SystemMessage(content=self.system_prompt)
        ]

    def reset_conversation(self) -> None:
        self.conversation_history = [
            SystemMessage(content=self.system_prompt)
        ]

    def _trim_history(self) -> None:
        if not isinstance(self.max_history, int) or self.max_history <= 0:
            return

        max_messages = 1 + (self.max_history * 2)
        if len(self.conversation_history) <= max_messages:
            return

        self.conversation_history = [self.conversation_history[0]] + self.conversation_history[-(max_messages - 1):]

    def generate_response(self, user_input: str, *, raise_on_error: bool = False) -> str:
        if not user_input.strip():
            return "Por favor, digite uma pergunta válida."

        try:
            self.conversation_history.append(
                HumanMessage(content=user_input)
            )

            response = self.llm.invoke(self.conversation_history)

            self.conversation_history.append(
                AIMessage(content=response.content)
            )

            self._trim_history()

            if self.log_file is not None:
                with self.log_file.open("a", encoding="utf-8") as log_file:
                    log_file.write(f"USER: {user_input}\n")
                    log_file.write(f"BOT: {response.content}\n\n")

            return response.content

        except Exception as e:
            if raise_on_error:
                raise
            return f"Erro ao gerar resposta: {str(e)}"


_default_session: Optional[AssistantSession] = None


def _get_default_session() -> AssistantSession:
    global _default_session
    if _default_session is None:
        _default_session = AssistantSession()
    return _default_session


def generate_response(user_input: str, *, raise_on_error: bool = False) -> str:
    return _get_default_session().generate_response(user_input, raise_on_error=raise_on_error)


def reset_conversation() -> None:
    _get_default_session().reset_conversation()
