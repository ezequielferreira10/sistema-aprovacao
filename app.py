import streamlit as st
from notion_client import Client
from datetime import datetime
import urllib.request
import ssl
import os
import html
import textwrap


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
    initial_sidebar_state="expanded"
)


# ============================================================
# FUNÇÃO PARA RENDERIZAR HTML
# ============================================================
# O textwrap.dedent() remove a indentação do código HTML.
# Isso evita que o Streamlit mostre as tags <div> na tela.

def render_html(conteudo):
    st.markdown(
        textwrap.dedent(conteudo),
        unsafe_allow_html=True
    )


# ============================================================
# CSS
# ============================================================

render_html(
    """
    <style>

    /* ======================================================
       CONFIGURAÇÃO GERAL
       ====================================================== */

    .stApp {
        background-color: #f4f7fb;
    }

    .main .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }


    /* ======================================================
       SIDEBAR
       ====================================================== */

    section[data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #0f5b9f 0%,
            #125d9f 100%
        );

        border-right: none;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1.5rem;
    }

    section[data-testid="stSidebar"] * {
        color: white;
    }

    .sidebar-brand {
        font-size: 1.25rem;
        font-weight: 700;
        letter-spacing: -0.3px;
        margin-bottom: 1.4rem;
    }

    .sidebar-line {
        height: 1px;
        background: rgba(255,255,255,0.22);
        margin: 0.5rem 0 1.7rem 0;
    }

    .sidebar-label {
        font-size: 0.72rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        opacity: 0.82;
        margin-bottom: 0.55rem;
    }

    .project-selected {
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 10px;
        padding: 0.75rem 0.85rem;
        margin-top: 0.75rem;
        font-size: 0.91rem;
        font-weight: 600;
    }

    .project-icon {
        margin-right: 0.4rem;
    }


    /* ======================================================
       CABEÇALHO
       ====================================================== */

    .page-header {
        background: linear-gradient(
            135deg,
            #0f5b9f 0%,
            #155f9f 100%
        );

        border-radius: 18px;

        padding: 2.4rem 2rem;

        margin-bottom: 2rem;

        box-shadow:
            0 8px 25px rgba(15, 91, 159, 0.12);
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


    /* ======================================================
       TÍTULOS DE SEÇÃO
       ====================================================== */

    .section-label {
        color: #5c6b7a;

        font-size: 0.72rem;

        font-weight: 800;

        text-transform: uppercase;

        letter-spacing: 1.4px;

        margin-top: 1.3rem;

        margin-bottom: 0.65rem;
    }


    /* ======================================================
       CENÁRIO
       ====================================================== */

    .scenario-container {
        background: white;

        border: 1px solid #e3e8ee;

        border-radius: 14px;

        padding: 1.25rem 1.35rem;

        margin-bottom: 1rem;

        box-shadow:
            0 3px 12px rgba(20, 40, 60, 0.04);
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


    /* ======================================================
       STATUS
       ====================================================== */

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

    .status-pendente {
        color: #075da8;

        background: #edf5fc;

        border: 1px solid #b9d7ef;
    }

    .status-aprovado {
        color: #247043;

        background: #edf8f1;

        border: 1px solid #b9dec5;
    }

    .status-reprovado {
        color: #a33a3a;

        background: #fff0f0;

        border: 1px solid #e8bcbc;
    }


    /* ======================================================
       INFORMAÇÕES
       ====================================================== */

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

    .info-item {
        min-width: 0;
    }

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


    /* ======================================================
       ANEXOS
       ====================================================== */

    .files-section {
        margin-top: 1.3rem;

        margin-bottom: 0.7rem;
    }

    .files-label {
        color: #26384a;

        font-size: 0.9rem;

        font-weight: 750;

        margin-bottom: 0.15rem;
    }

    .files-message {
        color: #7a8794;

        font-size: 0.8rem;
    }

    .file-row {
        display: flex;

        align-items: center;

        background: white;

        border: 1px solid #e3e8ee;

        border-radius: 9px;

        padding: 0.7rem 0.85rem;

        margin-top: 0.45rem;
    }

    .file-name {
        color: #314254;

        font-size: 0.87rem;

        font-weight: 600;

        overflow: hidden;

        text-overflow: ellipsis;
    }


    /* ======================================================
       FORMULÁRIO
       ====================================================== */

    .section-divider {
        height: 1px;

        background: #e5e9ee;

        margin: 1.5rem 0;
    }

    .form-section {
        margin-bottom: 1rem;
    }

    .form-title {
        color: #25384a;

        font-size: 1.15rem;

        font-weight: 750;

        margin: 0 0 0.25rem 0;
    }

    .form-message {
        color: #748292;

        font-size: 0.82rem;

        margin: 0;
    }


    /* ======================================================
       INPUTS
       ====================================================== */

    div[data-baseweb="select"] > div {
        border-radius: 8px;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea {
        border-radius: 8px;
    }

    .stButton button {
        border-radius: 8px;

        font-weight: 700;
    }


    /* ======================================================
       EXPANDER
       ====================================================== */

    div[data-testid="stExpander"] {
        background: transparent;

        border: none;
    }

    div[data-testid="stExpander"] details {
        border: none !important;
    }

    div[data-testid="stExpander"] summary {
        background: white;

        border: 1px solid #dfe5eb;

        border-radius: 12px;

        padding: 0.9rem 1rem;
    }

    div[data-testid="stExpander"] summary:hover {
        border-color: #a9c9e4;
    }


    /* ======================================================
       RESPONSIVIDADE
       ====================================================== */

    @media (max-width: 800px) {

        .page-title {
            font-size: 1.8rem;
        }

        .info-grid {
            grid-template-columns: 1fr;
        }

        .scenario-header {
            flex-direction: column;

            align-items: flex-start;
        }

    }

    </style>
    """
)


# ============================================================
# FUNÇÕES DO NOTION
# ============================================================

def encontrar_tabela(nome_tabela):

    try:

        response = notion.search(
            query=nome_tabela,
            filter={
                "property": "object",
                "value": "data_source"
            }
        )

        resultados = response.get(
            "results",
            []
        )

        for resultado in resultados:

            titulo = resultado.get(
                "title",
                []
            )

            if titulo:

                texto = titulo[0].get(
                    "plain_text",
                    ""
                )

                if texto.strip().lower() == nome_tabela.strip().lower():

                    return resultado["id"]


            propriedades = resultado.get(
                "properties",
                {}
            )

            if "title" in propriedades:

                props_title = propriedades[
                    "title"
                ].get(
                    "title",
                    []
                )

                if props_title:

                    texto = props_title[0].get(
                        "plain_text",
                        ""
                    )

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

    # Primeiro tenta correspondência exata
    for nome in nomes_possiveis:

        if nome in props:

            return nome


    # Depois ignora maiúsculas/minúsculas
    props_lower = {
        nome.lower(): nome
        for nome in props.keys()
    }

    for nome in nomes_possiveis:

        if nome.lower() in props_lower:

            return props_lower[
                nome.lower()
            ]


    return None


def get_status_safe(props, coluna_nome):

    if not coluna_nome:
        return "Não definido"

    if coluna_nome not in props:
        return "Não definido"

    col = props[coluna_nome]

    if not isinstance(col, dict):
        return "Não definido"


    # Select
    select = col.get("select")

    if isinstance(select, dict):

        return select.get(
            "name",
            "Não definido"
        )


    # Status
    status = col.get("status")

    if isinstance(status, dict):

        return status.get(
            "name",
            "Não definido"
        )


    return "Não definido"


def get_titulo_safe(props, coluna_nome):

    if not coluna_nome:
        return "Sem nome"

    if coluna_nome not in props:
        return "Sem nome"

    col = props[coluna_nome]

    if not isinstance(col, dict):
        return "Sem nome"

    titulos = col.get(
        "title",
        []
    )

    if titulos:

        return titulos[0].get(
            "plain_text",
            "Sem nome"
        )

    return "Sem nome"


def get_texto_safe(props, coluna_nome):

    if not coluna_nome:
        return ""

    if coluna_nome not in props:
        return ""

    col = props[coluna_nome]

    if not isinstance(col, dict):
        return ""

    textos = col.get(
        "rich_text",
        []
    )

    if textos:

        return textos[0].get(
            "plain_text",
            ""
        )

    return ""


def get_people_safe(props, coluna_nome):

    if not coluna_nome:
        return "Não definido"

    if coluna_nome not in props:
        return "Não definido"

    col = props[coluna_nome]

    if not isinstance(col, dict):
        return "Não definido"

    pessoas = col.get(
        "people",
        []
    )

    if pessoas:

        pessoa = pessoas[0]

        nome = pessoa.get("name")

        if nome:
            return nome

        person = pessoa.get(
            "person",
            {}
        )

        email = person.get("email")

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
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "*/*"
            }
        )

        with urllib.request.urlopen(
            req,
            timeout=30,
            context=ctx
        ) as response:

            return response.read()

    except Exception:

        return None


def get_opcoes_select(
    db_info,
    coluna_nome
):

    if not coluna_nome:
        return []

    propriedades = db_info.get(
        "properties",
        {}
    )

    if coluna_nome not in propriedades:
        return []

    prop = propriedades[
        coluna_nome
    ]


    # Select
    if prop.get("type") == "select":

        options = prop.get(
            "select",
            {}
        ).get(
            "options",
            []
        )

        return [
            opt.get("name")
            for opt in options
            if opt.get("name")
        ]


    # Status
    if prop.get("type") == "status":

        options = prop.get(
            "status",
            {}
        ).get(
            "options",
            []
        )

        return [
            opt.get("name")
            for opt in options
            if opt.get("name")
        ]


    return []


def criar_propriedade_opcao(
    tipo,
    valor
):

    if tipo == "status":

        return {
            "status": {
                "name": valor
            }
        }


    return {
        "select": {
            "name": valor
        }
    }


# ============================================================
# LOCALIZAR DATABASES
# ============================================================

id_projetos = encontrar_tabela(
    "Projetos"
)

id_cenarios = encontrar_tabela(
    "Cenário"
)

id_analises = encontrar_tabela(
    "Análises"
)


if not id_projetos:

    st.error(
        "Tabela 'Projetos' não encontrada no Notion."
    )

    st.stop()


if not id_cenarios:

    st.error(
        "Tabela 'Cenário' não encontrada no Notion."
    )

    st.stop()


if not id_analises:

    st.error(
        "Tabela 'Análises' não encontrada no Notion."
    )

    st.stop()


# ============================================================
# INFORMAÇÕES DA DATABASE DE ANÁLISES
# ============================================================

try:

    db_info_analises = notion.databases.retrieve(
        database_id=id_analises
    )

except Exception as e:

    st.error(
        f"Não foi possível acessar a tabela de Análises: {e}"
    )

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    render_html(
        """
        <div class="sidebar-brand">
            Compliance Tributário
        </div>
        """
    )

    render_html(
        """
        <div class="sidebar-line"></div>
        """
    )

    render_html(
        """
        <div class="sidebar-label">
            Projetos
        </div>
        """
    )


    try:

        projetos_response = notion.databases.query(
            database_id=id_projetos
        )

        projetos = projetos_response.get(
            "results",
            []
        )

        lista_projetos = []


        for proj in projetos:

            props = proj.get(
                "properties",
                {}
            )

            col_titulo = encontrar_coluna_title(
                props
            )

            nome_proj = get_titulo_safe(
                props,
                col_titulo
            )

            lista_projetos.append(
                {
                    "id": proj["id"],
                    "nome": nome_proj
                }
            )


        if lista_projetos:

            projeto_escolhido = st.selectbox(
                "Selecione o projeto",
                options=lista_projetos,
                format_func=lambda x: x["nome"],
                label_visibility="collapsed"
            )


            if projeto_escolhido:

                nome_sidebar = html.escape(
                    projeto_escolhido["nome"]
                )

                render_html(
                    f"""
                    <div class="project-selected">

                        <span class="project-icon">
                            ✓
                        </span>

                        {nome_sidebar}

                    </div>
                    """
                )


        else:

            projeto_escolhido = None

            st.warning(
                "Nenhum projeto encontrado."
            )


    except Exception as e:

        projeto_escolhido = None

        st.error(
            f"Erro ao carregar projetos: {e}"
        )


# ============================================================
# TELA PRINCIPAL
# ============================================================

if projeto_escolhido:

    nome_projeto = html.escape(
        projeto_escolhido["nome"]
    )


    # ========================================================
    # CABEÇALHO
    # ========================================================

    render_html(
        f"""
        <div class="page-header">

            <div class="page-title">
                Compliance Tributário
            </div>

            <div class="page-subtitle">
                Projeto: {nome_projeto}
            </div>

        </div>
        """
    )


    # ========================================================
    # BUSCAR CENÁRIOS
    # ========================================================

    try:

        cenarios_response = notion.databases.query(
            database_id=id_cenarios,
            filter={
                "property": "Projeto",
                "relation": {
                    "contains": projeto_escolhido["id"]
                }
            }
        )

        cenarios = cenarios_response.get(
            "results",
            []
        )


    except Exception as e:

        st.error(
            f"Erro ao carregar os cenários: {e}"
        )

        st.stop()


    # ========================================================
    # NENHUM CENÁRIO
    # ========================================================

    if not cenarios:

        render_html(
            """
            <div class="section-label">
                Cenários
            </div>
            """
        )

        st.info(
            "Nenhum cenário encontrado para este projeto."
        )


    # ========================================================
    # EXISTEM CENÁRIOS
    # ========================================================

    else:

        todas_props = db_info_analises.get(
            "properties",
            {}
        )


        # ----------------------------------------------------
        # TÍTULO DA ANÁLISE
        # ----------------------------------------------------

        coluna_titulo_analise = (
            encontrar_coluna_title(
                todas_props
            )
        )


        # ----------------------------------------------------
        # COLUNAS
        # ----------------------------------------------------

        nomes_colunas = {

            "setor": [
                "Setor",
                "Área",
                "Area",
                "Departamento"
            ],

            "status": [
                "Status",
                "Situação",
                "Situacao"
            ],

            "motivo": [
                "Motivo",
                "Motivo da Reprovação",
                "Observação",
                "Observacao",
                "Comentario",
                "Comentário"
            ],

            "data": [
                "Data",
                "Date",
                "Data da Análise"
            ]

        }


        colunas_reais = {}


        for chave, possiveis in nomes_colunas.items():

            colunas_reais[chave] = encontrar_coluna(
                todas_props,
                possiveis
            )


        # ----------------------------------------------------
        # TIPOS
        # ----------------------------------------------------

        tipo_setor = None

        tipo_status = None


        if colunas_reais.get("setor"):

            tipo_setor = todas_props[
                colunas_reais["setor"]
            ].get("type")


        if colunas_reais.get("status"):

            tipo_status = todas_props[
                colunas_reais["status"]
            ].get("type")


        # ----------------------------------------------------
        # RELAÇÃO COM CENÁRIO
        # ----------------------------------------------------

        col_relation = None


        for prop_name, prop_info in todas_props.items():

            if prop_info.get("type") != "relation":
                continue

            nome_lower = prop_name.lower()

            if nome_lower in [
                "cenário",
                "cenario",
                "cenários",
                "cenarios"
            ]:

                col_relation = prop_name

                break


        if not col_relation:

            for prop_name, prop_info in todas_props.items():

                if prop_info.get("type") == "relation":

                    col_relation = prop_name

                    break


        if not col_relation:

            st.error(
                "A tabela 'Análises' não possui uma relação com os cenários."
            )

            st.stop()


        # ----------------------------------------------------
        # OPÇÕES
        # ----------------------------------------------------

        opcoes_setor = get_opcoes_select(
            db_info_analises,
            colunas_reais.get("setor")
        )

        opcoes_status = get_opcoes_select(
            db_info_analises,
            colunas_reais.get("status")
        )


        if not opcoes_setor:

            opcoes_setor = [
                "Contabilidade",
                "Apuração",
                "Fiscal",
                "Jurídico",
                "Auditoria"
            ]


        if not opcoes_status:

            opcoes_status = [
                "Aprovado",
                "Reprovado",
                "Em Análise"
            ]


        # ====================================================
        # TÍTULO CENÁRIOS
        # ====================================================

        render_html(
            """
            <div class="section-label">
                Cenários
            </div>
            """
        )


        # ====================================================
        # LOOP DOS CENÁRIOS
        # ====================================================

        for cenario in cenarios:

            props = cenario.get(
                "properties",
                {}
            )


            # ------------------------------------------------
            # NOME
            # ------------------------------------------------

            col_titulo_cenario = (
                encontrar_coluna_title(
                    props
                )
            )

            nome_cenario = get_titulo_safe(
                props,
                col_titulo_cenario
            )

            nome_cenario_html = html.escape(
                nome_cenario
            )


            # ------------------------------------------------
            # STATUS DO CENÁRIO
            # ------------------------------------------------

            coluna_status_cenario = encontrar_coluna(
                props,
                [
                    "Status",
                    "Situação",
                    "Situacao"
                ]
            )

            status = get_status_safe(
                props,
                coluna_status_cenario
            )


            # ------------------------------------------------
            # RESPONSÁVEL
            # ------------------------------------------------

            coluna_responsavel = encontrar_coluna(
                props,
                [
                    "Responsável",
                    "Responsavel"
                ]
            )

            responsavel = get_people_safe(
                props,
                coluna_responsavel
            )


            # ------------------------------------------------
            # ANEXOS
            # ------------------------------------------------

            anexos = []


            coluna_anexos = encontrar_coluna(
                props,
                [
                    "Anexos",
                    "Anexo",
                    "Arquivos",
                    "Documentos"
                ]
            )


            if coluna_anexos:

                arquivos = props[
                    coluna_anexos
                ].get(
                    "files",
                    []
                )


                for arquivo in arquivos:

                    nome_arquivo = arquivo.get(
                        "name",
                        "Arquivo"
                    )

                    url_arquivo = None


                    if arquivo.get("external"):

                        url_arquivo = arquivo[
                            "external"
                        ].get("url")


                    elif arquivo.get("file"):

                        url_arquivo = arquivo[
                            "file"
                        ].get("url")


                    if url_arquivo:

                        anexos.append(
                            {
                                "nome": nome_arquivo,
                                "url": url_arquivo
                            }
                        )


            # ------------------------------------------------
            # BADGE
            # ------------------------------------------------

            status_lower = str(
                status
            ).strip().lower()


            if status_lower == "aprovado":

                badge_html = """
                <span class="status-badge status-aprovado">
                    Aprovado
                </span>
                """


            elif status_lower == "reprovado":

                badge_html = """
                <span class="status-badge status-reprovado">
                    Reprovado
                </span>
                """


            else:

                badge_html = """
                <span class="status-badge status-pendente">
                    Pronto para análise
                </span>
                """


            # =================================================
            # EXPANDER
            # =================================================

            with st.expander(
                f"▸ {nome_cenario}",
                expanded=True
            ):


                # =============================================
                # CABEÇALHO
                # =============================================

                render_html(
                    f"""
                    <div class="scenario-container">

                        <div class="scenario-header">

                            <div class="scenario-title">
                                {nome_cenario_html}
                            </div>

                            {badge_html}

                        </div>

                    </div>
                    """
                )


                # =============================================
                # INFORMAÇÕES
                # =============================================

                responsavel_html = html.escape(
                    str(responsavel)
                )

                status_html = html.escape(
                    str(status)
                )


                render_html(
                    f"""
                    <div class="info-section">

                        <div class="info-grid">

                            <div class="info-item">

                                <div class="info-label">
                                    Responsável
                                </div>

                                <div class="info-value">
                                    {responsavel_html}
                                </div>

                            </div>


                            <div class="info-item">

                                <div class="info-label">
                                    Status
                                </div>

                                <div class="info-value">
                                    {status_html}
                                </div>

                            </div>

                        </div>

                    </div>
                    """
                )


                # =============================================
                # ANEXOS
                # =============================================

                if anexos:

                    titulo_anexos = (
                        "Anexo"
                        if len(anexos) == 1
                        else "Anexos"
                    )


                    render_html(
                        f"""
                        <div class="files-section">

                            <div class="files-label">
                                {titulo_anexos} ({len(anexos)})
                            </div>

                            <div class="files-message">
                                Baixe os documentos abaixo para
                                revisar antes de registrar sua análise.
                            </div>

                        </div>
                        """
                    )


                    for idx, arquivo in enumerate(anexos):

                        nome_arquivo_html = html.escape(
                            arquivo["nome"]
                        )


                        conteudo = baixar_arquivo_notion(
                            arquivo["url"]
                        )


                        # IMPORTANTE:
                        # Não usar vertical_alignment.
                        # Compatível com versões antigas
                        # do Streamlit.

                        col_nome, col_btn = st.columns(
                            [5, 1]
                        )


                        with col_nome:

                            render_html(
                                f"""
                                <div class="file-row">

                                    <div class="file-name">
                                        📄 {nome_arquivo_html}
                                    </div>

                                </div>
                                """
                            )


                        with col_btn:

                            if conteudo:

                                st.download_button(
                                    label="Baixar",
                                    data=conteudo,
                                    file_name=arquivo["nome"],
                                    mime="application/octet-stream",
                                    key=(
                                        f"download_"
                                        f"{cenario['id']}_"
                                        f"{idx}"
                                    ),
                                    type="secondary",
                                    use_container_width=True
                                )


                            else:

                                url_segura = html.escape(
                                    arquivo["url"],
                                    quote=True
                                )


                                render_html(
                                    f"""
                                    <a
                                        href="{url_segura}"
                                        target="_blank"
                                        style="
                                            display:block;
                                            text-align:center;
                                            background:#ffffff;
                                            color:#075da8;
                                            padding:0.45rem 0.4rem;
                                            border-radius:8px;
                                            text-decoration:none;
                                            font-weight:700;
                                            border:1px solid #b9d7ef;
                                            margin-top:0.45rem;
                                        "
                                    >
                                        Abrir
                                    </a>
                                    """
                                )


                else:

                    st.info(
                        "Nenhum anexo disponível para este cenário."
                    )


                # =============================================
                # DIVISOR
                # =============================================

                render_html(
                    """
                    <div class="section-divider"></div>
                    """
                )


                # =============================================
                # FORMULÁRIO
                # =============================================

                render_html(
                    """
                    <div class="form-section">

                        <div class="form-title">
                            Registrar análise
                        </div>

                        <div class="form-message">
                            Preencha os campos abaixo para registrar
                            a análise deste setor. Cada setor pode
                            analisar este cenário apenas uma vez.
                        </div>

                    </div>
                    """
                )


                # =============================================
                # FORM
                # =============================================

                with st.form(
                    key=f"form_analise_{cenario['id']}"
                ):


                    col_f1, col_f2 = st.columns(
                        2
                    )


                    with col_f1:

                        nome_input = st.text_input(
                            "Analista responsável",
                            placeholder="Ex.: João Silva"
                        )


                        setor_input = st.selectbox(
                            "Setor",
                            options=[
                                ""
                            ] + opcoes_setor,

                            format_func=lambda x:
                                "Selecione o setor"
                                if x == ""
                                else x
                        )


                    with col_f2:

                        status_input = st.selectbox(
                            "Resultado da análise",

                            options=[
                                ""
                            ] + opcoes_status,

                            format_func=lambda x:
                                "Selecione o resultado"
                                if x == ""
                                else x
                        )


                        motivo_input = st.text_area(
                            "Motivo",
                            placeholder=(
                                "Informe o motivo caso a análise "
                                "seja reprovada."
                            )
                        )


                    submit = st.form_submit_button(
                        "Salvar análise",
                        type="primary",
                        use_container_width=True
                    )


                    # ==========================================
                    # PROCESSAMENTO
                    # ==========================================

                    if submit:


                        # --------------------------------------
                        # NOME
                        # --------------------------------------

                        if not nome_input.strip():

                            st.error(
                                "Informe o nome do analista."
                            )


                        # --------------------------------------
                        # SETOR
                        # --------------------------------------

                        elif not setor_input:

                            st.error(
                                "Selecione o setor responsável."
                            )


                        # --------------------------------------
                        # STATUS
                        # --------------------------------------

                        elif not status_input:

                            st.error(
                                "Selecione o resultado da análise."
                            )


                        # --------------------------------------
                        # MOTIVO
                        # --------------------------------------

                        elif (
                            status_input.strip().lower()
                            == "reprovado"
                            and
                            not motivo_input.strip()
                        ):

                            st.error(
                                "Informe o motivo da reprovação."
                            )


                        # --------------------------------------
                        # SALVAR
                        # --------------------------------------

                        else:

                            try:

                                # =================================
                                # VERIFICAR DUPLICIDADE
                                # =================================

                                analises_existentes = (
                                    notion.databases.query(
                                        database_id=id_analises,

                                        filter={
                                            "property":
                                                col_relation,

                                            "relation": {
                                                "contains":
                                                    cenario["id"]
                                            }
                                        }
                                    )
                                )


                                setor_ja_analisou = False


                                for analise_existente in (
                                    analises_existentes.get(
                                        "results",
                                        []
                                    )
                                ):

                                    a_props = (
                                        analise_existente.get(
                                            "properties",
                                            {}
                                        )
                                    )


                                    setor_existente = (
                                        get_status_safe(
                                            a_props,
                                            colunas_reais.get(
                                                "setor"
                                            )
                                        )
                                    )


                                    if (
                                        setor_existente.strip().lower()
                                        ==
                                        setor_input.strip().lower()
                                    ):

                                        setor_ja_analisou = True

                                        break


                                if setor_ja_analisou:

                                    st.error(
                                        f"O setor "
                                        f"'{setor_input}' "
                                        f"já realizou uma análise "
                                        f"deste cenário."
                                    )


                                else:

                                    # =================================
                                    # DATA
                                    # =================================

                                    data_hoje = (
                                        datetime.now()
                                        .strftime(
                                            "%Y-%m-%d"
                                        )
                                    )


                                    propriedades = {}


                                    # =================================
                                    # TÍTULO
                                    # =================================

                                    if coluna_titulo_analise:

                                        propriedades[
                                            coluna_titulo_analise
                                        ] = {

                                            "title": [

                                                {

                                                    "text": {

                                                        "content":
                                                            nome_input.strip()

                                                    }

                                                }

                                            ]

                                        }


                                    # =================================
                                    # SETOR
                                    # =================================

                                    if colunas_reais.get(
                                        "setor"
                                    ):

                                        propriedades[
                                            colunas_reais["setor"]
                                        ] = (
                                            criar_propriedade_opcao(
                                                tipo_setor,
                                                setor_input
                                            )
                                        )


                                    # =================================
                                    # STATUS
                                    # =================================

                                    if colunas_reais.get(
                                        "status"
                                    ):

                                        propriedades[
                                            colunas_reais["status"]
                                        ] = (
                                            criar_propriedade_opcao(
                                                tipo_status,
                                                status_input
                                            )
                                        )


                                    # =================================
                                    # MOTIVO
                                    # =================================

                                    if colunas_reais.get(
                                        "motivo"
                                    ):

                                        if motivo_input.strip():

                                            propriedades[
                                                colunas_reais["motivo"]
                                            ] = {

                                                "rich_text": [

                                                    {

                                                        "text": {

                                                            "content":
                                                                motivo_input.strip()

                                                        }

                                                    }

                                                ]

                                            }

                                        else:

                                            propriedades[
                                                colunas_reais["motivo"]
                                            ] = {

                                                "rich_text": []

                                            }


                                    # =================================
                                    # DATA
                                    # =================================

                                    if colunas_reais.get(
                                        "data"
                                    ):

                                        propriedades[
                                            colunas_reais["data"]
                                        ] = {

                                            "date": {

                                                "start":
                                                    data_hoje

                                            }

                                        }


                                    # =================================
                                    # RELAÇÃO COM CENÁRIO
                                    # =================================

                                    propriedades[
                                        col_relation
                                    ] = {

                                        "relation": [

                                            {

                                                "id":
                                                    cenario["id"]

                                            }

                                        ]

                                    }


                                    # =================================
                                    # CRIAR PÁGINA NO NOTION
                                    # =================================

                                    notion.pages.create(

                                        parent={

                                            "database_id":
                                                id_analises

                                        },

                                        properties=propriedades

                                    )


                                    # =================================
                                    # SUCESSO
                                    # =================================

                                    st.success(
                                        f"Análise de "
                                        f"'{nome_input.strip()}' "
                                        f"registrada com sucesso!"
                                    )


                                    st.rerun()


                            except Exception as e:

                                st.error(
                                    "Não foi possível salvar a análise."
                                )

                                st.caption(
                                    f"Detalhes técnicos: {e}"
                                )


# ============================================================
# SEM PROJETO
# ============================================================

else:

    render_html(
        """
        <div class="page-header">

            <div class="page-title">
                Compliance Tributário
            </div>

            <div class="page-subtitle">
                Selecione um projeto para começar
            </div>

        </div>
        """
    )
