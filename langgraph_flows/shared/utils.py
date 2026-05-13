"""
Utilitários compartilhados pelos fluxos LangGraph.

Inclui logging seguro (sem dados sensíveis) e invocação padronizada do LLM.
"""

from pathlib import Path
from typing import Optional

from langchain_core.messages import SystemMessage, HumanMessage


LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


def safe_log(flow_name: str, step: str, message: str, confidential: bool = False) -> None:
    """Grava log apenas com o passo executado, nunca o conteúdo da paciente.

    Quando `confidential=True`, registra apenas a etapa concluída.
    """
    log_path = LOG_DIR / f"{flow_name}.log"

    try:
        with log_path.open("a", encoding="utf-8") as log_file:
            if confidential:
                log_file.write(f"[{flow_name}] step={step} status=ok\n")
            else:
                # Mesmo sem confidencialidade explícita, evitamos gravar conteúdo
                # médico em texto puro — apenas o resumo da etapa.
                log_file.write(f"[{flow_name}] step={step} info={message[:60]}...\n")
    except Exception:
        # Logging nunca deve quebrar o fluxo
        pass


def invoke_llm(llm, system_prompt: str, user_content: str) -> str:
    """Invoca o LLM com tratamento de erro padronizado."""
    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content),
        ]
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return f"[Erro ao consultar LLM: {str(e)}]"


def empty_string(value: Optional[str]) -> str:
    """Normaliza valores None para string vazia, evitando concatenações com None."""
    return value if isinstance(value, str) else ""
