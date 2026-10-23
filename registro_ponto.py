# =================================================================
# SISTEMA DE PONTO DIGITAL PRO - ARQUIVO PRINCIPAL INTEGRADO
# =================================================================
import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image, ImageDraw
import streamlit.components.v1 as components
from database import DB_FILE, FOTO_DIR, TIMEZONE, inicializar_tabelas_excel, obter_dados_tempo, salvar_registro_ponto
from auth import inicializar_estado_sessao, processar_login, realizar_logout
from admin import renderizar_painel_administrativo

# CONFIGURAÇÃO DA INTERFACE VISUAL RESPONSIVA DO STREAMLIT
st.set_page_config(
    page_title="Ponto Digital Pro",
    page_icon="⏰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# EXECUTA A INICIALIZAÇÃO ATÔMICA DOS BANCOS DE DADOS
inicializar_tabelas_excel()

# GARANTE A PERSISTÊNCIA DAS VARIÁVEIS DE CONTROLE DE SESSÃO
inicializar_estado_sessao()

# INTERFACE PRINCIPAL DE LOGIN DO FUNCIONÁRIO
st.markdown("## ⏰ Registro de Ponto Digital")
st.markdown("---")

if not st.session_state.logado:
    st.markdown("### 🔑 Área de Acesso do Colaborador")
    input_usuario = st.text_input("Digite seu Usuário de Acesso:", key="login_user_input").strip()
    input_senha = st.text_input("Digite sua Senha Pessoal:", type="password", key="login_pass_input").strip()

    if st.button("Entrar", type="primary"):
        if processar_login(input_usuario, input_senha):
            st.rerun()
        else:
            st.error("❌ Usuário ou Senha incorreta.")
else:
    st.sidebar.markdown(f"👤 **Usuário:**\n{st.session_state.nome_colaborador}")
    if st.sidebar.button("Logout / Sair"):
        realizar_logout()
        st.rerun()

    st.success(f"🔓 Conectado: **{st.session_state.nome_colaborador}** (Matrícula: {st.session_state.matricula_funcionario})")
    
    # CRIA AS DUAS ABAS OPERACIONAIS DO FUNCIONÁRIO
    tab_bater, tab_consultar = st.tabs(["⏱️ Registrar meu Ponto", "📊 Consultar meus Dias"])
    
    with tab_bater:
        tipo_registro = st.selectbox(
            "Selecione o Tipo de Registro:",
            ["Entrada", "Saída Almoço", "Retorno Almoço", "Saída"],
            key="tipo_registro_select"
        )
        observacao = st.text_area("Observação (Opcional):", max_chars=200, key="obs_text_area")

        st.markdown("### 🗺️ Validação de Presença")
        
        js_gps = """
        <script>
        function obterLocalizacao() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        const dados = {
                            lat: position.coords.latitude,
                            lon: position.coords.longitude
                        };
                        window.parent.postMessage({type: 'streamlit:setComponentValue', value: dados}, '*');
                    },
                    function(error) {
                        window.parent.postMessage({type: 'streamlit:setComponentValue', value: "erro"}, '*');
                    },
                    {enableHighAccuracy: true, timeout: 10000, maximumAge: 0}
                );
            }
        }
        </script>
        <button onclick="obterLocalizacao()" style="padding: 12px; background-color: #ff4b4b; color: white; border: none; border-radius: 4px; cursor: pointer; width: 100%; font-weight: bold;">
            📍 CLIQUE AQUI PARA VERIFICAR LOCALIZAÇÃO ATUAL
        </button>
        """
        
        dados_retorno = components.html(js_gps, height=60)
        
        if dados_retorno:
            if isinstance(dados_retorno, dict) and "lat" in dados_retorno:
                st.session_state.lat = dados_retorno["lat"]
                st.session_state.lon = dados_retorno["lon"]
                st.session_state.gps_ok = True
            elif dados_retorno == "erro":
                st.error("❌ Permissão de GPS negada. Ative a localização no seu aparelho celular ou navegador.")
                st.session_state.gps_ok = False

        if st.session_state.gps_ok:
            st.success(f"✅ Localização obtida! (Lat: {st.session_state.lat:.4f}, Lon: {st.session_state.lon:.4f})")

            st.markdown("### 📸 Comprovação por Foto")
            foto_capturada = st.camera_input("Posicione o rosto e tire a foto:")
            
            if foto_capturada:
                img = Image.open(foto_capturada)
                draw = ImageDraw.Draw(img)
                
                tempo = obter_dados_tempo()
                texto_carimbo = f"{tempo['data']} - {tempo['hora']}\nLat: {st.session_state.lat:.4f}, Lon: {st.session_state.lon:.4f}"
                
                largura, altura = img.size
                draw.rectangle([15, altura - 75, 340, altura - 15], fill="black")
                draw.text((20, altura - 70), texto_carimbo, fill="white")
                
                lista_nomes = st.session_state.nome_colaborador.split()
                usuario_username = lista_nomes.lower() if lista_nomes else "user"
                timestamp_arquivo = datetime.now(TIMEZONE).strftime("%Y%m%d_%H%M%S")
                nome_foto = f"foto_{usuario_username}_{timestamp_arquivo}.jpg"
                caminho_salvamento = os.path.join(FOTO_DIR, nome_foto)
                
                img.save(caminho_salvamento, "JPEG")
                st.session_state.foto_carimbada_path = caminho_salvamento
                st.success("📸 Imagem capturada e carimbada com sucesso!")
        else:
            st.warning("⚠️ Valide sua localização atual no botão acima para liberar a câmera.")

        if st.session_state.gps_ok and st.session_state.foto_carimbada_path:
            st.markdown("---")
            if st.button("Confirmar Registro de Ponto", type="primary", key="btn_confirmar_ponto"):
                salvar_registro_ponto(
                    st.session_state.matricula_funcionario,
                    st.session_state.nome_colaborador,
                    tipo_registro,
                    observacao,
                    st.session_state.foto_carimbada_path,
                    st.session_state.lat,
                    st.session_state.lon
                )
                
                st.success(f"✅ Ponto de {st.session_state.nome_colaborador} gravado com sucesso!")
                st.balloons()
                
                st.session_state.lat = None
                st.session_state.lon = None
                st.session_state.gps_ok = False
                st.session_state.foto_carimbada_path = None
                st.rerun()

    # MÓDULO PRIVADO DE CONSULTA DE HISTÓRICO
    with tab_consultar:
        st.markdown(f"### 📊 Seus Registros de Ponto - {st.session_state.nome_colaborador}")
        if os.path.exists(DB_FILE):
            df_pontos_geral = pd.read_excel(DB_FILE)
            if not df_pontos_geral.empty:
                df_meu_ponto = df_pontos_geral[df_pontos_geral["Nome do Funcionário"] == st.session_state.nome_colaborador]
                if not df_meu_ponto.empty:
                    st.dataframe(df_meu_ponto, use_container_width=True)
                else:
                    st.info("ℹ️ Você ainda não possui registros de ponto gravados.")
            else:
                st.info("ℹ️ Nenhum registro de ponto encontrado no sistema.")

# INJEÇÃO DO PAINEL ADMINISTRATIVO ISOLADO
renderizar_painel_administrativo()

# FIM DO NOVO FLUXO MODULAR - CONTAGEM DE LINHAS DESTE BLOCO: 154
