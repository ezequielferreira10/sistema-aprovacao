import streamlit as st
from notion_client import Client
from datetime import datetime

# --- CONFIGURAÇÕES ---
NOTION_TOKEN = "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"


st.set_page_config(page_title="Compliance Tributário", page_icon="🏛️", layout="wide")

# --- CSS PERSONALIZADO ---
st.markdown("""
<style>
    * { box-sizing: border-box; }
    body {
        background-color: #FFFFFF;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #1F2937;
        font-size: 14px;
    }
    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E5E7EB;
        padding: 2rem 1rem;
    }
    .main { background-color: #FFFFFF; padding: 2rem 3rem; }
    
    .header {
        border-bottom: 1px solid #E5E7EB;
        padding-bottom: 1.5rem;
        margin-bottom: 2rem;
    }
    .header h1 {
        color: #1F2937;
        font-size: 2rem;
        font-weight: 600;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .header p {
        color: #6B7280;
        font-size: 0.9rem;
        margin: 0.5rem 0 0 0;
    }
    
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1F2937;
        margin: 0;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.5rem;
    }
    
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-aprovado {
        background-color: #F0FDF4;
        color: #166534;
        border: 1px solid #BBF7D0;
    }
    .badge-reprovado {
        background-color: #FEF2F2;
        color: #991B1B;
        border: 1px solid #FECACA;
    }
    .badge-pendente {
        background-color: #FFF7ED;
        color: #C2410C;
        border: 1px solid #FED7AA;
    }
    
    .analise-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-left: 3px solid #F97316;
        border-radius: 6px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    .analise-card-aprovado { border-left-color: #10B981; }
    .analise-card-reprovado { border-left-color: #EF4444; }
    
    .stButton > button {
        border-radius: 6px;
        font-weight: 500;
        font-size: 0.875rem;
        padding: 0.625rem 1.25rem;
    }
    .stButton > button[kind="primary"] {
        background-color: #F97316;
        color: #FFFFFF;
        border: 1px solid #F97316;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #EA580C;
    }
    .stButton > button[kind="secondary"] {
        background-color: #FFFFFF;
        color: #1F2937;
        border: 1px solid #E5E7EB;
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        border-radius: 6px;
        border: 1px solid #E5E7EB;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #F97316;
        box-shadow: 0 0 0 2px rgba(249, 115, 22, 0.1);
    }
    
    .stExpander {
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES AUXILIARES ---
def encontrar_tabela(nome_tabela):
    response = notion.search(
        query=nome_tabela,
        filter={"value": "database", "property": "object"}
    )
    resultados = response.get("results", [])
    if resultados:
        return resultados[0]["id"]
    return None

def encontrar_coluna(props, nomes_possiveis):
    for nome in nomes_possiveis:
        if nome in props:
            return nome
    return None

def get_status_safe(props, coluna_nome):
    """Busca o status de forma segura, sem dar erro se estiver vazio"""
    if coluna_nome and coluna_nome in props:
        col = props[coluna_nome]
        if col and isinstance(col, dict):
            select = col.get("select")
            if select and isinstance(select, dict):
                return select.get("name", "Desconhecido")
    return "Desconhecido"

def get_titulo_safe(props, nomes_possiveis):
    """Busca o título de forma segura"""
    for nome in nomes_possiveis:
        if nome in props:
            col = props[nome]
            if col and isinstance(col, dict):
                titulos = col.get("title", [])
                if titulos and len(titulos) > 0:
                    return titulos[0].get("plain_text", "Sem nome")
    return "Sem nome"

def get_texto_safe(props, coluna_nome):
    """Busca texto de forma segura"""
    if coluna_nome and coluna_nome in props:
        col = props[coluna_nome]
        if col and isinstance(col, dict):
            textos = col.get("rich_text", [])
            if textos and len(textos) > 0:
                return textos[0].get("plain_text", "")
    return ""

def get_people_safe(props, coluna_nome):
    """Busca pessoa de forma segura"""
    if coluna_nome and coluna_nome in props:
        col = props[coluna_nome]
        if col and isinstance(col, dict):
            pessoas = col.get("people", [])
            if pessoas and len(pessoas) > 0:
                return pessoas[0].get("name", "Não definido")
    return "Não definido"

# --- INICIALIZAÇÃO ---
notion = Client(auth=NOTION_TOKEN)

id_projetos = encontrar_tabela("Projetos")
id_cenarios = encontrar_tabela("Cenário")
id_analises = encontrar_tabela("Análises")

if not all([id_projetos, id_cenarios, id_analises]):
    st.error("Tabelas não encontradas no Notion.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### Compliance")
    st.markdown("---")
    
    try:
        projetos_response = notion.databases.query(database_id=id_projetos)
        projetos = projetos_response.get("results", [])
        
        if projetos:
            lista_projetos = []
            for proj in projetos:
                props = proj.get("properties", {})
                nome_proj = get_titulo_safe(props, ["Projeto", "Nome", "Name"])
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
                st.markdown(f"**{projeto_escolhido['nome']}**")
        else:
            st.warning("Nenhum projeto encontrado.")
    except Exception as e:
        st.error(f"Erro ao carregar projetos: {e}")

# --- ÁREA PRINCIPAL ---
if 'projeto_escolhido' in dir() and projeto_escolhido:
    st.markdown(f"""
    <div class="header">
        <h1>{projeto_escolhido['nome']}</h1>
        <p>Gestão de cenários e análises de compliance tributário</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        cenarios_response = notion.databases.query(
            database_id=id_cenarios,
            filter={
                "property": "Projeto",
                "relation": {"contains": projeto_escolhido["id"]}
            }
        )
        cenarios = cenarios_response.get("results", [])
        
        if not cenarios:
            st.info("Nenhum cenário encontrado para este projeto.")
        else:
            # Métricas (agora com proteção contra None)
            total_cenarios = len(cenarios)
            aprovados = 0
            reprovados = 0
            pendentes = 0
            
            for c in cenarios:
                props = c.get("properties", {})
                status = get_status_safe(props, "Status")
                if status == "Aprovado":
                    aprovados += 1
                elif status == "Reprovado":
                    reprovados += 1
                else:
                    pendentes += 1
            
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            with col_m1:
                st.markdown(f"""
                <div class="metric-card">
                    <p class="metric-value">{total_cenarios}</p>
                    <p class="metric-label">Total de Cenários</p>
                </div>
                """, unsafe_allow_html=True)
            with col_m2:
                st.markdown(f"""
                <div class="metric-card">
                    <p class="metric-value">{aprovados}</p>
                    <p class="metric-label">Aprovados</p>
                </div>
                """, unsafe_allow_html=True)
            with col_m3:
                st.markdown(f"""
                <div class="metric-card">
                    <p class="metric-value">{reprovados}</p>
                    <p class="metric-label">Reprovados</p>
                </div>
                """, unsafe_allow_html=True)
            with col_m4:
                st.markdown(f"""
                <div class="metric-card">
                    <p class="metric-value">{pendentes}</p>
                    <p class="metric-label">Pendentes</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Descobrir colunas da tabela Análises
            db_info = notion.databases.retrieve(database_id=id_analises)
            todas_props = db_info.get("properties", {})
            
            nomes_colunas = {
                "nome_analise": ["Nome da Análise", "Nome da Analise", "Nome", "Name"],
                "setor": ["Setor", "Área", "Area", "Departamento"],
                "analista": ["Analista Responsável", "Analista Responsavel", "Analista", "Responsável"],
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
            
            # Lista de cenários
            st.markdown("### Cenários")
            
            for cenario in cenarios:
                props = cenario.get("properties", {})
                
                nome_cenario = get_titulo_safe(props, ["Cenário", "Cenario", "Nome", "Name"])
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
                
                # Badge de status
                if status == "Aprovado":
                    badge_html = '<span class="badge badge-aprovado">Aprovado</span>'
                elif status == "Reprovado":
                    badge_html = '<span class="badge badge-reprovado">Reprovado</span>'
                else:
                    badge_html = '<span class="badge badge-pendente">Pendente</span>'
                
                with st.expander(f"{nome_cenario}  {badge_html}", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown("**Responsável**")
                        st.markdown(responsavel)
                    with col2:
                        st.markdown("**Status**")
                        st.markdown(badge_html, unsafe_allow_html=True)
                    with col3:
                        st.markdown("**Arquivos**")
                        if anexos:
                            for arquivo in anexos:
                                st.link_button(arquivo['nome'], arquivo['url'])
                        else:
                            st.markdown("Nenhum arquivo")
                    
                    st.markdown("---")
                    
                    # Análises
                    st.markdown("#### Análises por Setor")
                    
                    try:
                        analises_response = notion.databases.query(
                            database_id=id_analises,
                            filter={
                                "property": col_relation,
                                "relation": {"contains": cenario["id"]}
                            }
                        )
                        analises = analises_response.get("results", [])
                    except:
                        analises = []
                    
                    if analises:
                        for analise in analises:
                            a_props = analise.get("properties", {})
                            
                            nome_analise = get_titulo_safe(a_props, [colunas_reais.get("nome_analise")] if colunas_reais.get("nome_analise") else [])
                            if nome_analise == "Sem nome":
                                nome_analise = "Análise sem nome"
                            
                            setor = get_status_safe(a_props, colunas_reais.get("setor"))
                            analista = get_texto_safe(a_props, colunas_reais.get("analista"))
                            if not analista:
                                analista = get_people_safe(a_props, colunas_reais.get("analista"))
                            if not analista:
                                analista = "Não definido"
                            
                            status_analise = get_status_safe(a_props, colunas_reais.get("status"))
                            motivo = get_texto_safe(a_props, colunas_reais.get("motivo"))
                            
                            data_analise = ""
                            col_data = colunas_reais.get("data")
                            if col_data and col_data in a_props:
                                col = a_props[col_data]
                                if col and isinstance(col, dict):
                                    date_info = col.get("date")
                                    if date_info and isinstance(date_info, dict):
                                        data_analise = date_info.get("start", "")
                            
                            # Card da análise
                            if status_analise == "Aprovado":
                                card_class = "analise-card analise-card-aprovado"
                                badge_analise = '<span class="badge badge-aprovado">Aprovado</span>'
                            elif status_analise == "Reprovado":
                                card_class = "analise-card analise-card-reprovado"
                                badge_analise = '<span class="badge badge-reprovado">Reprovado</span>'
                            else:
                                card_class = "analise-card"
                                badge_analise = '<span class="badge badge-pendente">Em Análise</span>'
                            
                            st.markdown(f"""
                            <div class="{card_class}">
                                <div style="display: flex; justify-content: space-between; align-items: start;">
                                    <div>
                                        <strong>{nome_analise}</strong><br>
                                        <span style="color: #6B7280; font-size: 0.875rem;">
                                            Setor: {setor} | Analista: {analista}<br>
                                            {f'Motivo: {motivo}<br>' if motivo else ''}
                                            {f'Data: {data_analise}' if data_analise else ''}
                                        </span>
                                    </div>
                                    <div>{badge_analise}</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("Nenhuma análise registrada ainda.")
                    
                    st.markdown("---")
                    
                    # Formulário
                    st.markdown("#### Registrar Nova Análise")
                    
                    with st.form(key=f"form_analise_{cenario['id']}"):
                        col_f1, col_f2 = st.columns(2)
                        
                        with col_f1:
                            nome_input = st.text_input("Nome da Análise", placeholder="Ex: Análise Contábil")
                            setor_input = st.selectbox(
                                "Setor",
                                options=["Contabilidade", "Apuração", "Fiscal", "Jurídico", "Auditoria"]
                            )
                            analista_input = st.text_input("Nome do Analista", placeholder="Ex: João Silva")
                        
                        with col_f2:
                            status_input = st.selectbox(
                                "Status",
                                options=["Aprovado", "Reprovado", "Em Análise"]
                            )
                            motivo_input = st.text_area(
                                "Motivo (obrigatório se reprovado)",
                                placeholder="Explique o motivo..."
                            )
                        
                        submit = st.form_submit_button("Salvar Análise", type="primary")
                        
                        if submit:
                            if not nome_input:
                                st.error("Preencha o nome da análise.")
                            elif not analista_input:
                                st.error("Preencha o nome do analista.")
                            elif status_input == "Reprovado" and not motivo_input:
                                st.error("Informe o motivo da reprovação.")
                            else:
                                try:
                                    data_hoje = datetime.now().strftime("%Y-%m-%d")
                                    
                                    propriedades = {}
                                    if colunas_reais.get("nome_analise"):
                                        propriedades[colunas_reais["nome_analise"]] = {"title": [{"text": {"content": nome_input}}]}
                                    if colunas_reais.get("setor"):
                                        propriedades[colunas_reais["setor"]] = {"select": {"name": setor_input}}
                                    if colunas_reais.get("analista"):
                                        propriedades[colunas_reais["analista"]] = {"rich_text": [{"text": {"content": analista_input}}]}
                                    if colunas_reais.get("status"):
                                        propriedades[colunas_reais["status"]] = {"select": {"name": status_input}}
                                    if colunas_reais.get("motivo"):
                                        propriedades[colunas_reais["motivo"]] = {"rich_text": [{"text": {"content": motivo_input}}] if motivo_input else []}
                                    if colunas_reais.get("data"):
                                        propriedades[colunas_reais["data"]] = {"date": {"start": data_hoje}}
                                    if col_relation:
                                        propriedades[col_relation] = {"relation": [{"id": cenario["id"]}]}
                                    
                                    notion.pages.create(parent={"database_id": id_analises}, properties=propriedades)
                                    st.success(f"Análise '{nome_input}' salva com sucesso!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro ao salvar: {e}")
                    
                    st.markdown("---")
                    
                    # Botões finais
                    if status == "Pronto para Análise":
                        st.markdown("#### Decisão Final")
                        col_ap, col_rp = st.columns(2)
                        with col_ap:
                            if st.button("Aprovar Cenário", type="primary", use_container_width=True, key=f"ap_{cenario['id']}"):
                                notion.pages.update(page_id=cenario["id"], properties={"Status": {"select": {"name": "Aprovado"}}})
                                st.success("Cenário Aprovado!")
                                st.rerun()
                        with col_rp:
                            if st.button("Reprovar Cenário", type="secondary", use_container_width=True, key=f"rp_{cenario['id']}"):
                                notion.pages.update(page_id=cenario["id"], properties={"Status": {"select": {"name": "Reprovado"}}})
                                st.error("Cenário Reprovado!")
                                st.rerun()
    
    except Exception as e:
        st.error(f"Erro: {e}")
