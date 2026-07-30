import streamlit as st
from notion_client import Client
from datetime import datetime

# --- CONFIGURAÇÕES ---
NOTION_TOKEN = "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"

st.set_page_config(page_title="Compliance Tributário", page_icon="️", layout="wide")

# --- CSS PERSONALIZADO (Visual Colorido) ---
st.markdown("""
<style>
    /* Fundo com cor suave */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        padding: 2rem;
    }
    
    /* Cabeçalho */
    .header {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        text-align: center;
    }
    .header h1 {
        color: #1e3a8a;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    .header p {
        color: #6b7280;
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
    }
    
    /* Cards de cenário */
    .scenario-card {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        border-left: 6px solid #f97316;
    }
    
    .scenario-card-aprovado {
        border-left-color: #10b981;
    }
    
    .scenario-card-reprovado {
        border-left-color: #ef4444;
    }
    
    /* Título do cenário */
    .scenario-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 1rem;
    }
    
    /* Badge de status */
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: 700;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .status-aprovado {
        background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
        color: white;
        box-shadow: 0 4px 10px rgba(16, 185, 129, 0.3);
    }
    .status-reprovado {
        background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
        color: white;
        box-shadow: 0 4px 10px rgba(239, 68, 68, 0.3);
    }
    .status-pendente {
        background: linear-gradient(135deg, #f97316 0%, #fb923c 100%);
        color: white;
        box-shadow: 0 4px 10px rgba(249, 115, 22, 0.3);
    }
    
    /* Seções */
    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1f2937;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #f97316;
    }
    
    /* Cards de análise */
    .analysis-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #f97316;
    }
    .analysis-card-aprovado {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border-left-color: #10b981;
    }
    .analysis-card-reprovado {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        border-left-color: #ef4444;
    }
    
    /* Botões */
    .stButton > button {
        border-radius: 10px;
        font-weight: 700;
        font-size: 1rem;
        padding: 0.75rem 2rem;
        transition: all 0.3s ease;
        border: none;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #f97316 0%, #fb923c 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(249, 115, 22, 0.4);
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(249, 115, 22, 0.5);
    }
    
    /* Formulário */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        border-radius: 8px;
        border: 2px solid #e5e7eb;
        background: white;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #f97316;
        box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.1);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a8a 0%, #3730a3 100%);
        color: white;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    [data-testid="stSidebar"] .stSelectbox label {
        color: white !important;
        font-weight: 600;
    }
    
    /* Expander */
    .stExpander {
        border: none;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        overflow: hidden;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    }
    
    /* Botões de decisão final */
    .decision-buttons {
        display: flex;
        gap: 1rem;
        margin-top: 2rem;
    }
    
    /* Responsável e arquivos */
    .info-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 1.5rem;
        margin-bottom: 1.5rem;
        padding: 1.5rem;
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-radius: 10px;
    }
    
    /* Links de arquivo */
    .file-link {
        display: inline-block;
        background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        text-decoration: none;
        margin: 0.25rem;
        font-weight: 600;
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
    if coluna_nome and coluna_nome in props:
        col = props[coluna_nome]
        if col and isinstance(col, dict):
            select = col.get("select")
            if select and isinstance(select, dict):
                return select.get("name", "Desconhecido")
    return "Desconhecido"

def get_titulo_safe(props, nomes_possiveis):
    for nome in nomes_possiveis:
        if nome in props:
            col = props[nome]
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
    st.markdown("### 🏛️ Compliance")
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
            
            st.markdown("**📁 Projetos**")
            projeto_escolhido = st.selectbox(
                "Selecione o projeto:",
                options=lista_projetos,
                format_func=lambda x: x["nome"],
                label_visibility="collapsed"
            )
            
            if projeto_escolhido:
                st.markdown("---")
                st.success(f"✅ **{projeto_escolhido['nome']}**")
        else:
            st.warning("Nenhum projeto encontrado.")
    except Exception as e:
        st.error(f"Erro: {e}")

# --- ÁREA PRINCIPAL ---
if 'projeto_escolhido' in dir() and projeto_escolhido:
    st.markdown(f"""
    <div class="header">
        <h1>🏛️ {projeto_escolhido['nome']}</h1>
        <p>Sistema de Aprovação - Compliance Tributário</p>
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
            st.info("📭 Nenhum cenário encontrado para este projeto.")
        else:
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
            st.markdown("## 📋 Cenários")
            
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
                
                # Classe do card baseada no status
                card_class = "scenario-card"
                if status == "Aprovado":
                    card_class += " scenario-card-aprovado"
                    status_html = '<span class="status-badge status-aprovado">✅ APROVADO</span>'
                elif status == "Reprovado":
                    card_class += " scenario-card-reprovado"
                    status_html = '<span class="status-badge status-reprovado">❌ REPROVADO</span>'
                else:
                    status_html = '<span class="status-badge status-pendente"> PRONTO PARA ANÁLISE</span>'
                
                with st.expander(f"📄 {nome_cenario}", expanded=False):
                    # Informações do cenário
                    st.markdown(f"""
                    <div class="{card_class}">
                        <div class="scenario-title">{nome_cenario}</div>
                        <div style="margin-bottom: 1.5rem;">{status_html}</div>
                        
                        <div class="info-grid">
                            <div>
                                <strong>👤 Responsável:</strong><br>
                                {responsavel}
                            </div>
                            <div>
                                <strong>📊 Status:</strong><br>
                                {status}
                            </div>
                            <div>
                                <strong> Arquivos:</strong><br>
                                {''.join([f'<a href="{a["url"]}" target="_blank" class="file-link">📥 {a["nome"]}</a>' for a in anexos]) if anexos else 'Nenhum arquivo'}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # --- FORMULÁRIO PARA NOVA ANÁLISE ---
                    st.markdown("### 📝 Registrar Nova Análise")
                    
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
                                placeholder="Explique o motivo da reprovação..."
                            )
                        
                        submit = st.form_submit_button("💾 Salvar Análise", type="primary", use_container_width=True)
                        
                        if submit:
                            if not nome_input:
                                st.error("❌ Preencha o nome da análise.")
                            elif not analista_input:
                                st.error("❌ Preencha o nome do analista.")
                            elif status_input == "Reprovado" and not motivo_input:
                                st.error("❌ Informe o motivo da reprovação.")
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
                                    st.success(f"✅ Análise '{nome_input}' salva com sucesso!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Erro ao salvar: {e}")
                    
                    st.markdown("---")
                    
                    # --- BOTÕES DE DECISÃO FINAL ---
                    if status == "Pronto para Análise":
                        st.markdown("### ✅ Decisão Final do Cenário")
                        st.markdown("Aprove ou reprova este cenário de forma definitiva")
                        
                        col_ap, col_rp = st.columns(2)
                        with col_ap:
                            if st.button("✅ APROVAR CENÁRIO", type="primary", use_container_width=True, key=f"ap_{cenario['id']}"):
                                notion.pages.update(
                                    page_id=cenario["id"],
                                    properties={"Status": {"select": {"name": "Aprovado"}}}
                                )
                                st.balloons()
                                st.success("🎉 Cenário Aprovado com sucesso!")
                                st.rerun()
                        with col_rp:
                            if st.button("❌ REPROVAR CENÁRIO", type="secondary", use_container_width=True, key=f"rp_{cenario['id']}"):
                                notion.pages.update(
                                    page_id=cenario["id"],
                                    properties={"Status": {"select": {"name": "Reprovado"}}}
                                )
                                st.error("Cenário Reprovado!")
                                st.rerun()
    
    except Exception as e:
        st.error(f"❌ Erro: {e}")
