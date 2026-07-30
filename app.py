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
        background-color: #f1f5f9;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a8a 0%, #1e40af 100%);
        padding: 2rem 1.5rem;
    }
    [data-testid="stSidebar"] * { color: white !important; }
    [data-testid="stSidebar"] .stSelectbox > div > div > div {
        background-color: white !important;
        color: #1f2937 !important;
    }
    [data-testid="stSidebar"] .stSelectbox > div > div > div > div {
        color: #1f2937 !important;
    }
    
    .main {
        background-color: #f1f5f9;
        padding: 2rem 3rem;
    }
    
    .header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 3rem 2rem;
        border-radius: 16px;
        margin-bottom: 2.5rem;
        text-align: center;
        box-shadow: 0 20px 40px rgba(30, 58, 138, 0.2);
    }
    .header h1 {
        color: white;
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -1px;
    }
    .header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.2rem;
        margin: 0.75rem 0 0 0;
        font-weight: 500;
    }
    
    .scenario-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        border-left: 6px solid #f97316;
    }
    .scenario-card-aprovado { border-left-color: #10b981; }
    .scenario-card-reprovado { border-left-color: #ef4444; }
    
    .scenario-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 1rem;
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1.25rem;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .status-aprovado { background: #10b981; color: white; }
    .status-reprovado { background: #ef4444; color: white; }
    .status-pendente { background: #f97316; color: white; }
    
    .info-box {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        font-size: 1.05rem;
        border: 1px solid #e2e8f0;
    }
    
    .files-section {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        border: 2px solid #3b82f6;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.1);
    }
    .files-section h4 {
        color: #1e3a8a;
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
    }
    
    .file-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #f8fafc;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin-bottom: 0.75rem;
        border: 1px solid #e2e8f0;
        transition: all 0.2s ease;
    }
    .file-row:hover {
        background: #f1f5f9;
        border-color: #3b82f6;
    }
    .file-name {
        font-weight: 600;
        color: #1f2937;
        font-size: 1rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .stButton > button {
        border-radius: 10px;
        font-weight: 700;
        font-size: 1rem;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
    }
    .stButton > button[kind="primary"] {
        background: #10b981;
        color: white;
        border: none;
    }
    .stButton > button[kind="primary"]:hover { background: #059669; }
    .stButton > button[kind="secondary"] {
        background: #ef4444;
        color: white;
        border: none;
    }
    .stButton > button[kind="secondary"]:hover { background: #dc2626; }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        border-radius: 8px;
        border: 2px solid #e5e7eb;
        background: white;
        font-size: 1rem;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    .stExpander {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        background: white;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    label {
        font-size: 1rem;
        font-weight: 600;
        color: #374151;
    }
    
    h3, h4 {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1f2937;
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

def baixar_arquivo(url):
    """Baixa o arquivo e retorna o conteúdo em bytes"""
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return response.read()
    except Exception as e:
        st.error(f"Erro ao baixar arquivo: {e}")
        return None

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
    st.markdown("### 🏛️ Compliance Tributário")
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
        <h1>🏛️ Compliance Tributário</h1>
        <p>Projeto: {projeto_escolhido['nome']}</p>
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
            db_info = notion.databases.retrieve(database_id=id_analises)
            todas_props = db_info.get("properties", {})
            
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
            
            st.markdown("## 📋 Cenários")
            
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
                
                card_class = "scenario-card"
                if status == "Aprovado":
                    card_class += " scenario-card-aprovado"
                elif status == "Reprovado":
                    card_class += " scenario-card-reprovado"
                
                with st.expander(f"📄 {nome_cenario}", expanded=False):
                    st.markdown(f"""
                    <div class="{card_class}">
                        <div class="scenario-title">{nome_cenario}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if status == "Aprovado":
                        st.markdown('<span class="status-badge status-aprovado">✅ APROVADO</span>', unsafe_allow_html=True)
                    elif status == "Reprovado":
                        st.markdown('<span class="status-badge status-reprovado">❌ REPROVADO</span>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span class="status-badge status-pendente">⏳ PRONTO PARA ANÁLISE</span>', unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    st.markdown(f"""
                    <div class="info-box">
                        <strong>👤 Responsável:</strong> {responsavel}<br><br>
                        <strong>📊 Status:</strong> {status}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # SEÇÃO DE ARQUIVOS COM DOWNLOAD FUNCIONAL
                    if anexos:
                        st.markdown(f"""
                        <div class="files-section">
                            <h4> Arquivos Disponíveis ({len(anexos)})</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        for idx, arquivo in enumerate(anexos):
                            # Baixa o arquivo
                            conteudo = baixar_arquivo(arquivo['url'])
                            
                            if conteudo:
                                # Layout: nome à esquerda, botão à direita
                                col_nome, col_btn = st.columns([4, 1])
                                
                                with col_nome:
                                    st.markdown(f"""
                                    <div class="file-row" style="margin-bottom: 0;">
                                        <div class="file-name">
                                            📄 {arquivo['nome']}
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                with col_btn:
                                    st.download_button(
                                        label="⬇️ Baixar",
                                        data=conteudo,
                                        file_name=arquivo['nome'],
                                        mime="application/octet-stream",
                                        key=f"download_{cenario['id']}_{idx}",
                                        type="primary",
                                        use_container_width=True
                                    )
                    else:
                        st.info(" Nenhum arquivo disponível")
                    
                    st.markdown("---")
                    
                    # FORMULÁRIO
                    st.markdown("### 📝 Registrar Nova Análise")
                    
                    with st.form(key=f"form_analise_{cenario['id']}"):
                        col_f1, col_f2 = st.columns(2)
                        
                        with col_f1:
                            nome_input = st.text_input("Analista Responsável", placeholder="Ex: João Silva")
                            setor_input = st.selectbox(
                                "Setor",
                                options=["Contabilidade", "Apuração", "Fiscal", "Jurídico", "Auditoria"]
                            )
                        
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
                                st.error("❌ Preencha o nome do analista.")
                            elif status_input == "Reprovado" and not motivo_input:
                                st.error("❌ Informe o motivo da reprovação.")
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
                                    st.success(f"✅ Análise de '{nome_input}' salva com sucesso!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Erro ao salvar: {e}")
                    
                    st.markdown("---")
                    
                    # BOTÕES DE DECISÃO FINAL
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
