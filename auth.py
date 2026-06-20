"""Proteção por senha para a versão publicada do aplicativo."""

import hmac
import streamlit as st


def require_authentication():
    try:
        app_password = str(st.secrets["APP_PASSWORD"])
    except Exception:
        st.error("Configuração ausente: defina APP_PASSWORD nos segredos do Streamlit.")
        st.stop()

    if st.session_state.get("authenticated"):
        return

    st.title("Finanças Pessoais")
    with st.form("login"):
        password = st.text_input("Senha de acesso", type="password")
        submit = st.form_submit_button("Entrar", use_container_width=True)

    if submit:
        if hmac.compare_digest(password, app_password):
            st.session_state.authenticated = True
            st.rerun()
        st.error("Senha incorreta.")
    st.stop()