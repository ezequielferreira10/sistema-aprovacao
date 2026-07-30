import streamlit as st
from notion_client import Client
from datetime import datetime

# --- CONFIGURAÇÕES ---
NOTION_TOKEN = "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"

st.set_page_config(page_title="Sistema de Aprovação", page_icon="🏛️", layout="wide")
st.title("🏛️ Sistema de Aprovação - Compliance Tributário")
st.markdown("---")

notion = Client(auth=NOTION_TOKEN)

# --- Buscar tabelas automaticamente ---
def encontrar_tabela(nome_tabela):
    """Busca uma tabela pelo nome"""
    response = notion.search(
        query=nome_tabela,
        filter={"value": "database", "property": "object"}
    )
    resultados = response.get("results", [])
    if resultados:
        return resultados[0]["id"]
    return None

# Encontra os IDs das tabelas automaticamente
id_projetos = encontrar_tabela("Projetos")
id_cenarios = encontrar_tabela("Cenário")
id_analises = encontrar_tabela("Análises")

if not id_projetos:
    st.error("❌ Tabela 'Projetos' não encontrada.")
    st.stop()

if not id_cenarios:
    st.error("❌ Tabela 'Cenário' não encontrada.")
    st.stop()

if not id_analises:
    st.warning("️ Tabela 'Análises' não encontrada.")
    st.stop()

# --- SIDEBAR: Seleção de Projetos ---
st.sidebar.title("📁 Projetos")

try:
    # Busca todos os projetos
    projetos_response = notion.databases.query(
        database_id=id_projetos
    )
    projetos = projetos_response.get("results", [])
    
    if projetos:
        # Cria lista de nomes de projetos
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
        
        # Dropdown para selecionar projeto
        projeto_escolhido = st.sidebar.selectbox(
            "Selecione o projeto:",
            options=lista_projetos,
            format_func=lambda x: x["nome"]
        )
        
        if projeto_escolhido:
            st.sidebar.success(f"✅ Projeto: {projeto_escolhido['nome']}")
            
            # --- ÁREA PRINCIPAL: Cenários do Projeto ---
            st.header(f"📋 Cenários - {projeto_escolhido['nome']}")
            
            # Busca cenários relacionados ao projeto
            cenarios_response = notion.databases.query(
                database_id=id_cenarios,
                filter={
                    "property": "Projeto",
                    "relation": {
                        "contains": projeto_escolhido["id"]
                    }
                }
            )
            
            cenarios = cenarios_response.get("results", [])
            
            if not cenarios:
                st.info(" Nenhum cenário encontrado para este projeto.")
            else:
                st.success(f"✅ Encontrados **{len(cenarios)}** cenário(s)")
                
                for cenario in cenarios:
                    props = cenario["properties"]
                    
                    # Nome do cenário
                    nome_cenario = "Sem nome"
                    for col in ["Cenário", "Nome", "Name"]:
                        if col in props:
                            titulos = props[col].get("title", [])
                            if titulos:
                                nome_cenario = titulos[0].get("plain_text", "Sem nome")
                                break
                    
                    # Status
                    status = "Desconhecido"
                    if "Status" in props and props["Status"].get("select"):
                        status = props["Status"]["select"].get("name", "Desconhecido")
                    
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
                                anexos.append({
                                    "nome": arquivo.get("name", "Arquivo"),
                                    "url": arquivo["external"]["url"]
                                })
                            elif arquivo.get("file", {}).get("url"):
                                anexos.append({
                                    "nome": arquivo.get("name", "Arquivo"),
                                    "url": arquivo["file"]["url"]
                                })
                    
                    # Card do Cenário (Expansível)
                    with st.expander(f"📄 {nome_cenario} - {status}", expanded=False):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Responsável:** {responsavel}")
                            st.write(f"**Status:** {status}")
                        
                        with col2:
                            if anexos:
                                st.write("**📎 Arquivos:**")
                                for arquivo in anexos:
                                    st.link_button(
                                        f" {arquivo['nome']}",
                                        arquivo['url']
                                    )
                            else:
                                st.warning("⚠️ Sem arquivos")
                        
                        st.markdown("---")
                        
                        # --- SEÇÃO DE ANÁLISES ---
                        st.subheader("📊 Análises por Setor")
                        
                        # Busca todas as análises deste cenário
                        analises_response = notion.databases.query(
                            database_id=id_analises,
                            filter={
                                "property": "Cenário",
                                "relation": {
                                    "contains": cenario["id"]
                                }
                            }
                        )
                        
                        analises = analises_response.get("results", [])
                        
                        if analises:
                            for analise in analises:
                                a_props = analise["properties"]
                                
                                # Nome da análise
                                nome_analise = "Sem nome"
                                if "Nome da Análise" in a_props:
                                    titulos = a_props["Nome da Análise"].get("title", [])
                                    if titulos:
                                        nome_analise = titulos[0].get("plain_text", "Sem nome")
                                
                                # Setor
                                setor = "Não definido"
                                if "Setor" in a_props and a_props["Setor"].get("select"):
                                    setor = a_props["Setor"]["select"].get("name", "Não definido")
                                
                                # Analista
                                analista = "Não definido"
                                if "Analista Responsável" in a_props:
                                    if a_props["Analista Responsável"].get("people"):
                                        analista = a_props["Analista Responsável"]["people"][0].get("name", "Não definido")
                                    elif a_props["Analista Responsável"].get("rich_text"):
                                        analista = a_props["Analista Responsável"]["rich_text"][0].get("plain_text", "Não definido")
                                
                                # Status da análise
                                status_analise = "Não definido"
                                if "Status" in a_props and a_props["Status"].get("select"):
                                    status_analise = a_props["Status"]["select"].get("name", "Não definido")
                                
                                # Motivo
                                motivo = ""
                                if "Motivo" in a_props and a_props["Motivo"].get("rich_text"):
                                    motivo = a_props["Motivo"]["rich_text"][0].get("plain_text", "")
                                
                                # Data
                                data_analise = ""
                                if "Data" in a_props and a_props["Data"].get("date"):
                                    data_analise = a_props["Data"]["date"].get("start", "")
                                
                                # Card da análise
                                cor_status = "🟢" if status_analise == "Aprovado" else "🔴" if status_analise == "Reprovado" else "🟡"
                                
                                with st.container(border=True):
                                    col_a1, col_a2 = st.columns([3, 1])
                                    
                                    with col_a1:
                                        st.write(f"**{nome_analise}**")
                                        st.write(f"🏢 **Setor:** {setor}")
                                        st.write(f"👤 **Analista:** {analista}")
                                        if motivo:
                                            st.write(f"📝 **Motivo:** {motivo}")
                                        if data_analise:
                                            st.write(f" **Data:** {data_analise}")
                                    
                                    with col_a2:
                                        st.write(f"{cor_status} **{status_analise}**")
                                    
                                    st.markdown("---")
                        else:
                            st.info("📭 Nenhuma análise registrada ainda.")
                        
                        st.markdown("---")
                        
                        # --- FORMULÁRIO PARA NOVA ANÁLISE ---
                        st.subheader("➕ Registrar Nova Análise")
                        
                        with st.form(key=f"form_analise_{cenario['id']}"):
                            col_form1, col_form2 = st.columns(2)
                            
                            with col_form1:
                                nome_analise_input = st.text_input("Nome da Análise:", placeholder="Ex: Análise Contábil")
                                setor_input = st.selectbox(
                                    "Setor:",
                                    options=["Contabilidade", "Apuração", "Fiscal", "Jurídico", "Auditoria"]
                                )
                                analista_input = st.text_input("Nome do Analista:", placeholder="Ex: João Silva")
                            
                            with col_form2:
                                status_analise_input = st.selectbox(
                                    "Status da Análise:",
                                    options=["Aprovado", "Reprovado", "Em Análise"]
                                )
                                motivo_input = st.text_area(
                                    "Motivo (obrigatório se reprovado):",
                                    placeholder="Explique o motivo da reprovação..."
                                )
                            
                            submit_button = st.form_submit_button("💾 Salvar Análise")
                            
                            if submit_button:
                                # Validação
                                if not nome_analise_input:
                                    st.error("❌ Por favor, preencha o nome da análise.")
                                elif not analista_input:
                                    st.error("❌ Por favor, preencha o nome do analista.")
                                elif status_analise_input == "Reprovado" and not motivo_input:
                                    st.error("❌ Por favor, informe o motivo da reprovação.")
                                else:
                                    # Criar a análise no Notion
                                    try:
                                        # Data de hoje
                                        data_hoje = datetime.now().strftime("%Y-%m-%d")
                                        
                                        # Criar página na tabela Análises
                                        nova_analise = notion.pages.create(
                                            parent={"database_id": id_analises},
                                            properties={
                                                "Nome da Análise": {
                                                    "title": [{"text": {"content": nome_analise_input}}]
                                                },
                                                "Cenário": {
                                                    "relation": [{"id": cenario["id"]}]
                                                },
                                                "Setor": {
                                                    "select": {"name": setor_input}
                                                },
                                                "Analista Responsável": {
                                                    "rich_text": [{"text": {"content": analista_input}}]
                                                },
                                                "Status": {
                                                    "select": {"name": status_analise_input}
                                                },
                                                "Motivo": {
                                                    "rich_text": [{"text": {"content": motivo_input}}] if motivo_input else []
                                                },
                                                "Data": {
                                                    "date": {"start": data_hoje}
                                                }
                                            }
                                        )
                                        
                                        st.success(f"✅ Análise '{nome_analise_input}' salva com sucesso!")
                                        st.rerun()
                                        
                                    except Exception as e:
                                        st.error(f"❌ Erro ao salvar análise: {str(e)}")
                        
                        st.markdown("---")
                        
                        # Botões de Aprovação do Cenário (nível macro)
                        if status == "Pronto para Análise":
                            st.subheader("✅ Decisão Final do Cenário")
                            col_aprovar, col_reprovar = st.columns(2)
                            
                            with col_aprovar:
                                if st.button("✅ Aprovar Cenário (Final)", key=f"ap_final_{cenario['id']}"):
                                    notion.pages.update(
                                        page_id=cenario["id"],
                                        properties={
                                            "Status": {
                                                "select": {"name": "Aprovado"}
                                            }
                                        }
                                    )
                                    st.success("✔️ Cenário Aprovado!")
                                    st.rerun()
                            
                            with col_reprovar:
                                if st.button("❌ Reprovar Cenário (Final)", key=f"rp_final_{cenario['id']}"):
                                    notion.pages.update(
                                        page_id=cenario["id"],
                                        properties={
                                            "Status": {
                                                "select": {"name": "Reprovado"}
                                            }
                                        }
                                    )
                                    st.error("✖️ Cenário Reprovado!")
                                    st.rerun()
    else:
        st.warning("⚠️ Nenhum projeto encontrado no Notion.")
        
except Exception as e:
    st.error(f"❌ Erro: {str(e)}")
    st.info("💡 Verifique se as tabelas 'Projetos', 'Cenário' e 'Análises' existem no Notion.")
