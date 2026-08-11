import streamlit as st
from notion_client import Client
from datetime import datetime
import urllib.request
import textwrap
import ssl
import os
import html


# ============================================================
# CONFIGURAÇÃO
# ============================================================

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")

if not NOTION_TOKEN:
    st.error("A variável NOTION_TOKEN não foi configurada no Railway.")
    st.stop()

notion = Client(auth=NOTION_TOKEN)

st.set_page_config(
    page_title="Compliance Tributário",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# TEXTO DA TELA INICIAL (EDITE AQUI SE QUISER)
# ============================================================

TEXTO_INICIAL = (
    "Este painel é exclusivo da área de Compliance. "
    "Selecione o projeto para consultar os cenários, "
    "baixar os documentos e registrar a análise do seu setor."
)


# ============================================================
# RENDERIZAÇÃO DE HTML (CORREÇÃO DEFINITIVA)
# ============================================================

def render_html(conteudo):
    conteudo = textwrap.dedent(conteudo)
    linhas = [linha.strip() for linha in conteudo.splitlines()]
    linhas = [linha for linha in linhas if linha]
    st.markdown("\n".join(linhas), unsafe_allow_html=True)


# ============================================================
# CSS
# ============================================================

render_html(
    """
    <meta name="google" content="notranslate">
    <style>

    .stApp { background-color: #f4f7fb; }

    .main .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* Sidebar completamente escondida */
    section[data-testid="stSidebar"] { display: none; }

    /* ---------- TELA INICIAL ---------- */

    .landing {
        text-align: center;
        padding: 3.5rem 1rem 1rem;
    }

    .landing-title {
        color: #16324f;
        font-size: 2.6rem;
        font-weight: 800;
        letter-spacing: -1px;
        margin: 0;
    }

    .landing-bar {
        width: 64px;
        height: 4px;
        background: #0f5b9f;
        border-radius: 2px;
        margin: 1rem auto 0;
    }

    .landing-text {
        color: #5c6b7a;
        font-size: 0.95rem;
        margin-top: 1.1rem;
    }

    .landing-label {
        color: #5c6b7a;
        font-size: 0.72rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1.4px;
        margin-top: 3rem;
        margin-bottom: 0.6rem;
    }

    /* ---------- CABEÇALHO ---------- */

    .page-header {
        background: linear-gradient(135deg, #0f5b9f 0%, #155f9f 100%);
        border-radius: 18px;
        padding: 2.4rem 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 25px rgba(15, 91, 159, 0.12);
    }

    .page-title {
        color: white;
        font-size: 2.35rem;
        font-weight: 750;
        text-align: center;
        margin: 0;
        letter-spacing: -1px;
    }

    .page-subtitle {
        color: rgba(255,255,255,0.88);
        font-size: 1rem;
        text-align: center;
        margin-top: 0.55rem;
    }

    .section-label {
        color: #5c6b7a;
        font-size: 0.72rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1.4px;
        margin-top: 1.3rem;
        margin-bottom: 0.65rem;
    }

    .scenario-container {
        background: white;
        border: 1px solid #e3e8ee;
        border-radius: 14px;
        padding: 1.25rem 1.35rem;
        margin-bottom: 1rem;
        box-shadow: 0 3px 12px rgba(20, 40, 60, 0.04);
    }

    .scenario-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
    }

    .scenario-title {
        color: #075da8;
        font-size: 1.35rem;
        font-weight: 750;
        letter-spacing: -0.25px;
    }

    .status-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border-radius: 999px;
        padding: 0.45rem 0.85rem;
        font-size: 0.70rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.3px;
        white-space: nowrap;
    }

    .status-pendente { color: #075da8; background: #edf5fc; border: 1px solid #b9d7ef; }
    .status-aprovado { color: #247043; background: #edf8f1; border: 1px solid #b9dec5; }
    .status-reprovado { color: #a33a3a; background: #fff0f0; border: 1px solid #e8bcbc; }

    .info-section {
        background: #f8fafc;
        border-radius: 10px;
        padding: 1rem 1.1rem;
        margin-top: 0.8rem;
    }

    .info-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
    }

    .info-item { min-width: 0; }

    .info-label {
        color: #7a8794;
        font-size: 0.70rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.7px;
        margin-bottom: 0.25rem;
    }

    .info-value {
        color: #243447;
        font-size: 0.93rem;
        font-weight: 600;
    }

    /* ---------- ANEXOS ---------- */

    .files-section { margin-top: 1.3rem; margin-bottom: 0.7rem; }

    .files-label {
        color: #26384a;
        font-size: 0.9rem;
        font-weight: 750;
        margin-bottom: 0.15rem;
    }

    .files-message { color: #7a8794; font-size: 0.8rem; }

    .file-row {
        display: flex;
        align-items: center;
        background: white;
        border: 1px solid #e3e8ee;
        border-radius: 9px;
        padding: 0.55rem 0.85rem;
        margin-top: 0.45rem;
    }

    .file-name {
        color: #314254;
        font-size: 0.87rem;
        font-weight: 600;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* ---------- ÍCONES DE LINHA (visualizar / baixar) ---------- */

    .icon-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        background: #ffffff;
        border: 1px solid #dfe5eb;
        border-radius: 8px;
        padding: 0.45rem 0.55rem;
        margin-top: 0.45rem;
        color: #243447;
        text-decoration: none;
        line-height: 1;
    }

    .icon-btn:hover {
        color: #0f5b9f;
        border-color: #0f5b9f;
        background: #edf5fc;
    }

    .icon-btn svg { display: block; }

    /* Botão de download: texto invisível, ícone de linha no centro */
    div[data-testid="stDownloadButton"] button {
        background-color: #ffffff;
        background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23243447' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'><line x1='12' y1='4' x2='12' y2='15'></line><polyline points='6 9 12 15 18 9'></polyline><line x1='5' y1='20' x2='19' y2='20'></line></svg>");
        background-repeat: no-repeat;
        background-position: center center;
        background-size: 18px 18px;
        border: 1px solid #dfe5eb;
        border-radius: 8px;
        padding: 0.45rem 0.55rem;
        color: transparent !important;
    }

    div[data-testid="stDownloadButton"] button p {
        color: transparent !important;
        margin: 0;
    }

    div[data-testid="stDownloadButton"] button:hover {
        border-color: #0f5b9f;
        background-color: #edf5fc;
    }

    .section-divider { height: 1px; background: #e5e9ee; margin: 1.5rem 0; }

    .form-section { margin-bottom: 1rem; }

    .form-title {
        color: #25384a;
        font-size: 1.15rem;
        font-weight: 750;
        margin: 0 0 0.25rem 0;
    }

    .form-message { color: #748292; font-size: 0.82rem; margin: 0; }

    div[data-baseweb="select"] > div { border-radius: 8px; }
    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea { border-radius: 8px; }
    .stButton button { border-radius: 8px; font-weight: 700; }

    /* BOTÃO SALVAR ANÁLISE AZUL */
    .stForm button,
    form[data-testid="stForm"] button,
    [data-testid="stFormSubmitButton"] button {
        background-color: #0f5b9f !important;
        background-image: none !important;
        color: #ffffff !important;
        border: 1px solid #0f5b9f !important;
    }

    .stForm button:hover,
    form[data-testid="stForm"] button:hover,
    [data-testid="stFormSubmitButton"] button:hover {
        background-color: #0d4f8b !important;
        border-color: #0d4f8b !important;
    }

    div[data-testid="stExpander"] { background: transparent; border: none; }
    div[data-testid="stExpander"] details { border: none !important; }
    div[data-testid="stExpander"] summary {
        background: white;
        border: 1px solid #dfe5eb;
        border-radius: 12px;
        padding: 0.9rem 1rem;
    }
    div[data-testid="stExpander"] summary:hover { border-color: #a9c9e4; }

    @media (max-width: 800px) {
        .page-title { font-size: 1.8rem; }
        .landing-title { font-size: 1.9rem; }
        .info-grid { grid-template-columns: 1fr; }
        .scenario-header { flex-direction: column; align-items: flex-start; }
    }

    </style>
    """
)


# ============================================================
# FUNÇÕES DO NOTION
# ============================================================

def encontrar_tabela(nome_tabela):
    try:
        response = notion.search(query=nome_tabela)
        for resultado in response.get("results", []):
            titulo = resultado.get("title", [])
            if titulo:
                texto = titulo[0].get("plain_text", "")
                if texto.strip().lower() == nome_tabela.strip().lower():
                    return resultado["id"]
            propriedades = resultado.get("properties", {})
            if "title" in propriedades:
                props_title = propriedades["title"].get("title", [])
                if props_title:
                    texto = props_title[0].get("plain_text", "")
                    if texto.strip().lower() == nome_tabela.strip().lower():
                        return resultado["id"]
        return None
    except Exception:
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
    props_lower = {nome.lower(): nome for nome in props.keys()}
    for nome in nomes_possiveis:
        if nome.lower() in props_lower:
            return props_lower[nome.lower()]
    return None


def get_status_safe(props, coluna_nome):
    if not coluna_nome or coluna_nome not in props:
        return "Não definido"
    col = props[coluna_nome]
    if not isinstance(col, dict):
        return "Não definido"
    select = col.get("select")
    if isinstance(select, dict):
        return select.get("name", "Não definido")
    status = col.get("status")
    if isinstance(status, dict):
        return status.get("name", "Não definido")
    return "Não definido"


def get_titulo_safe(props, coluna_nome):
    if not coluna_nome or coluna_nome not in props:
        return "Sem nome"
    col = props[coluna_nome]
    if not isinstance(col, dict):
        return "Sem nome"
    titulos = col.get("title", [])
    if titulos:
        return titulos[0].get("plain_text", "Sem nome")
    return "Sem nome"


def get_people_safe(props, coluna_nome):
    if not coluna_nome or coluna_nome not in props:
        return "Não definido"
    col = props[coluna_nome]
    if not isinstance(col, dict):
        return "Não definido"
    pessoas = col.get("people", [])
    if pessoas:
        pessoa = pessoas[0]
        nome = pessoa.get("name")
        if nome:
            return nome
        email = pessoa.get("person", {}).get("email")
        if email:
            return email
    return "Não definido"


def baixar_arquivo_notion(url):
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
        )
        with urllib.request.urlopen(req, timeout=30, context=ctx) as response:
            return response.read()
    except Exception:
        return None


def get_opcoes_select(db_info, coluna_nome):
    if not coluna_nome:
        return []
    propriedades = db_info.get("properties", {})
    if coluna_nome not in propriedades:
        return []
    prop = propriedades[coluna_nome]
    if prop.get("type") == "select":
        options = prop.get("select", {}).get("options", [])
        return [opt.get("name") for opt in options if opt.get("name")]
    if prop.get("type") == "status":
        options = prop.get("status", {}).get("options", [])
        return [opt.get("name") for opt in options if opt.get("name")]
    return []


def criar_propriedade_opcao(tipo, valor):
    if tipo == "status":
        return {"status": {"name": valor}}
    return {"select": {"name": valor}}


# ============================================================
# ÍCONES SVG (estilo linha, iguais entre si)
# ============================================================

ICONE_OLHO = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" '
    'fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" '
    'stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z">'
    '</path><circle cx="12" cy="12" r="3"></circle></svg>'
)

ICONE_DOWNLOAD = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" '
    'fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" '
    'stroke-linejoin="round"><line x1="12" y1="4" x2="12" y2="15"></line>'
    '<polyline points="6 9 12 15 18 9"></polyline>'
    '<line x1="5" y1="20" x2="19" y2="20"></line></svg>'
)


# ============================================================
# LOCALIZAR DATABASES
# ============================================================

id_projetos = encontrar_tabela("Projetos")
id_cenarios = encontrar_tabela("Cenário")
id_analises = encontrar_tabela("Análises")

if not id_projetos:
    st.error("Tabela 'Projetos' não encontrada no Notion.")
    st.stop()

if not id_cenarios:
    st.error("Tabela 'Cenário' não encontrada no Notion.")
    st.stop()

if not id_analises:
    st.error("Tabela 'Análises' não encontrada no Notion.")
    st.stop()

try:
    db_info_analises = notion.databases.retrieve(database_id=id_analises)
except Exception as e:
    st.error(f"Não foi possível acessar a tabela de Análises: {e}")
    st.stop()


# ============================================================
# ESTADO DA SESSÃO (controla tela inicial x tela do projeto)
# ============================================================

if "projeto_ativo" not in st.session_state:
    st.session_state.projeto_ativo = None


# ============================================================
# CARREGAR PROJETOS (usado na tela inicial)
# ============================================================

lista_projetos = []

try:
    projetos_response = notion.databases.query(database_id=id_projetos)

    for proj in projetos_response.get("results", []):
        props = proj.get("properties", {})
        col_titulo = encontrar_coluna_title(props)
        nome_proj = get_titulo_safe(props, col_titulo)
        lista_projetos.append({"id": proj["id"], "nome": nome_proj})

except Exception as e:
    st.error(f"Erro ao carregar projetos: {e}")
    st.stop()


# ============================================================
# TELA INICIAL (CAPA)
# ============================================================

if st.session_state.projeto_ativo is None:

    col_e, col_c, col_d = st.columns([1, 2, 1])

    with col_c:

        render_html(
            f"""
            <div class="landing">
                <div class="landing-title">Compliance Tributário</div>
                <div class="landing-bar"></div>
                <div class="landing-text">{html.escape(TEXTO_INICIAL)}</div>
            </div>
            """
        )

        if lista_projetos:

            render_html('<div class="landing-label">Escolher o projeto</div>')

            projeto_selecionado = st.selectbox(
                "Escolher o projeto",
                options=[""] + lista_projetos,
                format_func=lambda x: "Selecione o projeto" if x == "" else x["nome"],
                label_visibility="collapsed"
            )

            if st.button("Iniciar", type="primary", use_container_width=True):
                if projeto_selecionado == "":
                    st.warning("Escolha um projeto para continuar.")
                else:
                    st.session_state.projeto_ativo = projeto_selecionado
                    st.rerun()

        else:
            st.warning("Nenhum projeto encontrado no Notion.")

    st.stop()


# ============================================================
# A PARTIR DAQUI: PROJETO ATIVO
# ============================================================

projeto_escolhido = st.session_state.projeto_ativo

# Botão "Trocar projeto" no topo direito
col_topo, col_trocar = st.columns([6, 1])

with col_trocar:
    if st.button("Trocar projeto", use_container_width=True):
        st.session_state.projeto_ativo = None
        st.rerun()

nome_projeto = html.escape(projeto_escolhido["nome"])

render_html(
    f"""
    <div class="page-header">
        <div class="page-title">Compliance Tributário</div>
        <div class="page-subtitle">Projeto: {nome_projeto}</div>
    </div>
    """
)

try:
    cenarios_response = notion.databases.query(
        database_id=id_cenarios,
        filter={
            "property": "Projeto",
            "relation": {"contains": projeto_escolhido["id"]}
        }
    )
    cenarios = cenarios_response.get("results", [])
except Exception as e:
    st.error(f"Erro ao carregar os cenários: {e}")
    st.stop()

if not cenarios:
    render_html('<div class="section-label">Cenários</div>')
    st.info("Nenhum cenário encontrado para este projeto.")

else:

    todas_props = db_info_analises.get("properties", {})
    coluna_titulo_analise = encontrar_coluna_title(todas_props)

    nomes_colunas = {
        "setor": ["Setor", "Área", "Area", "Departamento"],
        "status": ["Status", "Situação", "Situacao"],
        "motivo": ["Motivo", "Motivo da Reprovação", "Observação",
                   "Observacao", "Comentario", "Comentário"],
        "data": ["Data", "Date", "Data da Análise"]
    }

    colunas_reais = {}
    for chave, possiveis in nomes_colunas.items():
        colunas_reais[chave] = encontrar_coluna(todas_props, possiveis)

    tipo_setor = None
    tipo_status = None
    if colunas_reais.get("setor"):
        tipo_setor = todas_props[colunas_reais["setor"]].get("type")
    if colunas_reais.get("status"):
        tipo_status = todas_props[colunas_reais["status"]].get("type")

    col_relation = None
    for prop_name, prop_info in todas_props.items():
        if prop_info.get("type") != "relation":
            continue
        if prop_name.lower() in ["cenário", "cenario", "cenários", "cenarios"]:
            col_relation = prop_name
            break

    if not col_relation:
        for prop_name, prop_info in todas_props.items():
            if prop_info.get("type") == "relation":
                col_relation = prop_name
                break

    if not col_relation:
        st.error("A tabela 'Análises' não possui uma relação com os cenários.")
        st.stop()

    opcoes_setor = get_opcoes_select(db_info_analises, colunas_reais.get("setor"))
    opcoes_status = get_opcoes_select(db_info_analises, colunas_reais.get("status"))

    if not opcoes_setor:
        opcoes_setor = ["Contabilidade", "Apuração", "Fiscal", "Jurídico", "Auditoria"]
    if not opcoes_status:
        opcoes_status = ["Aprovado", "Reprovado", "Em Análise"]

    render_html('<div class="section-label">Cenários</div>')

    # ========================================================
    # LOOP DOS CENÁRIOS (fechados por padrão)
    # ========================================================

    for cenario in cenarios:

        props = cenario.get("properties", {})

        col_titulo_cenario = encontrar_coluna_title(props)
        nome_cenario = get_titulo_safe(props, col_titulo_cenario)
        nome_cenario_html = html.escape(nome_cenario)

        coluna_status_cenario = encontrar_coluna(
            props, ["Status", "Situação", "Situacao"]
        )
        status = get_status_safe(props, coluna_status_cenario)

        coluna_responsavel = encontrar_coluna(
            props, ["Responsável", "Responsavel"]
        )
        responsavel = get_people_safe(props, coluna_responsavel)

        anexos = []
        coluna_anexos = encontrar_coluna(
            props, ["Anexos", "Anexo", "Arquivos", "Documentos"]
        )

        if coluna_anexos:
            arquivos = props[coluna_anexos].get("files", [])
            for arquivo in arquivos:
                nome_arquivo = arquivo.get("name", "Arquivo")
                url_arquivo = None
                if arquivo.get("external"):
                    url_arquivo = arquivo["external"].get("url")
                elif arquivo.get("file"):
                    url_arquivo = arquivo["file"].get("url")
                if url_arquivo:
                    anexos.append({"nome": nome_arquivo, "url": url_arquivo})

        status_lower = str(status).strip().lower()

        if status_lower == "aprovado":
            badge_html = '<span class="status-badge status-aprovado">Aprovado</span>'
        elif status_lower == "reprovado":
            badge_html = '<span class="status-badge status-reprovado">Reprovado</span>'
        else:
            badge_html = '<span class="status-badge status-pendente">Pronto para análise</span>'

        with st.expander(f"▸ {nome_cenario}", expanded=False):

            render_html(
                f"""
                <div class="scenario-container">
                    <div class="scenario-header">
                        <div class="scenario-title">{nome_cenario_html}</div>
                        {badge_html}
                    </div>
                </div>
                """
            )

            responsavel_html = html.escape(str(responsavel))
            status_html = html.escape(str(status))

            render_html(
                f"""
                <div class="info-section">
                    <div class="info-grid">
                        <div class="info-item">
                            <div class="info-label">Responsável</div>
                            <div class="info-value">{responsavel_html}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Status</div>
                            <div class="info-value">{status_html}</div>
                        </div>
                    </div>
                </div>
                """
            )

            # ------------------------------------------------
            # ANEXOS (ícones de linha + tooltip no hover)
            # ------------------------------------------------

            if anexos:
                titulo_anexos = "Anexo" if len(anexos) == 1 else "Anexos"

                render_html(
                    f"""
                    <div class="files-section">
                        <div class="files-label">{titulo_anexos} ({len(anexos)})</div>
                        <div class="files-message">Passe o cursor sobre os ícones para visualizar ou baixar cada documento.</div>
                    </div>
                    """
                )

                for idx, arquivo in enumerate(anexos):

                    nome_arquivo_html = html.escape(arquivo["nome"])
                    tooltip_nome = html.escape(arquivo["nome"], quote=True)
                    url_segura = html.escape(arquivo["url"], quote=True)
                    conteudo = baixar_arquivo_notion(arquivo["url"])

                    col_nome, col_ver, col_baixar = st.columns([6, 1, 1])

                    with col_nome:
                        render_html(
                            f"""
                            <div class="file-row">
                                <div class="file-name">📄 {nome_arquivo_html}</div>
                            </div>
                            """
                        )

                    with col_ver:
                        render_html(
                            f"""
                            <a class="icon-btn" href="{url_segura}" target="_blank"
                               title="Visualizar: {tooltip_nome}">{ICONE_OLHO}</a>
                            """
                        )

                    with col_baixar:
                        if conteudo:
                            st.download_button(
                                label="Baixar",
                                data=conteudo,
                                file_name=arquivo["nome"],
                                mime="application/octet-stream",
                                key=f"download_{cenario['id']}_{idx}",
                                help=f"Baixar: {arquivo['nome']}",
                                use_container_width=True
                            )
                        else:
                            render_html(
                                f"""
                                <a class="icon-btn" href="{url_segura}" target="_blank"
                                   title="Baixar: {tooltip_nome}">{ICONE_DOWNLOAD}</a>
                                """
                            )
            else:
                st.info("Nenhum anexo disponível para este cenário.")

            render_html('<div class="section-divider"></div>')

            render_html(
                """
                <div class="form-section">
                    <div class="form-title">Registrar análise</div>
                    <div class="form-message">Preencha os campos abaixo para registrar a análise deste setor. Cada setor pode analisar este cenário apenas uma vez.</div>
                </div>
                """
            )

            with st.form(key=f"form_analise_{cenario['id']}"):

                col_f1, col_f2 = st.columns(2)

                with col_f1:
                    nome_input = st.text_input(
                        "Analista responsável",
                        placeholder="Ex.: João Silva"
                    )
                    setor_input = st.selectbox(
                        "Setor",
                        options=[""] + opcoes_setor,
                        format_func=lambda x: "Selecione o setor" if x == "" else x
                    )

                with col_f2:
                    status_input = st.selectbox(
                        "Resultado da análise",
                        options=[""] + opcoes_status,
                        format_func=lambda x: "Selecione o resultado" if x == "" else x
                    )
                    motivo_input = st.text_area(
                        "Motivo",
                        placeholder="Informe o motivo caso a análise seja reprovada."
                    )

                submit = st.form_submit_button(
                    "Salvar análise",
                    type="primary",
                    use_container_width=True
                )

                if submit:

                    if not nome_input.strip():
                        st.error("Informe o nome do analista.")
                    elif not setor_input:
                        st.error("Selecione o setor responsável.")
                    elif not status_input:
                        st.error("Selecione o resultado da análise.")
                    elif status_input.strip().lower() == "reprovado" and not motivo_input.strip():
                        st.error("Informe o motivo da reprovação.")
                    else:
                        try:
                            analises_existentes = notion.databases.query(
                                database_id=id_analises,
                                filter={
                                    "property": col_relation,
                                    "relation": {"contains": cenario["id"]}
                                }
                            )

                            setor_ja_analisou = False

                            for analise_existente in analises_existentes.get("results", []):
                                a_props = analise_existente.get("properties", {})
                                setor_existente = get_status_safe(
                                    a_props, colunas_reais.get("setor")
                                )
                                if setor_existente.strip().lower() == setor_input.strip().lower():
                                    setor_ja_analisou = True
                                    break

                            if setor_ja_analisou:
                                st.error(
                                    f"O setor '{setor_input}' já realizou uma análise deste cenário."
                                )
                            else:
                                data_hoje = datetime.now().strftime("%Y-%m-%d")
                                propriedades = {}

                                if coluna_titulo_analise:
                                    propriedades[coluna_titulo_analise] = {
                                        "title": [{"text": {"content": nome_input.strip()}}]
                                    }

                                if colunas_reais.get("setor"):
                                    propriedades[colunas_reais["setor"]] = criar_propriedade_opcao(
                                        tipo_setor, setor_input
                                    )

                                if colunas_reais.get("status"):
                                    propriedades[colunas_reais["status"]] = criar_propriedade_opcao(
                                        tipo_status, status_input
                                    )

                                if colunas_reais.get("motivo"):
                                    if motivo_input.strip():
                                        propriedades[colunas_reais["motivo"]] = {
                                            "rich_text": [{"text": {"content": motivo_input.strip()}}]
                                        }
                                    else:
                                        propriedades[colunas_reais["motivo"]] = {"rich_text": []}

                                if colunas_reais.get("data"):
                                    propriedades[colunas_reais["data"]] = {
                                        "date": {"start": data_hoje}
                                    }

                                propriedades[col_relation] = {
                                    "relation": [{"id": cenario["id"]}]
                                }

                                notion.pages.create(
                                    parent={"database_id": id_analises},
                                    properties=propriedades
                                )

                                st.success(
                                    f"Análise de '{nome_input.strip()}' registrada com sucesso!"
                                )
                                st.rerun()

                        except Exception as e:
                            st.error("Não foi possível salvar a análise.")
                            st.caption(f"Detalhes técnicos: {e}")
