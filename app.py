import streamlit as st
from notion_client import Client
from datetime import datetime

# --- CONFIGURAÇÕES ---
NOTION_TOKEN = "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"

st.set_page_config(page_title="Sistema de Aprovação", page_icon="🏛️", layout="wide")

# --- CSS PERSONALIZADO (Visual Profissional) ---
st.markdown("""
<style>
    /* Fundo e fontes */
    .main {
        background-color: #f5f7fa;
    }
    h1, h2, h3 {
        color: #1e3a8a;
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* Título principal */
    .titulo-principal {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .titulo-principal h1 {
        color: white;
        font-size: 2.5rem;
        margin: 0;
    }
    
    /* Cards de cenário */
    .stExpander {
        border: 2px solid #e5e7eb;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .stExpander:hover {
        border-color: #3b82f6;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
    }
    
    /* Status */
    .status-pronto { color: #f59e0b; font-weight: bold; }
    .status-aprovado { color: #10b981; font-weight: bold; }
    .status-reprovado { color: #ef4444; font-weight: bold; }
    
    /* Cards de análise */
    .card-analise {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #3b82f6;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .card-analise-aprovado {
        border-left-color: #10b981;
        background: #f0fdf4;
    }
    .card-analise-reprovado {
        border-left-color: #ef4444;
        background: #fef2f2;
    }
    
    /* Botões */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 2px solid #e5e7eb;
    }
    
    /* Destaque para projetos importantes */
    .projeto-destaque {
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Título personalizado
st.markdown("""
<div class="titulo-principal">
    <h1>🏛️ Sistema de Aprovação - Compliance Tributário</h1>
    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Gestão de Projetos e Cenários Fiscais</p>
</div>
""", unsafe_allow_html=True)

notion = Client(auth=NOTION_TOKEN)

# --- Buscar tabelas ---
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

id_projetos = encontrar_tabela("Projetos")
id_cenarios = encontrar_tabela("Cenário")
id_analises = encontrar_tabela("Análises")

if not all([id_projetos, id_cenarios, id_analises]):
    st.error(" Tabelas não encontradas no Notion.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 📁 Projetos")
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
            
            projeto_escolhido = st.selectbox(
                "Selecione o projeto:",
                options=lista_projetos,
                format_func=lambda x: x["nome"]
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
    st.markdown(f"### 📋 Cenários - {projeto_escolhido['nome']}")
    st.markdown("---")
    
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
            st.success(f"✅ **{len(cenarios)} cenário(s)** encontrado(s)")
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
            
            # Mostrar cenários
            for cenario in cenarios:
                props = cenario["properties"]
                
                # Nome do cenário
                nome_cenario = "Sem nome"
                for col in ["Cenário", "Cenario", "Nome", "Name"]:
                    if col in props:
                        titulos = props[col].get("title", [])
                        if titulos:
                            nome_cenario = titulos[0].get("plain_text", "Sem nome")
                            break
                
                # Destaque para cenários importantes
                destaque = ""
                if any(x in nome_cenario.upper() for x in ["SAP", "RECUP", "ICMS", "IPI"]):
                    destaque = ""
                
                # Status
                status = "Desconhecido"
                if "Status" in props and props["Status"].get("select"):
                    status = props["Status"]["select"].get("name", "Desconhecido")
                
                # Ícone de status
                icone_status = "🟢" if status == "Aprovado" else "🔴" if status == "Reprovado" else "🟡"
                
                # Responsável
                responsavel = "Não definido"
                if "Responsável" in props and props["Responsável"].get("people"):
                    responsavel = props["Responsável"]["people"][0].get("name", "Não definido")
                
                # Anexos
                anexos = []
                if "Anexos" in props:
                    arquivos = props["Anexos"].get("files", [])
                    for arquivo in arquivos:
                        if arquivo.get("external", {}).get("url"):
                            anexos.append({"nome": arquivo.get("name", "Arquivo"), "url": arquivo["external"]["url"]})
                        elif arquivo.get("file", {}).get("url"):
                            anexos.append({"nome": arquivo.get("name", "Arquivo"), "url": arquivo["file"]["url"]})
                
                # Card do cenário
                with st.expander(f"{destaque} 📄 **{nome_cenario}** {icone_status} - {status}", expanded=False):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**👤 Responsável:** {responsavel}")
                        if anexos:
                            st.markdown("**📎 Arquivos:**")
                            cols_anexo = st.columns(len(anexos))
                            for idx, arquivo in enumerate(anexos):
                                with cols_anexo[idx]:
                                    st.link_button(f"📥 {arquivo['nome'][:15]}...", arquivo['url'])
                    
                    with col2:
                        if status == "Aprovado":
                            st.markdown('<div class="status-aprovado">✅ APROVADO</div>', unsafe_allow_html=True)
                        elif status == "Reprovado":
                            st.markdown('<div class="status-reprovado">❌ REPROVADO</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="status-pronto">⏳ AGUARDANDO</div>', unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # --- ANÁLISES ---
                    st.markdown("### 📊 Análises por Setor")
                    
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
                            
                            # Card visual da análise
                            classe_card = "card-analise "
                            if status_analise == "Aprovado":
                                classe_card += "card-analise-aprovado"
                            elif status_analise == "Reprovado":
                                classe_card += "card-analise-reprovado"
                            
                            with st.container():
                                st.markdown(f"""
                                <div class="{classe_card}">
                                    <div style="display: flex; justify-content: space-between; align-items: start;">
                                        <div>
                                            <strong style="font-size: 1.1rem;">{nome_analise}</strong><br>
                                            🏢 <strong>Setor:</strong> {setor}<br>
                                            👤 <strong>Analista:</strong> {analista}<br>
                                            {f'📝 <strong>Motivo:</strong> {motivo}<br>' if motivo else ''}
                                            {f'📅 <strong>Data:</strong> {data_analise}<br>' if data_analise else ''}
                                        </div>
                                        <div style="font-size: 1.5rem; font-weight: bold;">
                                            {'🟢 APROVADO' if status_analise == 'Aprovado' else '🔴 REPROVADO' if status_analise == 'Reprovado' else '🟡 EM ANÁLISE'}
                                        </div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info(" Nenhuma análise registrada ainda.")
                    
                    st.markdown("---")
                    
                    # --- FORMULÁRIO ---
                    st.markdown("### ➕ Registrar Nova Análise")
                    
                    with st.form(key=f"form_analise_{cenario['id']}"):
                        col_f1, col_f2 = st.columns(2)
                        
                        with col_f1:
                            nome_input = st.text_input("Nome da Análise:", placeholder="Ex: Análise Contábil")
                            setor_input = st.selectbox(
                                "Setor:",
                                options=["Contabilidade", "Apuração", "Fiscal", "Jurídico", "Auditoria"]
                            )
                            analista_input = st.text_input("Nome do Analista:", placeholder="Ex: João Silva")
                        
                        with col_f2:
                            status_input = st.selectbox(
                                "Status:",
                                options=["Aprovado", "Reprovado", "Em Análise"]
                            )
                            motivo_input = st.text_area(
                                "Motivo (obrigatório se reprovado):",
                                placeholder="Explique o motivo..."
                            )
                        
                        submit = st.form_submit_button("💾 Salvar Análise", type="primary", use_container_width=True)
                        
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
                                    st.success(f"✅ Análise '{nome_input}' salva!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro: {e}")
                    
                    st.markdown("---")
                    
                    # Botões finais
                    if status == "Pronto para Análise":
                        st.markdown("### ✅ Decisão Final")
                        col_ap, col_rp = st.columns(2)
                        with col_ap:
                            if st.button("✅ APROVAR CENÁRIO", type="success", use_container_width=True, key=f"ap_{cenario['id']}"):
                                notion.pages.update(page_id=cenario["id"], properties={"Status": {"select": {"name": "Aprovado"}}})
                                st.balloons()
                                st.success("Cenário Aprovado!")
                                st.rerun()
                        with col_rp:
                            if st.button("❌ REPROVAR CENÁRIO", type="error", use_container_width=True, key=f"rp_{cenario['id']}"):
                                notion.pages.update(page_id=cenario["id"], properties={"Status": {"select": {"name": "Reprovado"}}})
                                st.error("Cenário Reprovado!")
                                st.rerun()
    
    except Exception as e:
        st.error(f"❌ Erro: {e}")
