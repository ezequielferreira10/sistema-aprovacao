import streamlit as st
from notion_client import Client
from datetime import datetime

# --- CONFIGURAÇÕES ---
NOTION_TOKEN = "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"

st.set_page_config(page_title="Compliance Tributário", page_icon="🏛️", layout="wide")

# --- CSS PERSONALIZADO (Visual Premium Minimalista) ---
st.markdown("""
<style>
    /* Reset e base */
    * {
        box-sizing: border-box;
    }
    
    body {
        background-color: #FFFFFF;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        color: #1F2937;
        font-size: 14px;
        line-height: 1.6;
    }
    
    /* Esconder elementos padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sidebar estilo app premium */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E5E7EB;
        padding: 2rem 1rem;
    }
    
    [data-testid="stSidebar"] .stSelectbox label {
        font-size: 12px;
        font-weight: 600;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    /* Main content */
    .main {
        background-color: #FFFFFF;
        padding: 2rem 3rem;
    }
    
    /* Cabeçalho */
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
    
    /* Cards */
    .card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
    }
    
    .card:hover {
        border-color: #F97316;
    }
    
    /* Status badges */
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
    
    /* Cards de análise */
    .analise-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-left: 3px solid #F97316;
        border-radius: 6px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    
    .analise-card-aprovado {
        border-left-color: #10B981;
    }
    
    .analise-card-reprovado {
        border-left-color: #EF4444;
    }
    
    /* Botões */
    .stButton > button {
        border-radius: 6px;
        font-weight: 500;
        font-size: 0.875rem;
        padding: 0.625rem 1.25rem;
        transition: all 0.2s ease;
    }
    
    .stButton > button[kind="primary"] {
        background-color: #F97316;
        color: #FFFFFF;
        border: 1px solid #F97316;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #EA580C;
        border-color: #EA580C;
    }
    
    .stButton > button[kind="secondary"] {
        background-color: #FFFFFF;
        color: #1F2937;
        border: 1px solid #E5E7EB;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background-color: #F9FAFB;
        border-color: #D1D5DB;
    }
    
    /* Formulários */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        border-radius: 6px;
        border: 1px solid #E5E7EB;
        font-size: 0.875rem;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #F97316;
        box-shadow: 0 0 0 2px rgba(249, 115, 22, 0.1);
    }
    
    /* Títulos de seção */
    .section-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1F2937;
        margin-bottom: 1rem;
        letter-spacing: -0.3px;
    }
    
    /* Métricas */
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
    
    /* Expander customizado */
    .stExpander {
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .stExpander:hover {
        border-color: #D1D5DB;
    }
    
    /* Divisores */
    hr {
        border: none;
        border-top: 1px solid #E5E7EB;
        margin: 1.5rem 0;
    }
    
    /* Labels */
    label {
        font-size: 0.875rem;
        font-weight: 500;
        color: #374151;
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

def get_badge_class(status):
    if status == "Aprovado":
        return "badge badge-aprovado"
    elif status == "Reprovado":
        return "badge badge-reprovado"
    else:
        return "badge badge-pendente"

def get_analise_card_class(status):
    if status == "Aprovado":
        return "analise-card analise-card-aprovado"
    elif status == "Reprovado":
        return "analise-card analise-card-reprovado"
    else:
        return "analise-card"

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
                props = proj["properties"]
                nome_proj = "Sem nome"
                for col in ["Projeto", "Nome", "Name"]:
                    if col in props:
                        titulos = props[col].get("title", [])
                        if titulos:
                            nome_proj = titulos[0].get("plain_text", "Sem nome")
                            break
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
        st.error(f"Erro: {e}")

# --- ÁREA PRINCIPAL ---
if 'projeto_escolhido' in dir() and projeto_escolhido:
    # Cabeçalho
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
            # Métricas
            total_cenarios = len(cenarios)
            aprovados = sum(1 for c in cenarios if c["properties"].get("Status", {}).get("select", {}).get("name") == "Aprovado")
            reprovados = sum(1 for c in cenarios if c["properties"].get("Status", {}).get("select", {}).get("name") == "Reprovado")
            pendentes = total_cenarios - aprovados - reprovados
            
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
                props = cenario["properties"]
                
                nome_cenario = "Sem nome"
                for col in ["Cenário", "Cenario", "Nome", "Name"]:
                    if col in props:
                        titulos = props[col].get("title", [])
                        if titulos:
                            nome_cenario = titulos[0].get("plain_text", "Sem nome")
                            break
                
                status = "Desconhecido"
                if "Status" in props and props["Status"].get("select"):
                    status = props["Status"]["select"].get("name", "Desconhecido")
                
                responsavel = "Não definido"
                if "Responsável" in props and props["Responsável"].get("people"):
                    responsavel = props["Responsável"]["people"][0].get("name", "Não definido")
                
                anexos = []
                if "Anexos" in props:
                    arquivos = props["Anexos"].get("files", [])
                    for arquivo in arquivos:
                        if arquivo.get("external", {}).get("url"):
                            anexos.append({"nome": arquivo.get("name", "Arquivo"), "url": arquivo["external"]["url"]})
                        elif arquivo.get("file", {}).get("url"):
                            anexos.append({"nome": arquivo.get("name", "Arquivo"), "url": arquivo["file"]["url"]})
                
                with st.expander(f"{nome_cenario}", expanded=False):
                    # Info do cenário
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"**Responsável**")
                        st.markdown(responsavel)
                    with col2:
                        st.markdown("**Status**")
                        st.markdown(f'<span class="{get_badge_class(status)}">{status}</span>', unsafe_allow_html=True)
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
                    
                    analises_response = notion.databases.query(
                        database_id=id_analises,
                        filter={
                            "property": col_relation,
                            "relation": {"contains": cenario["id"]}
                        }
                    )
                    analises = analises_response.get("results", [])
                    
                    if analises:
                        for analise in analises:
                            a_props = analise["properties"]
                            
                            nome_analise = "Sem nome"
                            if colunas_reais.get("nome_analise") and colunas_reais["nome_analise"] in a_props:
                                titulos = a_props[colunas_reais["nome_analise"]].get("title", [])
                                if titulos:
                                    nome_analise = titulos[0].get("plain_text", "Sem nome")
                            
                            setor = "Não definido"
                            if colunas_reais.get("setor") and colunas_reais["setor"] in a_props and a_props[colunas_reais["setor"]].get("select"):
                                setor = a_props[colunas_reais["setor"]]["select"].get("name", "Não definido")
                            
                            analista = "Não definido"
                            if colunas_reais.get("analista") and colunas_reais["analista"] in a_props:
                                if a_props[colunas_reais["analista"]].get("people"):
                                    analista = a_props[colunas_reais["analista"]]["people"][0].get("name", "Não definido")
                                elif a_props[colunas_reais["analista"]].get("rich_text"):
                                    textos = a_props[colunas_reais["analista"]]["rich_text"]
                                    if textos:
                                        analista = textos[0].get("plain_text", "Não definido")
                            
                            status_analise = "Não definido"
                            if colunas_reais.get("status") and colunas_reais["status"] in a_props and a_props[colunas_reais["status"]].get("select"):
                                status_analise = a_props[colunas_reais["status"]]["select"].get("name", "Não definido")
                            
                            motivo = ""
                            if colunas_reais.get("motivo") and colunas_reais["motivo"] in a_props and a_props[colunas_reais["motivo"]].get("rich_text"):
                                textos = a_props[colunas_reais["motivo"]]["rich_text"]
                                if textos:
                                    motivo = textos[0].get("plain_text", "")
                            
                            data_analise = ""
                            if colunas_reais.get("data") and colunas_reais["data"] in a_props and a_props[colunas_reais["data"]].get("date"):
                                data_analise = a_props[colunas_reais["data"]]["date"].get("start", "")
                            
                            st.markdown(f"""
                            <div class="{get_analise_card_class(status_analise)}">
                                <div style="display: flex; justify-content: space-between; align-items: start;">
                                    <div>
                                        <strong>{nome_analise}</strong><br>
                                        <span style="color: #6B7280; font-size: 0.875rem;">
                                            Setor: {setor} | Analista: {analista}<br>
                                            {f'Motivo: {motivo}<br>' if motivo else ''}
                                            {f'Data: {data_analise}' if data_analise else ''}
                                        </span>
                                    </div>
                                    <span class="{get_badge_class(status_analise)}">{status_analise}</span>
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
