"""Grafo do fluxo de Prevenção.

Histórico → Exames devidos → Orientações preventivas →
Agendamento automático → Lembretes personalizados

Fluxo linear — não exige roteamento condicional. Cada paciente recebe
todas as etapas independentemente do histórico, pois o conteúdo é
gerado em função dos exames identificados.
"""

from langgraph.graph import StateGraph, END

from .state import PrevencaoState
from .nodes import (
    identificar_exames_devidos,
    gerar_orientacoes_preventivas,
    agendar_automatico,
    configurar_lembretes,
)


def build_graph():
    """Monta e compila o grafo de prevenção."""
    builder = StateGraph(PrevencaoState)

    builder.add_node("identificar_exames_devidos", identificar_exames_devidos)
    builder.add_node("gerar_orientacoes_preventivas", gerar_orientacoes_preventivas)
    builder.add_node("agendar_automatico", agendar_automatico)
    builder.add_node("configurar_lembretes", configurar_lembretes)

    builder.set_entry_point("identificar_exames_devidos")
    builder.add_edge("identificar_exames_devidos", "gerar_orientacoes_preventivas")
    builder.add_edge("gerar_orientacoes_preventivas", "agendar_automatico")
    builder.add_edge("agendar_automatico", "configurar_lembretes")
    builder.add_edge("configurar_lembretes", END)

    return builder.compile()


graph = build_graph()


def run_prevencao_flow(
    idade: int,
    historico_familiar: str = "",
    ultimos_exames: str = "",
    fatores_risco: str = "",
) -> PrevencaoState:
    """Executa o fluxo de prevenção com base no histórico da paciente."""
    estado_inicial: PrevencaoState = {
        "idade": idade,
        "historico_familiar": historico_familiar,
        "ultimos_exames": ultimos_exames,
        "fatores_risco": fatores_risco,
    }
    return graph.invoke(estado_inicial)


if __name__ == "__main__":
    resultado = run_prevencao_flow(
        idade=45,
        historico_familiar="Mãe teve câncer de mama aos 52 anos",
        ultimos_exames="Papanicolau em 2022, mamografia em 2021",
        fatores_risco="Tabagismo leve, sobrepeso",
    )
    print("=== FLUXO PREVENÇÃO ===")
    for chave, valor in resultado.items():
        print(f"\n[{chave.upper()}]\n{valor}")
