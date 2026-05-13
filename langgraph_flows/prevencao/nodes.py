"""Nodes do fluxo de Prevenção."""

from datetime import datetime, timedelta

from langgraph_flows.shared import default_llm, invoke_llm, safe_log
from .state import PrevencaoState


FLOW_NAME = "prevencao"


def identificar_exames_devidos(state: PrevencaoState) -> PrevencaoState:
    """Identifica exames preventivos pendentes para a paciente."""
    idade = state.get("idade", 0)
    historico = state.get("historico_familiar", "")
    ultimos = state.get("ultimos_exames", "")
    fatores = state.get("fatores_risco", "")

    system_prompt = (
        "Você é uma médica preventivista em saúde da mulher, baseada em "
        "protocolos do Ministério da Saúde e da Febrasgo. Liste de 3 a 6 "
        "exames preventivos pendentes ou recomendados, um por linha, "
        "começando com '- '. Use nomenclatura brasileira padrão "
        "(Papanicolau, mamografia, densitometria, etc)."
    )

    user_content = (
        f"Idade: {idade}\n"
        f"Histórico familiar: {historico}\n"
        f"Últimos exames realizados: {ultimos}\n"
        f"Fatores de risco: {fatores}"
    )

    try:
        resposta = invoke_llm(default_llm, system_prompt, user_content)
        exames = [
            linha.lstrip("- ").strip()
            for linha in resposta.splitlines()
            if linha.strip().startswith("-")
        ]
        safe_log(FLOW_NAME, "identificar_exames_devidos", f"qtd={len(exames)}")
        return {**state, "exames_devidos": exames}
    except Exception as e:
        return {**state, "erro": f"identificar_exames_devidos: {str(e)}"}


def gerar_orientacoes_preventivas(state: PrevencaoState) -> PrevencaoState:
    """Gera orientações preventivas personalizadas."""
    idade = state.get("idade", 0)
    fatores = state.get("fatores_risco", "")
    exames = state.get("exames_devidos", [])

    system_prompt = (
        "Você é uma assistente em saúde da mulher. Gere orientações "
        "preventivas personalizadas em português brasileiro: hábitos "
        "saudáveis, autocuidado, sinais de alerta a observar. "
        "Mensagem acolhedora, clara e motivadora. NÃO prescreva "
        "medicamentos."
    )

    user_content = (
        f"Idade: {idade}\n"
        f"Fatores de risco: {fatores}\n"
        f"Exames pendentes: {', '.join(exames) if exames else 'nenhum identificado'}"
    )

    try:
        orientacoes = invoke_llm(default_llm, system_prompt, user_content)
        safe_log(FLOW_NAME, "gerar_orientacoes_preventivas", "ok")
        return {**state, "orientacoes_preventivas": orientacoes}
    except Exception as e:
        return {**state, "erro": f"gerar_orientacoes_preventivas: {str(e)}"}


def agendar_automatico(state: PrevencaoState) -> PrevencaoState:
    """Gera o agendamento automático para os exames pendentes."""
    exames = state.get("exames_devidos", [])

    if not exames:
        agendamento = "Nenhum exame pendente identificado."
    else:
        hoje = datetime.now()
        linhas = ["📅 Agendamento automático sugerido:"]
        for i, exame in enumerate(exames, start=1):
            # Espaçamos os agendamentos em intervalos quinzenais
            data = hoje + timedelta(days=15 * i)
            linhas.append(f"  - {exame}: {data.strftime('%d/%m/%Y')}")
        agendamento = "\n".join(linhas)

    safe_log(FLOW_NAME, "agendar_automatico", f"qtd={len(exames)}")
    return {**state, "agendamento_automatico": agendamento}


def configurar_lembretes(state: PrevencaoState) -> PrevencaoState:
    """Configura lembretes personalizados para a paciente."""
    exames = state.get("exames_devidos", [])

    lembretes = []
    for exame in exames:
        lembretes.append(
            f"Lembrete: realize o exame '{exame}' conforme agendamento. "
            "Avisaremos novamente 3 dias antes."
        )

    # Lembrete geral de autocuidado
    lembretes.append(
        "Lembrete mensal: autoexame das mamas e atenção a sinais de alerta."
    )

    safe_log(FLOW_NAME, "configurar_lembretes", f"qtd={len(lembretes)}")
    return {**state, "lembretes": lembretes}
