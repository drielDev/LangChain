"""Nodes do fluxo de Triagem Ginecológica."""

from langgraph_flows.shared import default_llm, invoke_llm, safe_log
from .state import GinecologicoState


FLOW_NAME = "ginecologico"


def analisar_risco(state: GinecologicoState) -> GinecologicoState:
    """Analisa os sintomas relatados e gera uma avaliação de risco preliminar."""
    sintomas = state.get("sintomas", "")

    system_prompt = (
        "Você é uma assistente clínica especializada em ginecologia. "
        "Analise os sintomas relatados pela paciente e gere uma avaliação "
        "de risco preliminar, em português brasileiro, de forma objetiva. "
        "NÃO forneça diagnóstico definitivo. NÃO prescreva medicamentos."
    )

    user_content = f"Sintomas relatados pela paciente: {sintomas}"

    try:
        analise = invoke_llm(default_llm, system_prompt, user_content)
        safe_log(FLOW_NAME, "analisar_risco", "ok")
        return {**state, "analise_risco": analise}
    except Exception as e:
        return {**state, "erro": f"analisar_risco: {str(e)}"}


def classificar_urgencia(state: GinecologicoState) -> GinecologicoState:
    """Classifica a urgência do atendimento e o nível de risco."""
    analise = state.get("analise_risco", "")
    sintomas = state.get("sintomas", "")

    system_prompt = (
        "Você é uma triagem ginecológica. Com base nos sintomas e na análise, "
        "retorne APENAS uma linha no formato exato:\n"
        "NIVEL_RISCO=<baixo|moderado|alto>;URGENCIA=<rotina|prioritaria|imediata>\n"
        "Sinais de urgência imediata: sangramento intenso, dor abdominal severa, "
        "febre alta com dor pélvica, perda de consciência, suspeita de gravidez "
        "ectópica."
    )

    user_content = f"Sintomas: {sintomas}\nAnálise: {analise}"

    try:
        resposta = invoke_llm(default_llm, system_prompt, user_content).strip()

        # Parser defensivo
        nivel = "moderado"
        urgencia = "prioritaria"
        for parte in resposta.split(";"):
            if "NIVEL_RISCO" in parte.upper():
                nivel = parte.split("=")[-1].strip().lower()
            elif "URGENCIA" in parte.upper():
                urgencia = parte.split("=")[-1].strip().lower()

        # Sanitização
        if nivel not in {"baixo", "moderado", "alto"}:
            nivel = "moderado"
        if urgencia not in {"rotina", "prioritaria", "imediata"}:
            urgencia = "prioritaria"

        safe_log(FLOW_NAME, "classificar_urgencia", f"nivel={nivel} urg={urgencia}")
        return {**state, "nivel_risco": nivel, "urgencia": urgencia}

    except Exception as e:
        return {**state, "erro": f"classificar_urgencia: {str(e)}"}


def sugerir_exames(state: GinecologicoState) -> GinecologicoState:
    """Sugere exames pertinentes aos sintomas e ao nível de risco."""
    sintomas = state.get("sintomas", "")
    nivel = state.get("nivel_risco", "moderado")

    system_prompt = (
        "Você é uma ginecologista experiente. Liste de 3 a 5 exames "
        "complementares pertinentes, em português, separados por linha, "
        "começando cada linha com '- '. Considere apenas exames de uso "
        "rotineiro em ginecologia."
    )

    user_content = f"Sintomas: {sintomas}\nNível de risco: {nivel}"

    try:
        resposta = invoke_llm(default_llm, system_prompt, user_content)
        exames = [
            linha.lstrip("- ").strip()
            for linha in resposta.splitlines()
            if linha.strip().startswith("-")
        ]
        safe_log(FLOW_NAME, "sugerir_exames", f"qtd={len(exames)}")
        return {**state, "exames_sugeridos": exames}
    except Exception as e:
        return {**state, "erro": f"sugerir_exames: {str(e)}"}


def gerar_orientacoes(state: GinecologicoState) -> GinecologicoState:
    """Gera orientações iniciais acolhedoras para a paciente."""
    sintomas = state.get("sintomas", "")
    nivel = state.get("nivel_risco", "moderado")

    system_prompt = (
        "Você é uma assistente acolhedora em saúde da mulher. "
        "Gere orientações iniciais em português brasileiro: claras, objetivas, "
        "seguras e empáticas. Reforce a importância de avaliação médica "
        "presencial. Não prescreva medicamentos."
    )

    user_content = (
        f"Sintomas: {sintomas}\nNível de risco: {nivel}\n"
        "Gere orientações iniciais para a paciente."
    )

    try:
        orientacoes = invoke_llm(default_llm, system_prompt, user_content)
        safe_log(FLOW_NAME, "gerar_orientacoes", "ok")
        return {**state, "orientacoes_iniciais": orientacoes}
    except Exception as e:
        return {**state, "erro": f"gerar_orientacoes: {str(e)}"}


def recomendar_agendamento(state: GinecologicoState) -> GinecologicoState:
    """Recomenda o tipo de agendamento conforme a urgência classificada."""
    urgencia = state.get("urgencia", "prioritaria")

    mapa = {
        "imediata": (
            "🚨 ATENDIMENTO IMEDIATO — Encaminhe a paciente para o "
            "pronto-atendimento ginecológico ou emergência hospitalar AGORA."
        ),
        "prioritaria": (
            "⚠️ Agendamento prioritário — Consulta ginecológica em até 72h."
        ),
        "rotina": (
            "📅 Agendamento de rotina — Consulta ginecológica em até 30 dias."
        ),
    }

    agendamento = mapa.get(urgencia, mapa["prioritaria"])
    safe_log(FLOW_NAME, "recomendar_agendamento", urgencia)
    return {**state, "agendamento": agendamento}
