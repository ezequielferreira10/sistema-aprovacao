import streamlit as st
from notion_client import Client
from datetime import datetime
import urllib.request
import ssl

NOTION_TOKEN = "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"

st.set_page_config(page_title="Compliance Tributário", page_icon="🏛️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* ESCONDER BOTÕES SUPERIORES */
    header[data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    footer { display: none !important; }
    
    * { box-sizing: border-box; }
    
    body {
        background-color: #f1f5f9;
        font-family: 'Inter', sans-serif;
        font-size: 14px;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0A5AA5 0%, #0c4a8a 100%);
        padding: 2rem 1.5rem;
    }
    [data-testid="stSidebar"] * { color: white !important; }
    
    [data-testid="stSidebar"] h3 {
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
        padding-bottom: 1rem !important;
        border-bottom: 2px solid rgba(255,255,255,0.2) !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox > div > div > div {
        background-color: white !important;
        border-radius: 8px !important;
        padding: 0.5rem !important;
    }
    [data-testid="stSidebar"] .stSelectbox > div > div > div > div {
        color: #0A5AA5 !important;
        font-weight: 600 !important;
    }
    
    .main {
        background-color: #f1f5f9;
        padding: 2rem 3rem;
    }
    
    .header {
        background: linear-gradient(135deg, #0A5AA5 0%, #084a8a 100%);
        padding: 3rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
    }
    .header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin: 0.75rem 0 0 0;
    }
    
    .section-label {
        font-size: 0.75rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 1rem;
    }
    
    .scenario-container {
        background: white;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border: 1px solid #e5e7eb;
    }
    
    .scenario-header {
        padding: 1.5rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #e5e7eb;
    }
    
    .scenario-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: #0A5AA5;
        margin: 0;
    }
    
    .status-badge {
        display: inline-flex;
        padding: 0.75rem 1.5rem;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.95rem;
        text-transform: uppercase;
    }
    .status-aprovado { background: #0A5AA5; color: white; }
    .status-reprovado { background: #FF6C12; color: white; }
    .status-pendente { background: #f1f5f9; color: #0A5AA5; border: 2px solid #0A5AA5; }
    
    .info-section {
        padding: 1.5rem 2rem;
        background: #f8fafc;
    }
    .info-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2rem;
    }
    .info-item { display: flex; flex-direction: column; gap: 0.5rem; }
    .info-label {
        font-size: 0.75rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .info-value {
        font-size: 1.25rem;
        font-weight: 700;
        color: #111827;
    }
    
    .files-section { padding: 1.5rem 2rem; background: white; }
    .files-label {
        font-size: 0.75rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.75rem;
    }
    .files-message {
        background: #fff7ed;
        padding: 1rem 1.25rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        color: #9a3412;
        font-weight: 600;
        border-left: 3px solid #FF6C12;
    }
    
    .file-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #f8fafc;
        padding: 1rem 1.25rem;
        border-radius: 10px;
        margin-bottom: 0.75rem;
        border: 1px solid #e5e7eb;
    }
    .file-name { font-weight: 600; color: #111827; font-size: 1rem; flex: 1; }
    
    .section-divider { margin: 1.5rem 2rem; border-top: 2px solid #e5e7eb; }
    
    .form-section {
        padding: 2rem;
        background: white;
        border-top: 3px solid #0A5AA5;
    }
    .form-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #0A5AA5;
        margin: 0 0 0.5rem 0;
    }
    .form-message { color: #64748b; font-size: 0.9rem; margin: 0; }
    
    .stButton > button {
        border-radius: 10px;
        font-weight: 700;
        font-size: 1rem;
        padding: 0.875rem 2rem;
    }
    .stButton > button[kind="primary"] {
        background: #0A5AA5;
        color: white;
        border: none;
        height: 52px;
    }
    .stButton > button[kind="secondary"] {
        background: white;
        color: #FF6C12;
        border: 2px solid #FF6C12;
    }
    .stButton > button[kind="tertiary"] {
        background: white;
        color: #64748b;
        border: 2px solid #e5e7eb;
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        border-radius: 10px;
        border: 2px solid #e5e7eb;
        background: white;
        font-size: 1rem;
        height: 52px;
    }
    
    .stExpander {
        border: none;
        border-radius: 16px;
        margin-bottom: 1rem;
        background: transparent;
    }
    
    label { font-size: 0.95rem; font-weight: 600; color: #111827; }
    h3, h4 { font-size: 1.3rem; font-weight: 700; color: #111827; }
</style>
""", unsafe_allow_html=True)

# ... (o resto do código continua igual - funções e lógica principal) ...
