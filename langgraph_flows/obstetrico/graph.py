"""Grafo do fluxo Obstétrico.

Dados da gestante → Avaliação de risco → Orientações → Exames →
Alertas de urgência → Acompanhamento

Edge condicional: a verificação de alertas pode interromper o fluxo
normal — se um alerta crítico é detectado, pula direto para o
acompanhamento (que sinaliza encaminhamento imediato).
"""

from langgraph.graph import StateGraph, END

from .state import ObstetricoState
from .nodes import (
    avaliar_risco_gestacional,
    gerar_orientacoes,
    agendar_exames,
    verificar_alertas_urgencia,
    configurar_acompanhamento,
)


def _rotear_alerta(state: ObstetricoState) -> str:
    """Se há alerta crítico, atalha para o acompanhamento (que orienta urgência)."""
    if state.get("alerta_urgencia"):
        return "configurar_acompanhamento"
    return "gerar_orientacoes"


def build_graph():
    """Monta e compila o grafo obstétrico."""
    builder = StateGraph(ObstetricoState)

    builder.add_node("avaliar_risco_gestacional", avaliar_risco_gestacional)
    builder.add_node("verificar_alertas_urgencia", verificar_alertas_urgencia)
    builder.add_node("gerar_orientacoes", gerar_orientacoes)
    builder.add_node("agendar_exames", agendar_exames)
    builder.add_node("configurar_acompanhamento", configurar_acompanhamento)

    # Verificamos os alertas LOGO APÓS a avaliação de risco — sinais críticos
    # devem cortar o fluxo o quanto antes.
    builder.set_entry_point("avaliar_risco_gestacional")
    builder.add_edge("avaliar_risco_gestacional", "verificar_alertas_urgencia")

    builder.add_conditional_edges(
        "verificar_alertas_urgencia",
        _rotear_alerta,
        {
            "configurar_acompanhamento": "configurar_acompanhamento",
            "gerar_orientacoes": "gerar_orientacoes",
        },
    )

    builder.add_edge("gerar_orientacoes", "agendar_exames")
    builder.add_edge("agendar_exames", "configurar_acompanhamento")
    builder.add_edge("configurar_acompanhamento", END)

    return builder.compile()


graph = build_graph()


def run_obstetrico_flow(
    idade: int,
    semanas_gestacao: int,
    paridade: str,
    queixas: str,
    comorbidades: str = "",
) -> ObstetricoState:
    """Executa o fluxo obstétrico com os dados da gestante."""
    estado_inicial: ObstetricoState = {
        "idade": idade,
        "semanas_gestacao": semanas_gestacao,
        "paridade": paridade,
        "queixas": queixas,
        "comorbidades": comorbidades,
    }
    return graph.invoke(estado_inicial)


if __name__ == "__main__":
    resultado = run_obstetrico_flow(
        idade=32,
        semanas_gestacao=28,
        paridade="G2P1A0",
        queixas="Dores nas costas e leve inchaço nos tornozelos",
        comorbidades="",
    )
    print("=== FLUXO OBSTÉTRICO ===")
    for chave, valor in resultado.items():
        print(f"\n[{chave.upper()}]\n{valor}")
