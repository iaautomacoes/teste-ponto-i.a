# =================================================================
# SISTEMA DE PONTO DIGITAL PRO - ARQUIVO: AUTH.PY
# =================================================================
import streamlit as st
import pandas as pd
import os
from database import CAD_FUNC_FILE

def inicializar_estado_sessao():
    """Garante a persistência das variáveis de login e do sistema."""
    if "logado" not in st.session_state:
        st.session_state.logado = False
    if "nome_colaborador" not in st.session_state:
        st.session_state.nome_colaborador = None
    if "matricula_funcionario" not in st.session_state:
        st.session_state.matricula_funcionario = None
    if "lat" not in st.session_state:
        st.session_state.lat = None
    if "lon" not in st.session_state:
        st.session_state.lon = None
    if "gps_ok" not in st.session_state:
        st.session_state.gps_ok = False
    if "foto_carimbada_path" not in st.session_state:
        st.session_state.foto_carimbada_path = None

def processar_login(usuario, senha):
    """Valida as credenciais digitadas contra o banco Excel."""
    if usuario and senha:
        if os.path.exists(CAD_FUNC_FILE):
            df_validos = pd.read_excel(CAD_FUNC_FILE)
            if not df_validos.empty:
                df_validos["Usuário"] = df_validos["Usuário"].astype(str).str.strip()
                df_validos["Senha"] = df_validos["Senha"].astype(str).str.strip()
                
                usuario_valido = df_validos[(df_validos["Usuário"] == usuario) & (df_validos["Senha"] == senha)]
                
                if not usuario_valido.empty:
                    st.session_state.logado = True
                    # Puxa o texto limpo da linha cadastrada na planilha
                    st.session_state.nome_colaborador = str(usuario_valido.iloc[0]["Nome Completo"])
                    st.session_state.matricula_funcionario = str(usuario_valido.iloc[0]["Matrícula"])
                    return True
    return False

def realizar_logout():
    """Limpa os dados da sessão corrente e desloga o usuário."""
    st.session_state.logado = False
    st.session_state.nome_colaborador = None
    st.session_state.matricula_funcionario = None
    st.session_state.gps_ok = False
    st.session_state.foto_carimbada_path = None

# FIM DO ARQUIVO DE AUTENTICAÇÃO - CONTAGEM DE LINHAS: 49
