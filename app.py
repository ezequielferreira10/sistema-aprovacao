import streamlit as st
from notion_client import Client

# --- CONFIGURAÇÕES ---

NOTION_TOKEN = "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"
DATABASE_ID = "f5d3222e-f158-4985-bc0f-3d0228bfb402"

st.set_page_config(page_title="Aprovação", page_icon="✅", layout="wide")
st.title("️ Sistema de Aprovação - Reforma Tributária")
st.markdown("---")

notion = Client(auth=NOTION_TOKEN)

try:
    response = notion.databases.query(
        database_id=DATABASE_ID,
        filter={
            "property": "Status",
            "select": {
                "equals": "Pronto para Análise"
            }
        }
    )
    
    resultados = response.get("results", [])
    
    if not resultados:
        st.info("📭 Nenhum cenário pendente de análise!")
    else:
        st.success(f"✅ Encontrados **{len(resultados)}** cenário(s) para análise")
        
        for item in resultados:
            props = item["properties"]
            
            # Nome do cenário
            nome = "Sem nome"
            if "Cenário" in props:
                titulos = props["Cenário"].get("title", [])
                if titulos:
                    nome = titulos[0].get("plain_text", "Sem nome")
            
            # Especialista
            especialista = "Não definido"
            if "Responsável" in props and props["Responsável"].get("people"):
                especialista = props["Responsável"]["people"][0].get("name", "Não definido")
            
            # Anexos (arquivos)
            anexos = []
            if "Anexos" in props:
                arquivos = props["Anexos"].get("files", [])
                for arquivo in arquivos:
                    if arquivo.get("external", {}).get("url"):
                        anexos.append({
                            "nome": arquivo.get("name", "Arquivo sem nome"),
                            "url": arquivo["external"]["url"]
                        })
                    elif arquivo.get("file", {}).get("url"):
                        anexos.append({
                            "nome": arquivo.get("name", "Arquivo sem nome"),
                            "url": arquivo["file"]["url"]
                        })
            
            # Card do cenário
            with st.container(border=True):
                st.subheader(f"📄 {nome}")
                st.write(f"**Especialista:** {especialista}")
                
                # Mostrar anexos se existirem
                if anexos:
                    st.write("**📎 Arquivos anexados:**")
                    for i, arquivo in enumerate(anexos, 1):
                        st.write(f"{i}. **{arquivo['nome']}**")
                        # Botão para abrir/link direto
                        st.link_button(f"📥 Download: {arquivo['nome']}", arquivo['url'])
                    st.markdown("---")
                else:
                    st.warning("⚠️ Nenhum arquivo anexado")
                    st.markdown("---")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("✅ Aprovar", key=f"ap_{item['id']}"):
                        notion.pages.update(
                            page_id=item["id"],
                            properties={
                                "Status": {
                                    "select": {
                                        "name": "Aprovado"
                                    }
                                }
                            }
                        )
                        st.success(f"✔️ '{nome}' foi APROVADO!")
                        st.rerun()
                
                with col2:
                    if st.button("❌ Reprovar", key=f"rp_{item['id']}"):
                        notion.pages.update(
                            page_id=item["id"],
                            properties={
                                "Status": {
                                    "select": {
                                        "name": "Reprovado"
                                    }
                                }
                            }
                        )
                        st.error(f"️ '{nome}' foi REPROVADO!")
                        st.rerun()
            
            st.markdown("---")
            
except Exception as e:
    st.error(f" Erro: {str(e)}")
