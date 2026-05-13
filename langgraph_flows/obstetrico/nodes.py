"""Nodes do fluxo Obstétrico."""

from langgraph_flows.shared import default_llm, invoke_llm, safe_log
from .state import ObstetricoState


FLOW_NAME = "obstetrico"


def avaliar_risco_gestacional(state: ObstetricoState) -> ObstetricoState:
    """Avalia o risco gestacional com base nos dados da gestante."""
    idade = state.get("idade", 0)
    semanas = state.get("semanas_gestacao", 0)
    paridade = state.get("paridade", "")
    queixas = state.get("queixas", "")
    comorbidades = state.get("comorbidades", "")

    system_prompt = (
        "Você é uma obstetra experiente baseada em protocolos do "
        "Ministério da Saúde. Avalie o risco gestacional e retorne "
        "DUAS partes:\n"
        "1) Uma linha de classificação no formato: "
        "CLASSIFICACAO=<habitual|alto>\n"
        "2) Em seguida, uma explicação curta e técnica em português.\n\n"
        "Considere alto risco: idade <15 ou >35, hipertensão, diabetes, "
        "histórico de aborto recorrente, gestação gemelar, "
        "pré-eclâmpsia prévia."
    )

    user_content = (
        f"Idade: {idade}\nSemanas: {semanas}\nParidade: {paridade}\n"
        f"Queixas: {queixas}\nComorbidades: {comorbidades}"
    )

    try:
        resposta = invoke_llm(default_llm, system_prompt, user_content)

        # Parser defensivo
        classificacao = "habitual"
        for linha in resposta.splitlines():
            if "CLASSIFICACAO" in linha.upper():
                valor = linha.split("=")[-1].strip().lower()
                if valor in {"habitual", "alto"}:
                    classificacao = valor
                break

        safe_log(FLOW_NAME, "avaliar_risco_gestacional", classificacao)
        return {
            **state,
            "avaliacao_risco_gestacional": resposta,
            "classificacao_risco": classificacao,
        }
    except Exception as e:
        return {**state, "erro": f"avaliar_risco_gestacional: {str(e)}"}


def gerar_orientacoes(state: ObstetricoState) -> ObstetricoState:
    """Gera orientações específicas para a fase gestacional e classificação."""
    semanas = state.get("semanas_gestacao", 0)
    classificacao = state.get("classificacao_risco", "habitual")
    queixas = state.get("queixas", "")

    system_prompt = (
        "Você é uma obstetra acolhedora. Gere orientações específicas "
        "para a gestante em português brasileiro, considerando a fase da "
        "gestação e a classificação de risco. Mensagem clara, objetiva, "
        "empática. NÃO prescreva medicamentos."
    )

    user_content = (
        f"Semanas de gestação: {semanas}\n"
        f"Classificação de risco: {classificacao}\n"
        f"Queixas atuais: {queixas}"
    )

    try:
        orientacoes = invoke_llm(default_llm, system_prompt, user_content)
        safe_log(FLOW_NAME, "gerar_orientacoes", "ok")
        return {**state, "orientacoes_especificas": orientacoes}
    except Exception as e:
        return {**state, "erro": f"gerar_orientacoes: {str(e)}"}


def agendar_exames(state: ObstetricoState) -> ObstetricoState:
    """Agenda exames apropriados ao trimestre e ao risco."""
    semanas = state.get("semanas_gestacao", 0)
    classificacao = state.get("classificacao_risco", "habitual")

    system_prompt = (
        "Você é uma obstetra. Liste de 3 a 6 exames pertinentes ao "
        "trimestre informado e à classificação de risco. Um exame por "
        "linha, começando com '- '. Use nomenclatura brasileira padrão."
    )

    user_content = f"Semanas: {semanas}\nClassificação: {classificacao}"

    try:
        resposta = invoke_llm(default_llm, system_prompt, user_content)
        exames = [
            linha.lstrip("- ").strip()
            for linha in resposta.splitlines()
            if linha.strip().startswith("-")
        ]
        safe_log(FLOW_NAME, "agendar_exames", f"qtd={len(exames)}")
        return {**state, "exames_agendados": exames}
    except Exception as e:
        return {**state, "erro": f"agendar_exames: {str(e)}"}


def verificar_alertas_urgencia(state: ObstetricoState) -> ObstetricoState:
    """Verifica se há sinais de alerta obstétrico que exigem urgência."""
    queixas = state.get("queixas", "").lower()

    sinais_criticos = [
        "sangramento", "hemorragia", "perda de líquido", "rompimento da bolsa",
        "dor de cabeça intensa", "visão turva", "convulsão", "edema súbito",
        "ausência de movimento", "dor abdominal severa", "contrações regulares",
    ]

    alertas_encontrados = [s for s in sinais_criticos if s in queixas]

    if alertas_encontrados:
        motivo = (
            "Sinais de alerta detectados: "
            + ", ".join(alertas_encontrados)
            + ". Encaminhamento imediato ao pronto-atendimento obstétrico."
        )
        safe_log(FLOW_NAME, "verificar_alertas", "ALERTA")
        return {**state, "alerta_urgencia": True, "motivo_alerta": motivo}

    safe_log(FLOW_NAME, "verificar_alertas", "ok")
    return {**state, "alerta_urgencia": False, "motivo_alerta": ""}


def configurar_acompanhamento(state: ObstetricoState) -> ObstetricoState:
    """Define o plano de acompanhamento contínuo da gestante."""
    classificacao = state.get("classificacao_risco", "habitual")
    alerta = state.get("alerta_urgencia", False)

    if alerta:
        plano = (
            "🚨 ENCAMINHAMENTO IMEDIATO ao pronto-atendimento obstétrico. "
            "Reavaliação após estabilização."
        )
    elif classificacao == "alto":
        plano = (
            "Acompanhamento pré-natal de ALTO RISCO. "
            "Consultas a cada 2 semanas até 32sem, semanais a partir de 32sem. "
            "Encaminhamento para serviço de referência."
        )
    else:
        plano = (
            "Acompanhamento pré-natal de RISCO HABITUAL. "
            "Consultas mensais até 28sem, quinzenais entre 28-36sem, "
            "semanais a partir de 36sem."
        )

    safe_log(FLOW_NAME, "configurar_acompanhamento", classificacao)
    return {**state, "acompanhamento": plano}
