# =================================================================
# SISTEMA DE PONTO DIGITAL PRO - ARQUIVO: ADMIN.PY
# =================================================================
import streamlit as st
import pandas as pd
import os
from database import DB_FILE, CAD_FUNC_FILE, cadastrar_novo_funcionario, limpar_banco_pontos

def renderizar_painel_administrativo():
    """Gera a interface completa do módulo restrito do RH."""
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    
    with st.expander("📊 Painel Administrativo Restrito (Apenas ADM)"):
        senha_adm = st.text_input("Digite a senha master:", type="password", key="senha_adm_input")
        
        if senha_adm == "1234":
            aba1, aba2, aba3, aba4 = st.tabs([
                "📊 Relatórios e Filtros", "👤 Cadastrar Funcionários", 
                "📸 Galeria Visual", "⚙️ Manutenção do Sistema"
            ])
            
            with aba1:
                st.markdown("### Histórico de Pontos por Funcionário")
                if os.path.exists(DB_FILE):
                    df_pontos = pd.read_excel(DB_FILE)
                    if not df_pontos.empty:
                        func_com_ponto = sorted(df_pontos["Nome do Funcionário"].unique().tolist())
                        abas_funcionarios = st.tabs(func_com_ponto)
                        for i, nome_func in enumerate(func_com_ponto):
                            with abas_funcionarios[i]:
                                st.dataframe(df_pontos[df_pontos["Nome do Funcionário"] == nome_func], use_container_width=True)
                    else:
                        st.info("ℹ️ Nenhum ponto registrado.")
                        
            with aba2:
                st.markdown("### Formulário de Cadastro Obrigatório de RH")
                col_esq, col_dir = st.columns(2)
                with col_esq:
                    c_mat = st.text_input("Nova Matrícula:", key="c_mat_in").strip()
                    c_nome = st.text_input("Nome completo:", key="c_nome_in").strip()
                    c_senha = st.text_input("Senha Pessoal:", type="password", key="c_senha_in").strip()
                    c_cpf = st.text_input("CPF do Colaborador:", key="c_cpf_in").strip()
                with col_dir:
                    c_tel = st.text_input("Telefone de Contato:", key="c_tel_in").strip()
                    c_cnh = st.text_input("CNH (Se possuir):", key="c_cnh_in").strip()
                    c_end = st.text_input("Endereço residencial:", key="c_end_in").strip()
                    c_foto = st.file_uploader("Foto de Perfil Oficial:", type=["jpg", "jpeg", "png"], key="c_foto_in")
                    
                if st.button("Cadastrar Funcionário Novo", type="primary"):
                    c_user = cadastrar_novo_funcionario(c_mat, c_nome, c_senha, c_cpf, c_tel, c_cnh, c_end, c_foto)
                    st.success(f"🎉 Cadastrado com sucesso! Login: {c_user}")
                    st.rerun()
                        
            with aba3:
                st.markdown("### Prontuários e Fichas com Fotos de Perfil")
                if os.path.exists(CAD_FUNC_FILE):
                    df_f = pd.read_excel(CAD_FUNC_FILE)
                    if not df_f.empty:
                        for _, row in df_f.iterrows():
                            with st.expander(f"👤 {row['Nome Completo']} (Matrícula: {row['Matrícula']})"):
                                col_f1, col_f2 = st.columns(2)
                                with col_f1:
                                    if os.path.exists(str(row['Foto Perfil'])):
                                        st.image(str(row['Foto Perfil']), width=150)
                                with col_f2:
                                    st.markdown(f"**Usuário:** {row['Usuário']} | **Senha:** {row['Senha']}")
                                    st.markdown(f"**CPF:** {row['CPF']} | **Telefone:** {row['Telefone']}")
                                    st.markdown(f"**CNH:** {row['CNH']}")
                                    st.markdown(f"**Endereço:** {row['Endereço']}")
                                    
            with aba4:
                st.markdown("### Manutenção")
                if st.button("Limpar Batidas de Ponto do Mês"):
                    limpar_banco_pontos()
                    st.success("🗑️ Histórico de pontos redefinido!")
                    st.rerun()

# FIM DO ARQUIVO DO PAINEL ADMINISTRATIVO - CONTAGEM DE LINHAS: 79
