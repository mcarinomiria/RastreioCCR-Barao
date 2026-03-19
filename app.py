import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from streamlit_google_auth import Authenticate

# --- 1. CONFIGURAÇÃO DE SEGURANÇA ---
if 'web' in st.secrets:
    with open('client_secret.json', 'w') as f:
        json.dump({"web": dict(st.secrets['web'])}, f)

authenticator = Authenticate(
    secret_credentials_path='client_secret.json',
    redirect_uri='https://rastreioccr-barao-uz2gyzkjdnazaz7huvaskg.streamlit.app',
    cookie_name='mfc_auth_tijuca',
    cookie_key='chave_secreta_mfc_2026'
)

# --- 2. LOGIN ---
if not st.session_state.get("connected"):
    st.markdown("### 🏥 APS Tijuca - Unidade Barão")
    st.title("🔒 Monitor de Rastreio CCR")
    st.info("Acesse com o e-mail da equipe para gerenciar a busca ativa.")
    authenticator.login()
    st.stop()

# --- 3. VERIFICAÇÃO DE EQUIPE ---
user_info = st.session_state.get("user_info")
user_email = user_info.get("email")
equipe_autorizada = ["mcarinomiria@gmail.com", "equipebarao@gmail.com"]

if user_email not in equipe_autorizada:
    st.error(f"Acesso negado para {user_email}.")
    if st.button("Sair"):
        authenticator.logout()
    st.stop()

# --- 4. APP PRINCIPAL ---
st.sidebar.success(f"Dra. {user_info.get('name')}")
if st.sidebar.button("Logoff"):
    authenticator.logout()

st.title("📊 Gestão de Rastreio CCR")
st.markdown("---")

st.subheader("📁 1. Importar Relatório do e-SUS")
arquivo = st.file_uploader("Suba a planilha (.xlsx)", type=['xlsx'])

if arquivo:
    df = pd.read_excel(arquivo)
    hoje = datetime.now()
    
    col_nasc = [c for c in df.columns if 'Nascimento' in str(c)]
    col_nasc = col_nasc[0] if col_nasc else df.columns[0]
    
    df['Nasc'] = pd.to_datetime(df[col_nasc], errors='coerce')
    df['Idade'] = (hoje - df['Nasc']).dt.days // 365
    
    alvo = df[(df['Idade'] >= 50) & (df['Idade'] <= 75)].copy()

    # Tudo aqui embaixo tem exatamente 4 espaços de recuo
    c1, c2, c3 = st.columns(3)
    c1.metric("Público-Alvo (50-75a)", len(alvo))
    c2.metric("Aguardando SOF", len(alvo))
    c3.metric("Status", "Monitorando")

    st.markdown("---")
    
    st.subheader("🔴 Lista de Busca Ativa")
    st.dataframe(alvo[['Nome', 'Idade', 'CNS']], use_container_width=True)

    csv = alvo.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Baixar Lista para ACS", csv, "busca_ativa.csv", "text/csv")
