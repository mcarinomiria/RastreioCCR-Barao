import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_google_auth import Authenticate

# --- 1. CONFIGURAÇÃO (O arquivo JSON que você baixou) ---
authenticator = Authenticate(
    secret_credentials_path='client_secret.json',
    redirect_uri='http://localhost:8501',
    cookie_name='mfc_auth_tijuca',
    cookie_key='chave_secreta_mfc_2026'
)

# --- 2. TELA DE LOGIN ---
# Se o usuário não estiver conectado, o Streamlit mostra o botão
if not st.session_state.get("connected"):
    st.markdown("### 🏥 APS Tijuca - Rastreio CCR")
    st.title("🔒 Login da Equipe")
    st.info("Faça login com sua conta Google para acessar os dados dos pacientes.")
    authenticator.login()

# --- 3. APP PRINCIPAL (SÓ APÓS LOGIN) ---
else:
    user_info = st.session_state.get("user_info")
    st.sidebar.success(f"Dra. {user_info.get('name')}")
    
    if st.sidebar.button("Logoff"):
        authenticator.logout()

    st.title("📊 Monitor de Rastreio de Câncer Colorretal")
    st.write("Processamento automático do e-SUS PEC (Protocolo SMS-Rio).")

    # Área de Upload da planilha operacional do PEC
    arquivo = st.file_uploader("Suba a planilha operacional (.xlsx)", type=['xlsx'])

    if arquivo:
        df = pd.read_excel(arquivo)
        hoje = datetime.now()
        
        # Lógica de Rastreio da SMS-Rio (50-75 anos)
        col_nasc = [c for c in df.columns if 'Nascimento' in str(c)]
        col_nasc = col_nasc[0] if col_nasc else df.columns[0]
        
        df['Nasc'] = pd.to_datetime(df[col_nasc], errors='coerce')
        df['Idade'] = (hoje - df['Nasc']).dt.days // 365
        
        # Filtro de público-alvo oficial (50 a 75 anos)
        alvo = df[(df['Idade'] >= 50) & (df['Idade'] <= 75)].copy()

        st.success(f"Identificados {len(alvo)} pacientes na faixa de rastreio.")
        
        st.subheader("🔴 Lista Prioritária para os ACS")
        st.dataframe(alvo[['Nome', 'Idade', 'CNS']], use_container_width=True)

        # Botão para exportar a lista de busca ativa
        csv = alvo.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Lista de Busca Ativa", csv, "busca_ativa.csv", "text/csv")