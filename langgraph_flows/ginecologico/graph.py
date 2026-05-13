"""Grafo do fluxo de Triagem Ginecológica.

Sintomas → Análise de risco → Classificação de urgência →
Sugestão de exames → Orientações iniciais → Agendamento

Edge condicional: se urgência for "imediata", pula direto para o
agendamento (pulando exames e orientações), pois o caso é emergencial.
"""

from langgraph.graph import StateGraph, END

from .state import GinecologicoState
from .nodes import (
    analisar_risco,
    classificar_urgencia,
    sugerir_exames,
    gerar_orientacoes,
    recomendar_agendamento,
)


def _rotear_urgencia(state: GinecologicoState) -> str:
    """Decide o próximo node com base na urgência classificada."""
    if state.get("urgencia") == "imediata":
        return "recomendar_agendamento"
    return "sugerir_exames"


def build_graph():
    """Monta e compila o grafo do fluxo ginecológico."""
    builder = StateGraph(GinecologicoState)

    builder.add_node("analisar_risco", analisar_risco)
    builder.add_node("classificar_urgencia", classificar_urgencia)
    builder.add_node("sugerir_exames", sugerir_exames)
    builder.add_node("gerar_orientacoes", gerar_orientacoes)
    builder.add_node("recomendar_agendamento", recomendar_agendamento)

    builder.set_entry_point("analisar_risco")
    builder.add_edge("analisar_risco", "classificar_urgencia")

    # Edge condicional: urgência imediata atalha para agendamento
    builder.add_conditional_edges(
        "classificar_urgencia",
        _rotear_urgencia,
        {
            "sugerir_exames": "sugerir_exames",
            "recomendar_agendamento": "recomendar_agendamento",
        },
    )

    builder.add_edge("sugerir_exames", "gerar_orientacoes")
    builder.add_edge("gerar_orientacoes", "recomendar_agendamento")
    builder.add_edge("recomendar_agendamento", END)

    return builder.compile()


graph = build_graph()


def run_ginecologico_flow(sintomas: str) -> GinecologicoState:
    """Executa o fluxo completo dado os sintomas relatados."""
    estado_inicial: GinecologicoState = {"sintomas": sintomas}
    return graph.invoke(estado_inicial)


if __name__ == "__main__":
    resultado = run_ginecologico_flow(
        "Tenho sentido cólicas fortes há 3 dias e um sangramento fora do período."
    )
    print("=== FLUXO GINECOLÓGICO ===")
    for chave, valor in resultado.items():
        print(f"\n[{chave.upper()}]\n{valor}")
