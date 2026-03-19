import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from streamlit_google_auth import Authenticate

# --- 1. CONFIGURAÇÃO DE SEGURANÇA (O Pulo do Gato para a Nuvem) ---
# Como o arquivo client_secret.json não está no GitHub, nós o recriamos aqui 
# usando os dados que você colou no "Secrets" do Streamlit.
if 'web' in st.secrets:
    with open('client_secret.json', 'w') as f:
        # Reconstroi o formato JSON esperado pela biblioteca
        json.dump({"web": dict(st.secrets['web'])}, f)

# Inicializa o porteiro com o link oficial da sua equipe
authenticator = Authenticate(
    secret_credentials_path='client_secret.json',
    redirect_uri='https://rastreioccr-barao-y9ck2rdmoasqbastp77xsu.streamlit.app',
    cookie_name='mfc_auth_tijuca',
    cookie_key='chave_secreta_mfc_2026'
)

# --- 2. LOGARITMO DE ACESSO ---
# Verifica se o usuário já passou pelo login do Google
if not st.session_state.get("connected"):
    st.markdown("### 🏥 APS Tijuca - Unidade Barão")
    st.title("🔒 Monitor de Rastreio CCR")
    st.info("Acesse com o e-mail da equipe para gerenciar a busca ativa de pacientes.")
    authenticator.login()
    st.stop() # Interrompe o código aqui até o login ser feito

# --- 3. VERIFICAÇÃO DE EQUIPE (Lista Branca) ---
user_info = st.session_state.get("user_info")
user_email = user_info.get("email")

# ADICIONE AQUI OS E-MAILS DA SUA EQUIPE NA TIJUCA
equipe_autorizada = [
    "mcarinomiria@gmail.com", 
    "equipebarao@gmail.com", 
    "carinomiria@gmail.com"
]

if user_email not in equipe_autorizada:
    st.error(f"Acesso negado para {user_email}. Você não tem permissão para ver estes dados.")
    if st.button("Sair"):
        authenticator.logout()
    st.stop()

# --- 4. APLICATIVO PRINCIPAL (SÓ PARA AUTORIZADOS) ---
st.sidebar.success(f"Conectado: Dra. {user_info.get('name')}")
if st.sidebar.button("Logoff"):
    authenticator.logout()

st.title("📊 Gestão de Rastreio de Câncer Colorretal")
st.markdown("---")

st.subheader("📁 1. Importar Relatório do e-SUS PEC")
st.write("Suba o arquivo Excel da 'Lista Nominal' extraído do Relatório Operacional.")

arquivo = st.file_uploader("Escolha a planilha (.xlsx)", type=['xlsx'])

if arquivo:
    # Lógica de processamento com Pandas
    df = pd.read_excel(arquivo)
    hoje = datetime.now()
    
    # Busca automática da coluna de data (evita erro se o nome mudar um pouco)
    col_nasc = [c for c in df.columns if 'Nascimento' in str(c)]
    col_nasc = col_nasc[0] if col_nasc else df.columns[0]
    
    df['Nasc'] = pd.to_datetime(df[col_nasc], errors='coerce')
    
    # Cálculo da Idade: 
    # $$Idade = \frac{\text{Data de Hoje} - \text{Data de Nascimento}}{365.25}$$
    df['Idade'] = (hoje - df['Nasc']).dt.days // 365
    
    # FILTRO PROTOCOLO SMS-RIO: 50 a 75 anos
    alvo = df[(df['Idade'] >= 50) & (df['Idade'] <= 75)].copy()

    # 5. DASHBOARD DE INDICADORES
    c1, c2, c3 = st.columns(3)
    c1.metric("Público-Alvo (50-75a
