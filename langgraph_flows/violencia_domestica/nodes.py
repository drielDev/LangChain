"""Nodes do fluxo de Detecção de Violência Doméstica.

Todos os nodes operam em modo confidencial: nenhum dado da paciente
é registrado em log em texto puro. O LLM é instruído a manter linguagem
acolhedora, não-julgadora e baseada em protocolos públicos de saúde.
"""

from langgraph_flows.shared import default_llm, invoke_llm, safe_log
from .state import ViolenciaState


FLOW_NAME = "violencia_domestica"


def identificar_sinais_alerta(state: ViolenciaState) -> ViolenciaState:
    """Identifica sinais de alerta de violência no relato."""
    relato = state.get("relato", "")

    system_prompt = (
        "Você é uma profissional da saúde treinada em identificação de "
        "violência doméstica, baseada em protocolos do Ministério da Saúde "
        "e da OMS. Identifique sinais de alerta presentes no relato. "
        "Liste os sinais identificados, um por linha, começando com '- '. "
        "Use linguagem técnica, acolhedora e não-julgadora. "
        "Nunca culpabilize a paciente."
    )

    try:
        resposta = invoke_llm(default_llm, system_prompt, relato)
        sinais = [
            linha.lstrip("- ").strip()
            for linha in resposta.splitlines()
            if linha.strip().startswith("-")
        ]
        safe_log(FLOW_NAME, "identificar_sinais_alerta", "ok", confidential=True)
        return {**state, "sinais_alerta": sinais, "modo_confidencial": True}
    except Exception as e:
        return {**state, "erro": f"identificar_sinais_alerta: {str(e)}"}


def avaliar_risco(state: ViolenciaState) -> ViolenciaState:
    """Avalia o nível de risco com base nos sinais detectados."""
    sinais = state.get("sinais_alerta", [])

    system_prompt = (
        "Você é uma assistente em saúde da mulher treinada em avaliação "
        "de risco de violência doméstica. Com base nos sinais identificados, "
        "retorne APENAS uma linha no formato exato:\n"
        "NIVEL_RISCO=<baixo|moderado|alto>\n"
        "Considere alto: ameaça à vida, uso de arma, estrangulamento prévio, "
        "gestação, isolamento severo, escalada recente."
    )

    user_content = "Sinais identificados:\n" + "\n".join(f"- {s}" for s in sinais)

    try:
        resposta = invoke_llm(default_llm, system_prompt, user_content).strip()

        nivel = "moderado"
        for parte in resposta.split(";"):
            if "NIVEL_RISCO" in parte.upper():
                nivel = parte.split("=")[-1].strip().lower()

        if nivel not in {"baixo", "moderado", "alto"}:
            nivel = "moderado"

        safe_log(FLOW_NAME, "avaliar_risco", "ok", confidential=True)
        return {**state, "nivel_risco": nivel}
    except Exception as e:
        return {**state, "erro": f"avaliar_risco: {str(e)}"}


def definir_protocolo_seguranca(state: ViolenciaState) -> ViolenciaState:
    """Define o protocolo de segurança aplicável ao caso."""
    nivel = state.get("nivel_risco", "moderado")

    system_prompt = (
        "Você é uma profissional do serviço de proteção à mulher. "
        "Com base no nível de risco informado, descreva um plano de "
        "segurança em até 5 itens curtos, em português brasileiro, "
        "começando cada item com '- '. Inclua orientações práticas como "
        "contatos de emergência (Disque 180, 190), preparação de uma "
        "bolsa de saída, rede de apoio confiável. "
        "Reforce que a paciente não está sozinha e não tem culpa."
    )

    user_content = f"Nível de risco: {nivel}"

    try:
        protocolo = invoke_llm(default_llm, system_prompt, user_content)
        safe_log(FLOW_NAME, "definir_protocolo_seguranca", "ok", confidential=True)
        return {**state, "protocolo_seguranca": protocolo}
    except Exception as e:
        return {**state, "erro": f"definir_protocolo_seguranca: {str(e)}"}


def acionar_equipe_especializada(state: ViolenciaState) -> ViolenciaState:
    """Aciona a equipe especializada quando aplicável."""
    nivel = state.get("nivel_risco", "moderado")

    if nivel == "alto":
        mensagem = (
            "🚨 EQUIPE ESPECIALIZADA ACIONADA — Assistente social, "
            "psicóloga e enfermagem foram notificadas. Disque 180 informado "
            "à paciente. Considerar acionamento da Polícia Militar (190) se "
            "houver risco iminente à vida."
        )
        acionada = True
    elif nivel == "moderado":
        mensagem = (
            "⚠️ Encaminhamento para assistência social e psicológica. "
            "Disque 180 informado. Seguimento próximo agendado."
        )
        acionada = True
    else:
        mensagem = (
            "📋 Caso registrado em observação. Oferecer informações sobre "
            "Disque 180 e rede de apoio."
        )
        acionada = False

    safe_log(FLOW_NAME, "acionar_equipe", f"nivel={nivel}", confidential=True)
    return {**state, "equipe_acionada": acionada, "protocolo_seguranca":
            (state.get("protocolo_seguranca", "") + "\n\n" + mensagem).strip()}


def registrar_documentacao(state: ViolenciaState) -> ViolenciaState:
    """Gera registro técnico do atendimento, sem dados identificáveis."""
    nivel = state.get("nivel_risco", "moderado")
    qtd_sinais = len(state.get("sinais_alerta", []))
    equipe = state.get("equipe_acionada", False)

    documentacao = (
        f"Registro técnico (confidencial):\n"
        f"- Nível de risco avaliado: {nivel}\n"
        f"- Quantidade de sinais identificados: {qtd_sinais}\n"
        f"- Equipe especializada acionada: {'Sim' if equipe else 'Não'}\n"
        f"- Protocolo de segurança fornecido: Sim\n"
        f"- Dados identificáveis: armazenar apenas em prontuário físico seguro."
    )

    safe_log(FLOW_NAME, "registrar_documentacao", "ok", confidential=True)
    return {**state, "documentacao": documentacao}


def definir_seguimento(state: ViolenciaState) -> ViolenciaState:
    """Define a estratégia de seguimento do caso."""
    nivel = state.get("nivel_risco", "moderado")

    seguimento_por_nivel = {
        "alto": (
            "Seguimento em 24-48h. Contato ativo da equipe. "
            "Reavaliação semanal pelos próximos 30 dias."
        ),
        "moderado": (
            "Seguimento em 7 dias. Contato da equipe psicossocial. "
            "Reavaliação quinzenal pelos próximos 60 dias."
        ),
        "baixo": (
            "Seguimento de rotina em 30 dias. Manter canal aberto "
            "para retorno da paciente."
        ),
    }

    seguimento = seguimento_por_nivel.get(nivel, seguimento_por_nivel["moderado"])
    safe_log(FLOW_NAME, "definir_seguimento", nivel, confidential=True)
    return {**state, "seguimento": seguimento}
