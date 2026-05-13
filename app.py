import streamlit as st

from langchain_assistant import generate_response
from langgraph_flows import (
    run_ginecologico_flow,
    run_violencia_flow,
    run_obstetrico_flow,
    run_prevencao_flow,
)


st.set_page_config(
    page_title="Assistente Médico",
    page_icon="🩺"
)

st.title("🩺 Assistente Médico")
st.write("Especializado em saúde da mulher")


# Sidebar — seleção do modo de atendimento
modo = st.sidebar.radio(
    "Modo de atendimento",
    [
        "Chat livre",
        "Triagem Ginecológica",
        "Violência Doméstica",
        "Obstétrico",
        "Prevenção",
    ],
)


def render_resultado_dict(resultado: dict) -> None:
    """Renderiza um estado final de fluxo no Streamlit."""
    for chave, valor in resultado.items():
        if chave == "erro" and not valor:
            continue
        titulo = chave.replace("_", " ").title()
        st.subheader(titulo)
        if isinstance(valor, list):
            for item in valor:
                st.markdown(f"- {item}")
        elif isinstance(valor, bool):
            st.markdown("✅ Sim" if valor else "❌ Não")
        else:
            st.markdown(str(valor))


# ============================================================
# MODO: CHAT LIVRE (comportamento original)
# ============================================================
if modo == "Chat livre":

    # histórico do chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # mostrar mensagens antigas
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # input do usuário
    if prompt := st.chat_input("Digite sua pergunta..."):
        # salva mensagem usuário

        st.session_state.messages.append(
            {"role": "user", "content": prompt}
        )

        # mostra mensagem usuário
        with st.chat_message("user"):
            st.markdown(prompt)
        # gera resposta
        response = generate_response(prompt)

        # mostra resposta
        with st.chat_message("assistant"):
            st.markdown(response)

        # salva resposta
        st.session_state.messages.append(
            {"role": "assistant", "content": response}
        )


# ============================================================
# MODO: TRIAGEM GINECOLÓGICA
# ============================================================
elif modo == "Triagem Ginecológica":

    # cabeçalho do modo
    st.header("Triagem Ginecológica")
    st.caption("Sintomas → Análise → Urgência → Exames → Orientações → Agendamento")

    # input dos sintomas
    sintomas = st.text_area(
        "Descreva os sintomas relatados pela paciente:",
        height=150,
        placeholder="Ex.: cólicas fortes há 3 dias, sangramento fora do período...",
    )

    # botão para iniciar triagem
    if st.button("Iniciar triagem", type="primary", disabled=not sintomas.strip()):
        # executa o fluxo de triagem
        with st.spinner("Executando fluxo de triagem..."):
            resultado = run_ginecologico_flow(sintomas.strip())
        # mostra sucesso
        st.success("Triagem concluída.")
        # renderiza o resultado
        render_resultado_dict(resultado)


# ============================================================
# MODO: VIOLÊNCIA DOMÉSTICA
# ============================================================
elif modo == "Violência Doméstica":

    # cabeçalho do modo
    st.header("Detecção de Violência Doméstica")
    st.caption(
        "Sinais → Avaliação → Protocolo → Equipe → Documentação → Seguimento"
    )
    # aviso de confidencialidade
    st.info(
        "🔒 Modo confidencial ativo. Nenhum dado da paciente é gravado em "
        "texto puro nos logs do sistema."
    )

    # input do relato
    relato = st.text_area(
        "Relato da paciente (modo confidencial):",
        height=200,
        placeholder="Descreva os sinais e o relato com cuidado e sensibilidade...",
    )

    # botão para iniciar avaliação
    if st.button("Iniciar avaliação", type="primary", disabled=not relato.strip()):
        # executa o fluxo de avaliação
        with st.spinner("Avaliando caso..."):
            resultado = run_violencia_flow(relato.strip())
        # mostra sucesso
        st.success("Avaliação concluída.")
        # renderiza o resultado
        render_resultado_dict(resultado)


# ============================================================
# MODO: OBSTÉTRICO
# ============================================================
elif modo == "Obstétrico":

    # cabeçalho do modo
    st.header("Acompanhamento Obstétrico")
    st.caption(
        "Dados → Risco gestacional → Orientações → Exames → Alertas → Acompanhamento"
    )

    # layout em duas colunas para dados básicos
    col1, col2 = st.columns(2)
    with col1:
        # input da idade
        idade = st.number_input("Idade da gestante", min_value=10, max_value=60, value=28)
        # input das semanas de gestação
        semanas = st.number_input("Semanas de gestação", min_value=1, max_value=42, value=20)
    with col2:
        # input da paridade
        paridade = st.text_input("Paridade (ex.: G2P1A0)", value="G1P0A0")
        # input das comorbidades
        comorbidades = st.text_input("Comorbidades (opcional)", value="")

    # input das queixas atuais
    queixas = st.text_area(
        "Queixas atuais:",
        height=120,
        placeholder="Ex.: dores nas costas, leve inchaço...",
    )

    # botão para iniciar avaliação
    if st.button("Iniciar avaliação obstétrica", type="primary", disabled=not queixas.strip()):
        # executa o fluxo obstétrico
        with st.spinner("Executando avaliação obstétrica..."):
            resultado = run_obstetrico_flow(
                idade=int(idade),
                semanas_gestacao=int(semanas),
                paridade=paridade,
                queixas=queixas.strip(),
                comorbidades=comorbidades,
            )
        # mostra sucesso
        st.success("Avaliação concluída.")
        # renderiza o resultado
        render_resultado_dict(resultado)


# ============================================================
# MODO: PREVENÇÃO
# ============================================================
elif modo == "Prevenção":

    # cabeçalho do modo
    st.header("Plano de Prevenção")
    st.caption(
        "Histórico → Exames devidos → Orientações → Agendamento → Lembretes"
    )

    # input da idade
    idade = st.number_input("Idade da paciente", min_value=12, max_value=100, value=35)
    # input do histórico familiar
    historico_familiar = st.text_area(
        "Histórico familiar:",
        height=80,
        placeholder="Ex.: mãe teve câncer de mama aos 52 anos...",
    )
    # input dos últimos exames
    ultimos_exames = st.text_area(
        "Últimos exames realizados:",
        height=80,
        placeholder="Ex.: Papanicolau em 2022, mamografia em 2021...",
    )
    # input dos fatores de risco
    fatores_risco = st.text_area(
        "Fatores de risco:",
        height=80,
        placeholder="Ex.: tabagismo, sedentarismo, sobrepeso...",
    )

    # botão para gerar plano
    if st.button("Gerar plano preventivo", type="primary"):
        # executa o fluxo de prevenção
        with st.spinner("Gerando plano preventivo..."):
            resultado = run_prevencao_flow(
                idade=int(idade),
                historico_familiar=historico_familiar.strip(),
                ultimos_exames=ultimos_exames.strip(),
                fatores_risco=fatores_risco.strip(),
            )
        # mostra sucesso
        st.success("Plano gerado.")
        # renderiza o resultado
        render_resultado_dict(resultado)
