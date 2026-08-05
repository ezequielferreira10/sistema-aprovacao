import streamlit as st
from notion_client import Client
from datetime import datetime
import urllib.request
import ssl
import os

# Pega o token das Variáveis do Railway. Se não achar, usa o padrão (para testes)
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "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")

st.set_page_config(page_title="Compliance Tributário", page_icon="🏛️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    header[data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    footer { display: none !important; }
    
    * { box-sizing: border-box; }
    
    body {
        background-color: #f1f5f9;
        font-family: 'Inter', sans-serif;
        font-size: 14px;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0A5AA5 0%, #0c4a8a 100%);
        padding: 2rem 1.5rem;
    }
    [data-testid="stSidebar"] * { color: white !important; }
    
    [data-testid="stSidebar"] h3 {
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
        padding-bottom: 1rem !important;
        border-bottom: 2px solid rgba(255,255,255,0.2) !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox > div > div > div {
        background-color: white !important;
        border-radius: 8px !important;
        padding: 0.5rem !important;
    }
    [data-testid="stSidebar"] .stSelectbox > div > div > div > div {
        color: #0A5AA5 !important;
        font-weight: 600 !important;
    }
    
    .main {
        background-color: #f1f5f9;
        padding: 2rem 3rem;
    }
    
    .header {
        background: linear-gradient(135deg, #0A5AA5 0%, #084a8a 100%);
        padding: 3rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
    }
    .header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin: 0.75rem 0 0 0;
    }
    
    .section-label {
        font-size: 0.75rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 1rem;
    }
    
    .scenario-container {
        background: white;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border: 1px solid #e5e7eb;
    }
    
    .scenario-header {
        padding: 1.5rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #e5e7eb;
    }
    
    .scenario-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: #0A5AA5;
        margin: 0;
    }
    
    .status-badge {
        display: inline-flex;
        padding: 0.75rem 1.5rem;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.95rem;
        text-transform: uppercase;
    }
    .status-aprovado { background: #0A5AA5; color: white; }
    .status-reprovado { background: #FF6C12; color: white; }
    .status-pendente { background: #f1f5f9; color: #0A5AA5; border: 2px solid #0A5AA5; }
    
    .info-section {
        padding: 1.5rem 2rem;
        background: #f8fafc;
    }
    .info-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2rem;
    }
    .info-item { display: flex; flex-direction: column; gap: 0.5rem; }
    .info-label {
        font-size: 0.75rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .info-value {
        font-size: 1.25rem;
        font-weight: 700;
        color: #111827;
    }
    
    .files-section { padding: 1.5rem 2rem; background: white; }
    .files-label {
        font-size: 0.75rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.75rem;
    }
    .files-message {
        background: #fff7ed;
        padding: 1rem 1.25rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        color: #9a3412;
        font-weight: 600;
        border-left: 3px solid #FF6C12;
    }
    
    .file-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #f8fafc;
        padding: 1rem 1.25rem;
        border-radius: 10px;
        margin-bottom: 0.75rem;
        border: 1px solid #e5e7eb;
    }
    .file-name { font-weight: 600; color: #111827; font-size: 1rem; flex: 1; }
    
    .section-divider { margin: 1.5rem 2rem; border-top: 2px solid #e5e7eb; }
    
    .form-section {
        padding: 2rem;
        background: white;
        border-top: 3px solid #0A5AA5;
    }
    .form-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #0A5AA5;
        margin: 0 0 0.5rem 0;
    }
    .form-message { color: #64748b; font-size: 0.9rem; margin: 0; }
    
    .stButton > button {
        border-radius: 10px;
        font-weight: 700;
        font-size: 1rem;
        padding: 0.875rem 2rem;
    }
    .stButton > button[kind="primary"] {
        background: #0A5AA5;
        color: white;
        border: none;
        height: 52px;
    }
    .stButton > button[kind="secondary"] {
        background: white;
        color: #FF6C12;
        border: 2px solid #FF6C12;
    }
    .stButton > button[kind="tertiary"] {
        background: white;
        color: #64748b;
        border: 2px solid #e5e7eb;
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        border-radius: 10px;
        border: 2px solid #e5e7eb;
        background: white;
        font-size: 1rem;
        height: 52px;
    }
    
    .stExpander {
        border: none;
        border-radius: 16px;
        margin-bottom: 1rem;
        background: transparent;
    }
    
    label { font-size: 0.95rem; font-weight: 600; color: #111827; }
    h3, h4 { font-size: 1.3rem; font-weight: 700; color: #111827; }
</style>
""", unsafe_allow_html=True)

def encontrar_tabela(nome_tabela):
    # CORREÇÃO CRÍTICA: A API do Notion exige "data_source" e NÃO "database" na busca!
    response = notion.search(
        query=nome_tabela, 
        filter={"property": "object", "value": "data_source"}
    )
    resultados = response.get("results", [])
    
    # Tenta achar pelo nome exato para evitar pegar o banco de dados errado
    for resultado in resultados:
        if "title" in resultado and len(resultado["title"]) > 0:
            if resultado["title"][0].get("plain_text") == nome_tabela:
                return resultado["id"]
        elif "properties" in resultado and "title" in resultado["properties"]:
            props = resultado["properties"]["title"].get("title", [])
            if props and len(props) > 0 and props[0].get("plain_text") == nome_tabela:
                return resultado["id"]
                
    # Fallback: se não achar pelo nome exato, retorna o primeiro encontrado
    if resultados:
        return resultados[0]["id"]
    return None

def encontrar_coluna_title(props):
    for prop_name, prop_info in props.items():
        if prop_info.get("type") == "title":
            return prop_name
    return None

def encontrar_coluna(props, nomes_possiveis):
    for nome in nomes_possiveis:
        if nome in props:
            return nome
    return None

def get_status_safe(props, coluna_nome):
    if coluna_nome and coluna_nome in props:
        col = props[coluna_nome]
        if col and isinstance(col, dict):
            select = col.get("select")
            if select and isinstance(select, dict):
                return select.get("name", "Desconhecido")
    return "Desconhecido"

def get_titulo_safe(props, coluna_nome):
    if coluna_nome and coluna_nome in props:
        col = props[coluna_nome]
        if col and isinstance(col, dict):
            titulos = col.get("title", [])
            if titulos and len(titulos) > 0:
                return titulos[0].get("plain_text", "Sem nome")
    return "Sem nome"

def get_texto_safe(props, coluna_nome):
    if coluna_nome and coluna_nome in props:
        col = props[coluna_nome]
        if col and isinstance(col, dict):
            textos = col.get("rich_text", [])
            if textos and len(textos) > 0:
                return textos[0].get("plain_text", "")
    return ""

def get_people_safe(props, coluna_nome):
    if coluna_nome and coluna_nome in props:
        col = props[coluna_nome]
        if col and isinstance(col, dict):
            pessoas = col.get("people", [])
            if pessoas and len(pessoas) > 0:
                return pessoas[0].get("name", "Não definido")
    return "Não definido"

def baixar_arquivo_notion(url):
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Accept': '*/*'})
        with urllib.request.urlopen(req, timeout=30, context=ctx) as response:
            return response.read()
    except:
        return None

def get_opcoes_select(db_info, coluna_nome):
    if not coluna_nome or coluna_nome not in db_info.get("properties", {}):
        return []
    prop = db_info["properties"][coluna_nome]
    if prop.get("type") == "select":
        options = prop.get("select", {}).get("options", [])
        return [opt.get("name") for opt in options if opt.get("name")]
    return []

notion = Client(auth=NOTION_TOKEN)

id_projetos = encontrar_tabela("Projetos")
id_cenarios = encontrar_tabela("Cenário")
id_analises = encontrar_tabela("Análises")

if not all([id_projetos, id_cenarios, id_analises]):
    st.error("Tabelas não encontradas no Notion. Verifique se a integração tem acesso a elas.")
    st.stop()

db_info_analises = notion.databases.retrieve(database_id=id_analises)

with st.sidebar:
    st.markdown("### Compliance Tributário")
    st.markdown("---")
    
    try:
        projetos_response = notion.databases.query(database_id=id_projetos)
        projetos = projetos_response.get("results", [])
        
        if projetos:
            lista_projetos = []
            for proj in projetos:
                props = proj.get("properties", {})
                col_titulo = encontrar_coluna_title(props)
                nome_proj = get_titulo_safe(props, col_titulo)
                lista_projetos.append({"id": proj["id"], "nome": nome_proj})
            
            st.markdown("**Projetos**")
            projeto_escolhido = st.selectbox(
                "Selecione o projeto:",
                options=lista_projetos,
                format_func=lambda x: x["nome"],
                label_visibility="collapsed"
            )
            
            if projeto_escolhido:
                st.markdown("---")
                st.success(f"✅ {projeto_escolhido['nome']}")
        else:
            st.warning("Nenhum projeto encontrado.")
    except Exception as e:
        st.error(f"Erro: {e}")

if 'projeto_escolhido' in dir() and projeto_escolhido:
    st.markdown(f"""
    <div class="header">
        <h1>Compliance Tributário</h1>
        <p>Projeto: {projeto_escolhido['nome']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        cenarios_response = notion.databases.query(database_id=id_cenarios, filter={"property": "Projeto", "relation": {"contains": projeto_escolhido["id"]}})
        cenarios = cenarios_response.get("results", [])
        
        if not cenarios:
            st.info("Nenhum cenário encontrado para este projeto.")
        else:
            todas_props = db_info_analises.get("properties", {})
            coluna_titulo_analise = encontrar_coluna_title(todas_props)
            
            nomes_colunas = {
                "setor": ["Setor", "Área", "Area", "Departamento"],
                "status": ["Status", "Situação", "Situacao"],
                "motivo": ["Motivo", "Motivo da Reprovação", "Observação", "Comentario"],
                "data": ["Data", "Date", "Data da Análise"]
            }
            
            colunas_reais = {}
            for chave, possiveis in nomes_colunas.items():
                colunas_reais[chave] = encontrar_coluna(todas_props, possiveis)
            
            col_relation = None
            for prop_name, prop_info in todas_props.items():
                if prop_info.get("type") == "relation":
                    col_relation = prop_name
                    break
            
            opcoes_setor = get_opcoes_select(db_info_analises, colunas_reais.get("setor"))
            opcoes_status = get_opcoes_select(db_info_analises, colunas_reais.get("status"))
            
            if not opcoes_setor:
                opcoes_setor = ["Contabilidade", "Apuração", "Fiscal", "Jurídico", "Auditoria"]
            if not opcoes_status:
                opcoes_status = ["Aprovado", "Reprovado", "Em Análise"]
            
            st.markdown('<div class="section-label">Cenários</div>', unsafe_allow_html=True)
            
            for cenario in cenarios:
                props = cenario.get("properties", {})
                col_titulo_cenario = encontrar_coluna_title(props)
                nome_cenario = get_titulo_safe(props, col_titulo_cenario)
                status = get_status_safe(props, "Status")
                responsavel = get_people_safe(props, "Responsável")
                
                anexos = []
                if "Anexos" in props:
                    arquivos = props["Anexos"].get("files", [])
                    if arquivos:
                        for arquivo in arquivos:
                            if arquivo.get("external", {}).get("url"):
                                anexos.append({"nome": arquivo.get("name", "Arquivo"), "url": arquivo["external"]["url"]})
                            elif arquivo.get("file", {}).get("url"):
                                anexos.append({"nome": arquivo.get("name", "Arquivo"), "url": arquivo["file"]["url"]})
                
                if status == "Aprovado":
                    badge_html = '<span class="status-badge status-aprovado">Aprovado</span>'
                elif status == "Reprovado":
                    badge_html = '<span class="status-badge status-reprovado">Reprovado</span>'
                else:
                    badge_html = '<span class="status-badge status-pendente">Pronto para análise</span>'
                
                with st.expander(nome_cenario, expanded=False):
                    st.markdown(f'<div class="scenario-container"><div class="scenario-header"><div class="scenario-title">{nome_cenario}</div>{badge_html}</div></div>', unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="info-section">
                        <div class="info-grid">
                            <div class="info-item">
                                <div class="info-label">Responsável</div>
                                <div class="info-value">{responsavel}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Status</div>
                                <div class="info-value">{status}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if anexos:
                        titulo_anexos = "Anexo" if len(anexos) == 1 else "Anexos"
                        st.markdown(f"""
                        <div class="files-section">
                            <div class="files-label">{titulo_anexos} ({len(anexos)})</div>
                            <div class="files-message">Baixe os documentos abaixo para revisar antes de registrar sua análise.</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        for idx, arquivo in enumerate(anexos):
                            conteudo = baixar_arquivo_notion(arquivo['url'])
                            if conteudo:
                                col_nome, col_btn = st.columns([4, 1])
                                with col_nome:
                                    st.markdown(f'<div class="file-row" style="margin-bottom: 0;"><div class="file-name">{arquivo["nome"]}</div></div>', unsafe_allow_html=True)
                                with col_btn:
                                    # ✅ CORREÇÃO: Trocado type="tertiary" por type="secondary"
                                    st.download_button(label="Baixar", data=conteudo, file_name=arquivo['nome'], mime="application/octet-stream", key=f"download_{cenario['id']}_{idx}", type="secondary", use_container_width=True)
                            else:
                                st.markdown(f'<div class="file-row"><div class="file-name">{arquivo["nome"]}</div><a href="{arquivo["url"]}" target="_blank" style="background: white; color: #FF6C12; padding: 0.5rem 1rem; border-radius: 8px; text-decoration: none; font-weight: 600; border: 2px solid #FF6C12;">Abrir</a></div>', unsafe_allow_html=True)
                            st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)
                    else:
                        st.info("Nenhum anexo disponível")
                    
                    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div class="form-section">
                        <div class="form-header">
                            <h3 class="form-title">Fazer análise</h3>
                            <p class="form-message">Preencha os campos abaixo para registrar sua análise. Cada setor só pode analisar uma vez.</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.form(key=f"form_analise_{cenario['id']}"):
                        col_f1, col_f2 = st.columns(2)
                        with col_f1:
                            nome_input = st.text_input("Analista responsável", placeholder="Ex: João Silva")
                            setor_input = st.selectbox("Setor", options=[""] + opcoes_setor, format_func=lambda x: "Selecione o setor" if x == "" else x, index=0)
                        with col_f2:
                            status_input = st.selectbox("Status", options=[""] + opcoes_status, format_func=lambda x: "Selecione o status" if x == "" else x, index=0)
                            motivo_input = st.text_area("Motivo (obrigatório se reprovado)", placeholder="Explique o motivo da reprovação...")
                        
                        submit = st.form_submit_button("Salvar análise", type="primary", use_container_width=True)
                        
                        if submit:
                            if not nome_input:
                                st.error("Preencha o nome do analista.")
                            elif not setor_input:
                                st.error("Selecione o setor.")
                            elif not status_input:
                                st.error("Selecione o status.")
                            elif status_input == "Reprovado" and not motivo_input:
                                st.error("Informe o motivo da reprovação.")
                            else:
                                analises_existentes = notion.databases.query(database_id=id_analises, filter={"property": col_relation, "relation": {"contains": cenario["id"]}})
                                setor_ja_analisou = False
                                for analise_existente in analises_existentes.get("results", []):
                                    a_props = analise_existente.get("properties", {})
                                    setor_existente = get_status_safe(a_props, colunas_reais.get("setor"))
                                    if setor_existente == setor_input:
                                        setor_ja_analisou = True
                                        break
                                
                                if setor_ja_analisou:
                                    st.error(f"O setor '{setor_input}' já realizou uma análise deste cenário.")
                                else:
                                    try:
                                        data_hoje = datetime.now().strftime("%Y-%m-%d")
                                        propriedades = {}
                                        if coluna_titulo_analise:
                                            propriedades[coluna_titulo_analise] = {"title": [{"text": {"content": nome_input}}]}
                                        if colunas_reais.get("setor"):
                                            propriedades[colunas_reais["setor"]] = {"select": {"name": setor_input}}
                                        if colunas_reais.get("status"):
                                            propriedades[colunas_reais["status"]] = {"select": {"name": status_input}}
                                        if colunas_reais.get("motivo"):
                                            propriedades[colunas_reais["motivo"]] = {"rich_text": [{"text": {"content": motivo_input}}] if motivo_input else []}
                                        if colunas_reais.get("data"):
                                            propriedades[colunas_reais["data"]] = {"date": {"start": data_hoje}}
                                        if col_relation:
                                            propriedades[col_relation] = {"relation": [{"id": cenario["id"]}]}
                                        
                                        notion.pages.create(parent={"database_id": id_analises}, properties=propriedades)
                                        st.success(f"Análise de '{nome_input}' salva com sucesso!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Erro ao salvar: {e}")
    except Exception as e:
        st.error(f"Erro: {e}")
