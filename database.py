# =================================================================
# SISTEMA DE PONTO DIGITAL PRO - ARQUIVO: DATABASE.PY
# =================================================================
import os
import pandas as pd
from datetime import datetime
import pytz

# DEFINIÇÃO DE DIRETÓRIOS, BANCOS EXCEL E CONFIGURAÇÃO DE FUSO HORÁRIO
DB_FILE = "registro_ponto.xlsx"
CAD_FUNC_FILE = "funcionarios.xlsx"
FOTO_DIR = "fotos_ponto"
PERFIL_DIR = "fotos_perfil"
TIMEZONE = pytz.timezone("America/Sao_Paulo")

def inicializar_tabelas_excel():
    """Garante a criação das pastas físicas e planilhas com colunas oficiais."""
    for pasta in [FOTO_DIR, PERFIL_DIR]:
        if not os.path.exists(pasta):
            os.makedirs(pasta)

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

def salvar_registro_ponto(matricula, nome, tipo, obs, foto_path, lat, lon):
    """Salva com segurança a batida de ponto e gera o link correto do mapa."""
    df_atual = pd.read_excel(DB_FILE)
    tempo_final = obter_dados_tempo()
    
    novo_registro = {
        "Matrícula": matricula,
        "Nome do Funcionário": nome,
        "Data": tempo_final["data"],
        "Dia da Semana": tempo_final["dia_semana"],
        "Hora": tempo_final["hora"],
        "Tipo de Registro": tipo,
        "Observação": obs if obs else "Nenhuma",
        "Caminho da Foto": foto_path,
        "Local do Serviço": f"https://google.com{lat},{lon}"
    }
    
    df_atual = pd.concat([df_atual, pd.DataFrame([novo_registro])], ignore_index=True)
    df_atual.to_excel(DB_FILE, index=False)

def cadastrar_novo_funcionario(matricula, nome, senha, cpf, telefone, cnh, endereco, foto_uploader):
    """Executa o cadastro do funcionário tratando o nome do usuário sem erros."""
    df_func = pd.read_excel(CAD_FUNC_FILE)
    
    lista_nomes = nome.split()
    c_user = lista_nomes[0].lower() if lista_nomes else "user"
    
    caminho_perfil = "Não possui"
    if foto_uploader is not None:
        caminho_perfil = os.path.join(PERFIL_DIR, f"perfil_{c_user}.jpg")
        with open(caminho_perfil, "wb") as f:
            f.write(foto_uploader.getbuffer())
        
    novo_reg = {
        "Matrícula": [matricula], "Nome Completo": [nome], "Usuário": [c_user],
        "Senha": [senha], "CPF": [cpf], "Telefone": [telefone],
        "CNH": [cnh if cnh else "Não possui"], "Endereço": [endereco if endereco else "Não informado"],
        "Foto Perfil": [caminho_perfil], "Data Cadastro": [datetime.now(TIMEZONE).strftime("%d/%m/%Y")]
    }
    df_func = pd.concat([df_func, pd.DataFrame(novo_reg)], ignore_index=True)
    df_func.to_excel(CAD_FUNC_FILE, index=False)
    return c_user

def limpar_banco_pontos():
    """Remove e reinicializa a tabela de marcações."""
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    inicializar_tabelas_excel()

# FIM DO ARQUIVO DATABASE.PY COMPLETO - CONTAGEM DE LINHAS: 93
