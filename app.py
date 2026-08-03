import streamlit as st
from notion_client import Client
from datetime import datetime
import urllib.request
import ssl

NOTION_TOKEN = "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"

st.set_page_config(page_title="Compliance Tributário", page_icon="🏛️", layout="wide")

# --- CSS PERSONALIZADO (Divisão Visual Clara) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * { box-sizing: border-box; }
    
    body {
        background-color: #f1f5f9;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 14px;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0A5AA5 0%, #084a8a 100%);
        padding: 2rem 1.5rem;
    }
    [data-testid="stSidebar"] * { color: white !important; }
    [data-testid="stSidebar"] .stSelectbox > div > div > div {
        background-color: white !important;
    }
    [data-testid="stSidebar"] .stSelectbox > div > div > div > div {
        color: #000000 !important;
    }
    
    /* Main */
    .main {
        background-color: #f1f5f9;
        padding: 2rem 3rem;
    }
    
    /* Header */
    .header {
        background: linear-gradient(135deg, #0A5AA5 0%, #084a8a 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
        border-bottom: 3px solid #FF6C12;
    }
    .header h1 {
        color: white;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    .header p {
        color: rgba(255,255,255,0.9);
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
    }
    
    /* ETAPA 1: Card do Cenário - COMPACTO */
    .scenario-header {
        background: white;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-left: 5px solid #FF6C12;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .scenario-header-aprovado { border-left-color: #0A5AA5; }
    .scenario-header-reprovado { border-left-color: #FF6C12; }
    
    .scenario-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1f2937;
        margin: 0;
    }
    
    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 0.375rem 0.875rem;
        border-radius: 999px;
        font-weight: 600;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .status-aprovado { background: #0A5AA5; color: white; }
    .status-reprovado { background: #FF6C12; color: white; }
    .status-pendente { background: #f1f5f9; color: #0A5AA5; border: 1.5px solid #0A5AA5; }
    
    /* ETAPA 2: Info Box - AZUL CLARO */
    .info-box {
        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
        padding: 1.25rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border: 1px solid #7dd3fc;
        box-shadow: 0 2px 8px rgba(14, 165, 233, 0.1);
    }
    .info-box strong {
        color: #0c4a6e;
    }
    .info-box-text {
        color: #075985;
        font-size: 0.95rem;
        margin: 0;
    }
    
    /* ETAPA 3: Anexos - LARANJA CLARO com mensagem */
    .files-section {
        background: linear-gradient(135deg, #fff7ed 0%, #fed7aa 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border: 1px solid #fdba74;
        box-shadow: 0 2px 8px rgba(251, 146, 60, 0.1);
    }
    .files-message {
        background: white;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 3px solid #FF6C12;
        font-size: 0.9rem;
        color: #9a3412;
        font-weight: 500;
    }
    .files-section h4 {
        color: #9a3412;
        font-size: 1rem;
        font-weight: 700;
        margin: 0 0 1rem 0;
    }
    
    /* File row */
    .file-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: white;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border: 1px solid #fed7aa;
        gap: 1rem;
    }
    .file-name {
        font-weight: 600;
        color: #1f2937;
        font-size: 0.95rem;
        flex: 1;
    }
    .file-name::before {
        content: "📄 ";
        margin-right: 0.5rem;
    }
    
    /* SEPARADOR VISUAL */
    .section-divider {
        margin: 2rem 0;
        text-align: center;
        position: relative;
    }
    .section-divider::before {
        content: "";
        position: absolute;
        top: 50%;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #0A5AA5, transparent);
    }
    .section-divider-icon {
        background: #0A5AA5;
        color: white;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        position: relative;
        z-index: 1;
        box-shadow: 0 4px 12px rgba(10, 90, 165, 0.3);
    }
    
    /* ETAPA 4: Formulário - BRANCO com borda azul */
    .analysis-section {
        background: white;
        border: 2px solid #0A5AA5;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 4px 16px rgba(10, 90, 165, 0.15);
    }
    .analysis-section h3 {
        margin-top: 0;
        margin-bottom: 0.5rem;
        color: #0A5AA5;
        font-size: 1.4rem;
        font-weight: 700;
    }
    .analysis-message {
        background: #f0f9ff;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border-left: 3px solid #0A5AA5;
        font-size: 0.9rem;
        color: #0c4a6e;
    }
    
    /* Streamlit buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 0.625rem 1.25rem;
        transition: all 0.2s ease;
    }
    .stButton > button[kind="primary"] {
        background: #0A5AA5;
        color: white;
        border: none;
    }
    .stButton > button[kind="primary"]:hover {
        background: #084a8a;
        transform: translateY(-1px);
    }
    .stButton > button[kind="secondary"] {
        background: white;
        color: #FF6C12;
        border: 2px solid #FF6C12;
    }
    .stButton > button[kind="secondary"]:hover {
        background: #FF6C12;
        color: white;
    }
    .stButton > button[kind="tertiary"] {
        background: white;
        color: #64748b;
        border: 2px solid #e2e8f0;
    }
    
    /* Form inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        border-radius: 8px;
        border: 1.5px solid #e5e7eb;
        background: white;
        font-size: 0.95rem;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #0A5AA5;
        box-shadow: 0 0 0 3px rgba(10, 90, 165, 0.1);
    }
    
    /* Expander */
    .stExpander {
        border: none;
        border-radius: 12px;
        margin-bottom: 1rem;
        background: transparent;
        box-shadow: none;
    }
    
    label {
        font-size: 0.9rem;
        font-weight: 600;
        color: #374151;
    }
    
    h3, h4 {
        font-size: 1.2rem;
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

def baixar_arquivo_notion(url):
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': '*/*',
                'Accept-Language': 'pt-BR,pt;q=0.9',
            }
        )
        with urllib.request.urlopen(req, timeout=30, context=ctx) as response:
            return response.read()
    except Exception as e:
        return None

def get_opcoes_select(db_info, coluna_nome):
    if not coluna_nome or coluna_nome not in db_info.get("properties", {}):
        return []
    prop = db_info["properties"][coluna_nome]
    if prop.get("type") == "select":
        options = prop.get("select", {}).get("options", [])
        return [opt.get("name") for opt in options if opt.get("name")]
    return []

# --- INICIALIZAÇÃO ---
notion = Client(auth=NOTION_TOKEN)

id_projetos = encontrar_tabela("Projetos")
id_cenarios = encontrar_tabela("Cenário")
id_analises = encontrar_tabela("Análises")

if not all([id_projetos, id_cenarios, id_analises]):
    st.error("Tabelas não encontradas no Notion.")
    st.stop()

db_info_analises = notion.databases.retrieve(database_id=id_analises)

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
                
                # ETAPA 1: Header do Cenário (COMPACTO)
                card_class = "scenario-header"
                if status == "Aprovado":
                    card_class += " scenario-header-aprovado"
                elif status == "Reprovado":
                    card_class += " scenario-header-reprovado"
                
                if status == "Aprovado":
                    badge_html = '<span class="status-badge status-aprovado">✅ Aprovado</span>'
                elif status == "Reprovado":
                    badge_html = '<span class="status-badge status-reprovado"> Reprovado</span>'
                else:
                    badge_html = '<span class="status-badge status-pendente">⏳ Pronto para Análise</span>'
                
                st.markdown(f"""
                <div class="{card_class}">
                    <div class="scenario-title">{nome_cenario}</div>
                    {badge_html}
                </div>
                """, unsafe_allow_html=True)
                
                # ETAPA 2: Info Box (AZUL CLARO)
                st.markdown(f"""
                <div class="info-box">
                    <p class="info-box-text">
                        <strong> Responsável:</strong> {responsavel} &nbsp;&nbsp;|&nbsp;&nbsp; 
                        <strong>📊 Status:</strong> {status}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # ETAPA 3: Anexos (LARANJA CLARO com mensagem)
                if anexos:
                    titulo_anexos = "Anexo" if len(anexos) == 1 else "Anexos"
                    
                    st.markdown(f"""
                    <div class="files-section">
                        <h4> {titulo_anexos} ({len(anexos)})</h4>
                        <div class="files-message">
                            💡 <strong>Baixe os anexos abaixo</strong> para revisar os documentos antes de registrar sua análise.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for idx, arquivo in enumerate(anexos):
                        conteudo = baixar_arquivo_notion(arquivo['url'])
                        
                        if conteudo:
                            col_nome, col_btn = st.columns([4, 1])
                            
                            with col_nome:
                                st.markdown(f"""
                                <div class="file-row" style="margin-bottom: 0;">
                                    <div class="file-name">{arquivo['nome']}</div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col_btn:
                                st.download_button(
                                    label="️ Baixar",
                                    data=conteudo,
                                    file_name=arquivo['nome'],
                                    mime="application/octet-stream",
                                    key=f"download_{cenario['id']}_{idx}",
                                    type="tertiary",
                                    use_container_width=True
                                )
                        else:
                            st.markdown(f"""
                            <div class="file-row">
                                <div class="file-name">{arquivo['nome']}</div>
                                <a href="{arquivo['url']}" target="_blank" style="background: white; color: #FF6C12; padding: 0.5rem 1rem; border-radius: 8px; text-decoration: none; font-weight: 600; border: 2px solid #FF6C12; display: inline-block;">
                                    🔗 Abrir
                                </a>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)
                else:
                    st.info("📭 Nenhum anexo disponível")
                
                # SEPARADOR VISUAL
                st.markdown("""
                <div class="section-divider">
                    <div class="section-divider-icon"></div>
                </div>
                """, unsafe_allow_html=True)
                
                # ETAPA 4: Formulário (BRANCO com borda azul)
                st.markdown("""
                <div class="analysis-section">
                    <h3>📝 Registrar Nova Análise</h3>
                    <div class="analysis-message">
                         Preencha os campos abaixo para registrar sua análise deste cenário. Cada setor só pode analisar uma vez.
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                with st.form(key=f"form_analise_{cenario['id']}"):
                    col_f1, col_f2 = st.columns(2)
                    
                    with col_f1:
                        nome_input = st.text_input(" Analista Responsável", placeholder="Ex: João Silva")
                        setor_input = st.selectbox(
                            "🏢 Setor",
                            options=[""] + opcoes_setor,
                            format_func=lambda x: "Selecione o setor" if x == "" else x,
                            index=0
                        )
                    
                    with col_f2:
                        status_input = st.selectbox(
                            "✅ Status",
                            options=[""] + opcoes_status,
                            format_func=lambda x: "Selecione o status" if x == "" else x,
                            index=0
                        )
                        motivo_input = st.text_area(
                            "💬 Motivo (obrigatório se reprovado)",
                            placeholder="Explique o motivo da reprovação..."
                        )
                    
                    submit = st.form_submit_button("💾 Salvar Análise", type="primary", use_container_width=True)
                    
                    if submit:
                        if not nome_input:
                            st.error("❌ Preencha o nome do analista.")
                        elif not setor_input:
                            st.error("❌ Selecione o setor.")
                        elif not status_input:
                            st.error("❌ Selecione o status.")
                        elif status_input == "Reprovado" and not motivo_input:
                            st.error("❌ Informe o motivo da reprovação.")
                        else:
                            # Verificar se este setor já analisou
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
                                setor_existente = get_status_safe(a_props, colunas_reais.get("setor"))
                                if setor_existente == setor_input:
                                    setor_ja_analisou = True
                                    break
                            
                            if setor_ja_analisou:
                                st.error(f"❌ O setor '{setor_input}' já realizou uma análise deste cenário e não pode alterar.")
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
    
    except Exception as e:
        st.error(f"❌ Erro: {e}")
