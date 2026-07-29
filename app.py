import streamlit as st
from notion_client import Client

# --- CONFIGURAÇÕES ---
# COLE SEU TOKEN AQUI (entre as aspas)
NOTION_TOKEN = "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"

# IDs das tabelas
DATABASE_ID_PROJETOS = "f45980a4-81f8-4bfb-890f-dccc7701848b"
DATABASE_ID_CENARIOS = "3ac4a13f-92e7-8045-95c8-fe2ebde78bcb"

st.set_page_config(page_title="Sistema de Aprovação", page_icon="️", layout="wide")
st.title("🏛️ Sistema de Aprovação - Compliance Tributário")
st.markdown("---")

notion = Client(auth=NOTION_TOKEN)

# --- SIDEBAR: Seleção de Projetos ---
st.sidebar.title(" Projetos")

try:
    # Busca todos os projetos
    projetos_response = notion.databases.query(
        database_id=DATABASE_ID_PROJETOS
    )
    projetos = projetos_response.get("results", [])
    
    if projetos:
        # Cria lista de nomes de projetos
        lista_projetos = []
        for proj in projetos:
            props = proj["properties"]
            nome_proj = "Sem nome"
            if "Projeto" in props:
                titulos = props["Projeto"].get("title", [])
                if titulos:
                    nome_proj = titulos[0].get("plain_text", "Sem nome")
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
                database_id=DATABASE_ID_CENARIOS,
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
                    if "Cenário" in props:
                        titulos = props["Cenário"].get("title", [])
                        if titulos:
                            nome_cenario = titulos[0].get("plain_text", "Sem nome")
                    
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
                                st.write("** Arquivos:**")
                                for arquivo in anexos:
                                    st.link_button(
                                        f"📥 {arquivo['nome']}",
                                        arquivo['url']
                                    )
                            else:
                                st.warning("⚠️ Sem arquivos")
                        
                        st.markdown("---")
                        
                        # Botões de Aprovação (só aparece se estiver "Pronto para Análise")
                        if status == "Pronto para Análise":
                            col_aprovar, col_reprovar = st.columns(2)
                            
                            with col_aprovar:
                                if st.button("✅ Aprovar", key=f"ap_{cenario['id']}"):
                                    notion.pages.update(
                                        page_id=cenario["id"],
                                        properties={
                                            "Status": {
                                                "select": {"name": "Aprovado"}
                                            }
                                        }
                                    )
                                    st.success("✔️ Aprovado!")
                                    st.rerun()
                            
                            with col_reprovar:
                                if st.button("❌ Reprovar", key=f"rp_{cenario['id']}"):
                                    notion.pages.update(
                                        page_id=cenario["id"],
                                        properties={
                                            "Status": {
                                                "select": {"name": "Reprovado"}
                                            }
                                        }
                                    )
                                    st.error("✖️ Reprovado!")
                                    st.rerun()
    else:
        st.warning("⚠️ Nenhum projeto encontrado no Notion.")
        
except Exception as e:
    st.error(f"❌ Erro: {str(e)}")
    st.info(" Verifique se os IDs das tabelas estão corretos e se a integração tem acesso.")
