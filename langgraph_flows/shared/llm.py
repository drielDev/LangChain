"""
LLM compartilhado entre todos os fluxos LangGraph.

Reaproveita a configuração já existente em `langchain_assistant.config`
para manter um único ponto de configuração do projeto.
"""

from langchain_groq import ChatGroq

from langchain_assistant.config import (
    GROQ_API_KEY,
    MODEL_NAME,
    TEMPERATURE,
)


def build_llm(temperature: float = TEMPERATURE) -> ChatGroq:
    """Cria uma instância do LLM com a configuração padrão do projeto.

    O parâmetro `temperature` pode ser ajustado por fluxo quando necessário
    (ex.: fluxos clínicos pedem temperatura mais baixa).
    """
    return ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name=MODEL_NAME,
        temperature=temperature,
    )


# Instância padrão reutilizável
default_llm = build_llm()
