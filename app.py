import streamlit as st

from langchain_assistant import generate_response


st.set_page_config(
    page_title="Assistente Médico",
    page_icon="🩺"
)

st.title("🩺 Assistente Médico")
st.write("Especializado em saúde da mulher")


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
        {
            "role": "user",
            "content": prompt
        }
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
        {
            "role": "assistant",
            "content": response
        }
    )