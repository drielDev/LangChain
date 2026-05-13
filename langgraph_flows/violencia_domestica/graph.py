"""Grafo do fluxo de Detecção de Violência Doméstica.

Sinais de alerta → Avaliação de risco → Protocolo de segurança →
Acionamento de equipe → Documentação segura → Seguimento

Edge condicional: se o risco for alto, o acionamento da equipe ocorre
ANTES de qualquer outra etapa não essencial, garantindo prioridade.
"""

from langgraph.graph import StateGraph, END

from .state import ViolenciaState
from .nodes import (
    identificar_sinais_alerta,
    avaliar_risco,
    definir_protocolo_seguranca,
    acionar_equipe_especializada,
    registrar_documentacao,
    definir_seguimento,
)


def _rotear_risco(state: ViolenciaState) -> str:
    """Risco alto pula a etapa de protocolo e aciona equipe imediatamente."""
    if state.get("nivel_risco") == "alto":
        return "acionar_equipe_especializada"
    return "definir_protocolo_seguranca"


def build_graph():
    """Monta e compila o grafo do fluxo de violência doméstica."""
    builder = StateGraph(ViolenciaState)

    builder.add_node("identificar_sinais_alerta", identificar_sinais_alerta)
    builder.add_node("avaliar_risco", avaliar_risco)
    builder.add_node("definir_protocolo_seguranca", definir_protocolo_seguranca)
    builder.add_node("acionar_equipe_especializada", acionar_equipe_especializada)
    builder.add_node("registrar_documentacao", registrar_documentacao)
    builder.add_node("definir_seguimento", definir_seguimento)

    builder.set_entry_point("identificar_sinais_alerta")
    builder.add_edge("identificar_sinais_alerta", "avaliar_risco")

    builder.add_conditional_edges(
        "avaliar_risco",
        _rotear_risco,
        {
            "acionar_equipe_especializada": "acionar_equipe_especializada",
            "definir_protocolo_seguranca": "definir_protocolo_seguranca",
        },
    )

    # Fluxo normal: protocolo → equipe
    builder.add_edge("definir_protocolo_seguranca", "acionar_equipe_especializada")
    builder.add_edge("acionar_equipe_especializada", "registrar_documentacao")
    builder.add_edge("registrar_documentacao", "definir_seguimento")
    builder.add_edge("definir_seguimento", END)

    return builder.compile()


graph = build_graph()


def run_violencia_flow(relato: str) -> ViolenciaState:
    """Executa o fluxo completo a partir de um relato da paciente."""
    estado_inicial: ViolenciaState = {
        "relato": relato,
        "modo_confidencial": True,
    }
    return graph.invoke(estado_inicial)


if __name__ == "__main__":
    resultado = run_violencia_flow(
        "Tenho me sentido controlada pelo meu parceiro, ele monitora "
        "minhas mensagens e já me empurrou algumas vezes durante "
        "discussões. Estou com medo."
    )
    print("=== FLUXO VIOLÊNCIA DOMÉSTICA (confidencial) ===")
    print(f"Nível de risco: {resultado.get('nivel_risco')}")
    print(f"Equipe acionada: {resultado.get('equipe_acionada')}")
    print(f"\nProtocolo:\n{resultado.get('protocolo_seguranca')}")
    print(f"\nDocumentação:\n{resultado.get('documentacao')}")
    print(f"\nSeguimento:\n{resultado.get('seguimento')}")
