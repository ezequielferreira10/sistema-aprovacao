import streamlit as st
from notion_client import Client
from datetime import datetime

# --- CONFIGURAÇÕES ---
NOTION_TOKEN = "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"

st.set_page_config(page_title="Sistema de Aprovação", page_icon="️", layout="wide")
st.title("🏛️ Sistema de Aprovação - Compliance Tributário")
st.markdown("---")

notion = Client(auth=NOTION_TOKEN)

# --- Buscar tabelas automaticamente ---
def encontrar_tabela(nome_tabela):
    response = notion.search(
        query=nome_tabela,
        filter={"value": "database", "property": "object"}
    )
    resultados = response.get("results", [])
    if resultados:
        return resultados[0]["id"]
    return None

# --- Buscar nome real da coluna ---
def encontrar_coluna(props, nomes_possiveis):
    for nome in nomes_possiveis:
        if nome in props:
            return nome
    return None

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
    st.error("❌ Tabela 'Análises' não encontrada.")
    st.stop()

st.sidebar.title("📁 Projetos")

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
        
        projeto_escolhido = st.sidebar.selectbox(
            "Selecione o projeto:",
            options=lista_projetos,
            format_func=lambda x: x["nome"]
        )
        
        if projeto_escolhido:
            st.sidebar.success(f"✅ Projeto: {projeto_escolhido['nome']}")
            st.header(f"📋 Cenários - {projeto_escolhido['nome']}")
            
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
                st.success(f"✅ Encontrados **{len(cenarios)}** cenário(s)")
                
                # --- DESCOBRIR NOMES DAS COLUNAS DA TABELA ANÁLISES ---
                db_info = notion.databases.retrieve(database_id=id_analises)
                todas_props = db_info.get("properties", {})
                
                # Nomes possíveis para cada coluna
                nomes_colunas = {
                    "nome_analise": ["Nome da Análise", "Nome da Analise", "Nome", "Name", "Título", "Titulo"],
                    "setor": ["Setor", "Área", "Area", "Departamento"],
                    "analista": ["Analista Responsável", "Analista Responsavel", "Analista", "Responsável", "Responsavel", "Analista responsável", "Analista responsavel"],
                    "status": ["Status", "Situação", "Situacao"],
                    "motivo": ["Motivo", "Motivo da Reprovação", "Observação", "Observacao", "Comentário", "Comentario"],
                    "data": ["Data", "Date", "Data da Análise"]
                }
                
                # Descobre os nomes reais
                colunas_reais = {}
                for chave, possiveis in nomes_colunas.items():
                    colunas_reais[chave] = encontrar_coluna(todas_props, possiveis)
                
                # **IMPORTANTE:** Encontra a coluna do tipo RELATION (que vincula com Cenário)
                col_relation = None
                for prop_name, prop_info in todas_props.items():
                    if prop_info.get("type") == "relation":
                        col_relation = prop_name
                        break
                
                # Mostra debug
                with st.expander("🔍 Nomes das colunas detectados (debug)"):
                    st.write(colunas_reais)
                    st.write(f"**Coluna de Relation encontrada:** {col_relation}")
                
                if not col_relation:
                    st.error("❌ Não foi encontrada uma coluna do tipo 'Relation' na tabela Análises!")
                    st.info(" Verifique se você criou a coluna que vincula com a tabela Cenário.")
                    st.stop()
                
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
                    
                    with st.expander(f"📄 {nome_cenario} - {status}", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Responsável:** {responsavel}")
                            st.write(f"**Status:** {status}")
                        with col2:
                            if anexos:
                                st.write("**📎 Arquivos:**")
                                for arquivo in anexos:
                                    st.link_button(f"📥 {arquivo['nome']}", arquivo['url'])
                            else:
                                st.warning("⚠️ Sem arquivos")
                        
                        st.markdown("---")
                        
                        # --- ANÁLISES EXISTENTES ---
                        st.subheader("📊 Análises por Setor")
                        
                        # Busca análises usando a coluna de RELATION correta
                        analises_response = notion.databases.query(
                            database_id=id_analises,
                            filter={
                                "property": col_relation,  # Usa a coluna de relation que encontramos!
                                "relation": {"contains": cenario["id"]}
                            }
                        )
                        
                        analises = analises_response.get("results", [])
                        
                        if analises:
                            for analise in analises:
                                a_props = analise["properties"]
                                
                                # Nome
                                nome_analise = "Sem nome"
                                col_nome = colunas_reais.get("nome_analise")
                                if col_nome and col_nome in a_props:
                                    titulos = a_props[col_nome].get("title", [])
                                    if titulos:
                                        nome_analise = titulos[0].get("plain_text", "Sem nome")
                                
                                # Setor
                                setor = "Não definido"
                                col_setor = colunas_reais.get("setor")
                                if col_setor and col_setor in a_props and a_props[col_setor].get("select"):
                                    setor = a_props[col_setor]["select"].get("name", "Não definido")
                                
                                # Analista
                                analista = "Não definido"
                                col_analista = colunas_reais.get("analista")
                                if col_analista and col_analista in a_props:
                                    if a_props[col_analista].get("people"):
                                        analista = a_props[col_analista]["people"][0].get("name", "Não definido")
                                    elif a_props[col_analista].get("rich_text"):
                                        textos = a_props[col_analista]["rich_text"]
                                        if textos:
                                            analista = textos[0].get("plain_text", "Não definido")
                                
                                # Status
                                status_analise = "Não definido"
                                col_status = colunas_reais.get("status")
                                if col_status and col_status in a_props and a_props[col_status].get("select"):
                                    status_analise = a_props[col_status]["select"].get("name", "Não definido")
                                
                                # Motivo
                                motivo = ""
                                col_motivo = colunas_reais.get("motivo")
                                if col_motivo and col_motivo in a_props and a_props[col_motivo].get("rich_text"):
                                    textos = a_props[col_motivo]["rich_text"]
                                    if textos:
                                        motivo = textos[0].get("plain_text", "")
                                
                                # Data
                                data_analise = ""
                                col_data = colunas_reais.get("data")
                                if col_data and col_data in a_props and a_props[col_data].get("date"):
                                    data_analise = a_props[col_data]["date"].get("start", "")
                                
                                cor_status = "🟢" if status_analise == "Aprovado" else "🔴" if status_analise == "Reprovado" else "🟡"
                                
                                with st.container(border=True):
                                    col_a1, col_a2 = st.columns([3, 1])
                                    with col_a1:
                                        st.write(f"**{nome_analise}**")
                                        st.write(f" **Setor:** {setor}")
                                        st.write(f"👤 **Analista:** {analista}")
                                        if motivo:
                                            st.write(f"📝 **Motivo:** {motivo}")
                                        if data_analise:
                                            st.write(f"📅 **Data:** {data_analise}")
                                    with col_a2:
                                        st.write(f"{cor_status} **{status_analise}**")
                                    st.markdown("---")
                        else:
                            st.info(" Nenhuma análise registrada ainda.")
                        
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
                                if not nome_analise_input:
                                    st.error("❌ Por favor, preencha o nome da análise.")
                                elif not analista_input:
                                    st.error("❌ Por favor, preencha o nome do analista.")
                                elif status_analise_input == "Reprovado" and not motivo_input:
                                    st.error("❌ Por favor, informe o motivo da reprovação.")
                                else:
                                    try:
                                        data_hoje = datetime.now().strftime("%Y-%m-%d")
                                        
                                        # Monta propriedades
                                        propriedades = {}
                                        
                                        if colunas_reais.get("nome_analise"):
                                            propriedades[colunas_reais["nome_analise"]] = {
                                                "title": [{"text": {"content": nome_analise_input}}]
                                            }
                                        
                                        if colunas_reais.get("setor"):
                                            propriedades[colunas_reais["setor"]] = {
                                                "select": {"name": setor_input}
                                            }
                                        
                                        if colunas_reais.get("analista"):
                                            propriedades[colunas_reais["analista"]] = {
                                                "rich_text": [{"text": {"content": analista_input}}]
                                            }
                                        
                                        if colunas_reais.get("status"):
                                            propriedades[colunas_reais["status"]] = {
                                                "select": {"name": status_analise_input}
                                            }
                                        
                                        if colunas_reais.get("motivo"):
                                            propriedades[colunas_reais["motivo"]] = {
                                                "rich_text": [{"text": {"content": motivo_input}}] if motivo_input else []
                                            }
                                        
                                        if colunas_reais.get("data"):
                                            propriedades[colunas_reais["data"]] = {
                                                "date": {"start": data_hoje}
                                            }
                                        
                                        # Adiciona a RELATION (coluna que vincula com o cenário)
                                        propriedades[col_relation] = {
                                            "relation": [{"id": cenario["id"]}]
                                        }
                                        
                                        nova_analise = notion.pages.create(
                                            parent={"database_id": id_analises},
                                            properties=propriedades
                                        )
                                        
                                        st.success(f"✅ Análise '{nome_analise_input}' salva com sucesso!")
                                        st.rerun()
                                        
                                    except Exception as e:
                                        st.error(f"❌ Erro ao salvar análise: {str(e)}")
                                        st.info(f"💡 Detalhes: Verifique se todas as colunas existem na tabela Análises")
                        
                        st.markdown("---")
                        
                        # Botões de Aprovação Final
                        if status == "Pronto para Análise":
                            st.subheader("✅ Decisão Final do Cenário")
                            col_aprovar, col_reprovar = st.columns(2)
                            with col_aprovar:
                                if st.button("✅ Aprovar Cenário (Final)", key=f"ap_final_{cenario['id']}"):
                                    notion.pages.update(
                                        page_id=cenario["id"],
                                        properties={"Status": {"select": {"name": "Aprovado"}}}
                                    )
                                    st.success("✔️ Cenário Aprovado!")
                                    st.rerun()
                            with col_reprovar:
                                if st.button("❌ Reprovar Cenário (Final)", key=f"rp_final_{cenario['id']}"):
                                    notion.pages.update(
                                        page_id=cenario["id"],
                                        properties={"Status": {"select": {"name": "Reprovado"}}}
                                    )
                                    st.error("✖️ Cenário Reprovado!")
                                    st.rerun()
    else:
        st.warning("⚠️ Nenhum projeto encontrado no Notion.")
        
except Exception as e:
    st.error(f"❌ Erro: {str(e)}")
    import traceback
    st.code(traceback.format_exc())
