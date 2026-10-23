
# =================================================================
# SISTEMA DE PONTO DIGITAL PRO - BLOCO 1 DE 5: ESTRUTURA DE DADOS
# =================================================================
import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import os
import streamlit.components.v1 as components
from PIL import Image, ImageDraw

# CONFIGURAÇÃO DA INTERFACE VISUAL RESPONSIVA
st.set_page_config(
    page_title="Ponto Digital Pro",
    page_icon="⏰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# DIRETÓRIOS, BANCOS EXCEL E CONFIGURAÇÃO DE FUSO HORÁRIO
DB_FILE = "registro_ponto.xlsx"
CAD_FUNC_FILE = "funcionarios.xlsx"
FOTO_DIR = "fotos_ponto"
PERFIL_DIR = "fotos_perfil"
TIMEZONE = pytz.timezone("America/Sao_Paulo")

# CRIA AS PASTAS FÍSICAS DE FOTOS SE NÃO EXISTIREM
for pasta in [FOTO_DIR, PERFIL_DIR]:
    if not os.path.exists(pasta):
        os.makedirs(pasta)

def obter_dados_tempo():
    """Retorna dicionário com data, hora e dia da semana atualizados."""
    agora = datetime.now(TIMEZONE)
    dias_semana = {
        0: "Segunda-feira", 1: "Terça-feira", 2: "Quarta-feira",
        3: "Quinta-feira", 4: "Sexta-feira", 5: "Sábado", 6: "Domingo"
    }
    return {
        "data": agora.strftime("%d/%m/%Y"),
        "dia_semana": dias_semana[agora.weekday()],
        "hora": agora.strftime("%H:%M:%S")
    }

def inicializar_tabelas_excel():
    """Garante a criação das duas planilhas com as novas colunas oficiais."""
    if not os.path.exists(DB_FILE):
        colunas_ponto = [
            "Matrícula", "Nome do Funcionário", "Data", "Dia da Semana",
            "Hora", "Tipo de Registro", "Observação", "Caminho da Foto",
            "Local do Serviço"
        ]
        pd.DataFrame(columns=colunas_ponto).to_excel(DB_FILE, index=False)
        
    if not os.path.exists(CAD_FUNC_FILE):
        colunas_func = [
            "Matrícula", "Nome Completo", "Usuário", "Senha", 
            "CPF", "Telefone", "CNH", "Endereço", "Foto Perfil", "Data Cadastro"
        ]
        pd.DataFrame(columns=colunas_func).to_excel(CAD_FUNC_FILE, index=False)

# EXECUTA A INICIALIZAÇÃO ATÔMICA DOS BANCOS DE DADOS
inicializar_tabelas_excel()

# FIM DO BLOCO 1 DE 5 - CONTAGEM DE LINHAS: 56


#  2  ====================================================================================================================================================================

# =================================================================
# SISTEMA DE PONTO DIGITAL PRO - BLOCO 2 DE 5: ACESSO INDIVIDUAL
# =================================================================

# INTERFACE PRINCIPAL DE LOGIN DO FUNCIONÁRIO
st.markdown("## ⏰ Registro de Ponto Digital")
st.markdown("---")

st.markdown("### 🔑 Área de Acesso do Colaborador")
input_usuario = st.text_input("Digite seu Usuário de Acesso:", key="login_user_input").strip()
input_senha = st.text_input("Digite sua Senha Pessoal:", type="password", key="login_pass_input").strip()

logado = False
nome_colaborador = None
matricula_funcionario = None

if input_usuario and input_senha:
    df_validos = pd.read_excel(CAD_FUNC_FILE)
    if not df_validos.empty:
        # ASSEGURA QUE OS DADOS SEJAM TRATADOS COMO TEXTO SEM ESPAÇOS
        df_validos["Usuário"] = df_validos["Usuário"].astype(str).str.strip()
        df_validos["Senha"] = df_validos["Senha"].astype(str).str.strip()
        
        # PROCURA AS CREDENCIAIS PREENCHIDAS NO ARQUIVO EXCEL
        usuario_valido = df_validos[(df_validos["Usuário"] == input_usuario) & (df_validos["Senha"] == input_senha)]
        
        if not usuario_valido.empty:
            logado = True
            nome_colaborador = str(usuario_valido.iloc[0]["Nome Completo"])
            matricula_funcionario = str(usuario_valido.iloc[0]["Matrícula"])
            st.success(f"🔓 Conectado com sucesso: **{nome_colaborador}** (Matrícula: {matricula_funcionario})")
        else:
            st.error("❌ Usuário ou Senha incorreta.")

if logado and nome_colaborador:
    # CRIA AS DUAS ABAS DO FUNCIONÁRIO SE ELE ESTIVER AUTENTICADO
    tab_bater, tab_consultar = st.tabs(["⏱️ Registrar meu Ponto", "📊 Consultar meus Dias"])
    
    with tab_bater:
        tipo_registro = st.selectbox(
            "Selecione o Tipo de Registro:",
            ["Entrada", "Saída Almoço", "Retorno Almoço", "Saída"],
            key="tipo_registro_select"
        )
        observacao = st.text_area("Observação (Opcional):", max_chars=200, key="obs_text_area")

# FIM DO BLOCO 2 DE 5 - CONTAGEM DE LINHAS: 42


#  3  ====================================================================================================================================================================

# =================================================================
# SISTEMA DE PONTO DIGITAL PRO - BLOCO 3 DE 5: CAPTURA DO GPS NATIVO
# =================================================================

# INICIALIZA AS VARIÁVEIS DE CONTROLE DE GPS NO ESTADO DA SESSÃO
if "lat" not in st.session_state:
    st.session_state.lat = None
if "lon" not in st.session_state:
    st.session_state.lon = None
if "gps_ok" not in st.session_state:
    st.session_state.gps_ok = False

if logado and nome_colaborador:
    with tab_bater:
        st.markdown("### 🗺️ Validação de Presença")
        
        # SCRIPT HTML5 RESPONSIVO COMPATÍVEL COM ANDROID E IOS
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
        
        # RENDERIZA O COMPONENTE VISUAL DO BOTÃO DE GPS
        dados_retorno = components.html(js_gps, height=60)
        
        # CAPTURA E VALIDA AS COORDENADAS ENVIADAS PELO NAVEGADOR
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

# FIM DO BLOCO 3 DE 5 - CONTAGEM DE LINHAS: 52


#  4  ====================================================================================================================================================================

# =================================================================
# SISTEMA DE PONTO DIGITAL PRO - BLOCO 4 DE 5: CÂMERA E CONSULTA
# =================================================================

# INICIALIZA A VARIÁVEL DE CAMINHO DA FOTO NO ESTADO DA SESSÃO
if "foto_carimbada_path" not in st.session_state:
    st.session_state.foto_carimbada_path = None

if logado and nome_colaborador:
    with tab_bater:
        if st.session_state.gps_ok:
            st.markdown("### 📸 Comprovação por Foto")
            foto_capturada = st.camera_input("Posicione o rosto e tire a foto:")
            
            if foto_capturada:
                # PROCESSAMENTO DA IMAGEM E INJEÇÃO DOS METADADOS VISUAIS
                img = Image.open(foto_capturada)
                draw = ImageDraw.Draw(img)
                
                tempo = obter_dados_tempo()
                texto_carimbo = f"{tempo['data']} - {tempo['hora']}\nLat: {st.session_state.lat:.4f}, Lon: {st.session_state.lon:.4f}"
                
                largura, altura = img.size
                draw.rectangle([15, altura - 75, 340, altura - 15], fill="black")
                draw.text((20, altura - 70), texto_carimbo, fill="white")
                
                # SALVA A FOTO CARIMBADA COM NOME EXCLUSIVO NA PASTA LOCAL
                timestamp_arquivo = datetime.now(TIMEZONE).strftime("%Y%m%d_%H%M%S")
                nome_foto = f"foto_{input_usuario}_{timestamp_arquivo}.jpg"
                caminho_salvamento = os.path.join(FOTO_DIR, nome_foto)
                
                img.save(caminho_salvamento, "JPEG")
                st.session_state.foto_carimbada_path = caminho_salvamento
                st.success("📸 Imagem capturada e carimbada com sucesso!")
        else:
            st.warning("⚠️ Valide sua localização atual no botão acima para liberar a câmera.")

    # MÓDULO PRIVADO DE CONSULTA DE HISTÓRICO DO COLABORADOR LOGADO
    with tab_consultar:
        st.markdown(f"### 📊 Seus Registros de Ponto - {nome_colaborador}")
        if os.path.exists(DB_FILE):
            df_pontos_geral = pd.read_excel(DB_FILE)
            if not df_pontos_geral.empty:
                # FILTRA RIGOROSAMENTE APENAS AS LINHAS DESTE FUNCIONÁRIO
                df_meu_ponto = df_pontos_geral[df_pontos_geral["Nome do Funcionário"] == nome_colaborador]
                if not df_meu_ponto.empty:
                    st.dataframe(df_meu_ponto, use_container_width=True)
                else:
                    st.info("ℹ️ Você ainda não possui registros de ponto gravados.")
            else:
                st.info("ℹ️ Nenhum registro de ponto encontrado no sistema.")

# FIM DO BLOCO 4 DE 5 - CONTAGEM DE LINHAS: 48


#  5  ====================================================================================================================================================================

# =================================================================
# SISTEMA DE PONTO DIGITAL PRO - BLOCO 5 DE 5: GRAVAÇÃO E PAINEL ADM
# =================================================================

if logado and nome_colaborador and st.session_state.get("foto_carimbada_path"):
    with tab_bater:
        st.markdown("---")
        if st.button("Confirmar Registro de Ponto", type="primary", key="btn_confirmar_ponto"):
            df_atual = pd.read_excel(DB_FILE)
            tempo_final = obter_dados_tempo()
            
            novo_registro = {
                "Matrícula": matricula_funcionario,
                "Nome do Funcionário": nome_colaborador,
                "Data": tempo_final["data"],
                "Dia da Semana": tempo_final["dia_semana"],
                "Hora": tempo_final["hora"],
                "Tipo de Registro": tipo_registro,
                "Observação": observacao if observacao else "Nenhuma",
                "Caminho da Foto": st.session_state.foto_carimbada_path,
                "Local do Serviço": f"https://google.com{st.session_state.lat},{st.session_state.lon}"
            }
            
            df_atual = pd.concat([df_atual, pd.DataFrame([novo_registro])], ignore_index=True)
            df_atual.to_excel(DB_FILE, index=False)
            
            st.success(f"✅ Ponto de {nome_colaborador} gravado com sucesso!")
            st.balloons()
            
            st.session_state.lat = None
            st.session_state.lon = None
            st.session_state.gps_ok = False
            del st.session_state["foto_carimbada_path"]
            st.rerun()

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
                c_nome = st.text_input("Nome Completo:", key="c_nome_in").strip()
                c_senha = st.text_input("Senha Pessoal:", type="password", key="c_senha_in").strip()
                c_cpf = st.text_input("CPF do Colaborador:", key="c_cpf_in").strip()
            with col_dir:
                c_tel = st.text_input("Telefone de Contato:", key="c_tel_in").strip()
                c_cnh = st.text_input("CNH (Se possuir):", key="c_cnh_in").strip()
                c_end = st.text_input("Endereço Residencial:", key="c_end_in").strip()
                c_foto = st.file_uploader("Foto de Perfil Oficial:", type=["jpg", "jpeg", "png"], key="c_foto_in")
                
            if st.button("Cadastrar Funcionário Novo", type="primary"):
                if c_mat and c_nome and c_senha and c_cpf and c_tel and c_foto:
                    df_func = pd.read_excel(CAD_FUNC_FILE)
                    c_user = c_nome.split()[0].lower() if c_nome.split() else "user"
                    
                    caminho_perfil = os.path.join(PERFIL_DIR, f"perfil_{c_user}.jpg")
                    with open(caminho_perfil, "wb") as f:
                        f.write(c_foto.getbuffer())
                        
                    novo_reg = {
                        "Matrícula": [c_mat], "Nome Completo": [c_nome], "Usuário": [c_user],
                        "Senha": [c_senha], "CPF": [c_cpf], "Telefone": [c_tel],
                        "CNH": [c_cnh if c_cnh else "Não possui"], "Endereço": [c_end if c_end else "Não informado"],
                        "Foto Perfil": [caminho_perfil], "Data Cadastro": [datetime.now(TIMEZONE).strftime("%d/%m/%Y")]
                    }
                    df_func = pd.concat([df_func, pd.DataFrame(novo_reg)], ignore_index=True)
                    df_func.to_excel(CAD_FUNC_FILE, index=False)
                    st.success(f"🎉 Cadastrado com sucesso! Login: {c_user}")
                    st.rerun()
                else:
                    st.error("❌ Os campos Matrícula, Nome, Senha, CPF, Telefone e Foto são OBRIGATÓRIOS!")
                    
        with aba3:
            st.markdown("### Prontuários e Fichas com Fotos de Perfil")
            if os.path.exists(CAD_FUNC_FILE):
                df_f = pd.read_excel(CAD_FUNC_FILE)
                if not df_f.empty:
                    for _, row in df_f.iterrows():
                        with st.expander(f"👤 {row['Nome Completo']} (Matrícula: {row['Matrícula']})"):
                            col_f1, col_f2 = st.columns([1, 2])
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
                if os.path.exists(DB_FILE):
                    os.remove(DB_FILE)
                    inicializar_tabelas_excel()
                    st.success("🗑️ Histórico de pontos redefinido!")
                    st.rerun()
# FIM DO ARQUIVO ÚNICO - CONTAGEM DE LINHAS DESTE BLOCO: 110


#  FIM  ====================================================================================================================================================================
