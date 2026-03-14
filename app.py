import json
import re
import unicodedata
from pathlib import Path
from typing import Optional
import streamlit as st

EXPECTED_SUFFIX = "certificado_sbb_2025"
# Caminho do manifest na mesma pasta do app.py (funciona mesmo rodando de outro diretório)
MANIFEST_PATH = Path(__file__).resolve().parent / "certificados.json"
DRIVE_FOLDER_URL = "https://drive.google.com/drive/folders/1hxzbqFqY3BRKIeVjFgAoIRKc6UyXyGjq?usp=drive_link"

def normalize_name(value: str) -> str:
    """Normaliza texto para o padrão esperado nos arquivos."""
    if value is None:
        return ""
    value = unicodedata.normalize("NFD", value)
    value = "".join(ch for ch in value if unicodedata.category(ch) != "Mn")
    value = value.lower().strip()
    value = re.sub(r"\s+", "_", value)
    value = re.sub(r"[^a-z0-9_]", "", value)
    return value

def build_filename(first_name: str, last_name: str) -> str:
    first = normalize_name(first_name)
    last = normalize_name(last_name)
    return f"{first}_{last}_{EXPECTED_SUFFIX}"

@st.cache_data
def load_manifest(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def find_certificate_url(first_name: str, last_name: str, manifest: dict) -> tuple[str, Optional[str]]:
    filename = build_filename(first_name, last_name)
    return filename, manifest.get(filename)

# === PAGE SETTINGS & STYLES ===
st.set_page_config(
    page_title="Certificados SBB 2025",
    page_icon=":white_check_mark:",
    layout="centered",
)
st.markdown(
    """
    <style>
        html, body, .main {
            background: #f8fbf7 !important;
        }
        .main-title {
            font-family: 'Inter', 'Montserrat', Arial, sans-serif;
            font-weight: bold;
            font-size: 2.4em;
            letter-spacing: -.016em;
            color: #218c39;
            text-align: center;
            margin-top: 0.1em;
            margin-bottom: 0.15em;
        }
        .sub-title {
            color: #48a063;
            text-align: center;
            font-size: 1.1em;
            margin-top: -0.7em;
            margin-bottom: 1.2em;
        }
        ul.fancy-list {
            color: #4b6f52;
            font-size: 1em;
            margin-top: -5px;
        }
        .stTextInput>div>div>input {
            background: #fff;
            border: 1.6px solid #b4e3bf;
            border-radius: 6.5px;
            font-size: 1.07em;
            color: #217249;
            font-weight: 400;
        }
        .divider {
            height: 2px;
            background: linear-gradient(90deg, #aef2be 0%, #e8feee 40%);
            border: none;
            margin-top: 16px;
            margin-bottom: 18px;
        }
        .info-file {
            color: #37a86c;
            background: #e6f8ec;
            border-radius: 5px;
            padding: 0.5em 0.95em 0.5em 0.7em;
            font-weight: 500;
            font-size: 1.04em;
            font-family: Menlo, "Fira Mono", monaco, monospace;
            display: inline-block;
            border-left: 3.7px solid #28cd71;
        }
        .success-badge {
            background: #e2f9e1;
            color: #2d8a53;
            border: none;
            border-radius: .74em;
            padding: 1.0em 0.9em 0.85em 1.05em;
            margin-bottom: 14px;
            font-size: 1.11em;
            box-shadow: 0 2px 16px #52db8540;
        }
        .warn-badge {
            background: #fbffe7;
            color: #6a824e;
            border: none;
            border-radius: .8em;
            padding: 1.0em 1.0em 0.85em 1.05em;
            margin-bottom: 15px;
            font-size: 1.06em;
            box-shadow: 0 2px 12px #c6e7b64d;
        }
        .expander-content {
            background: #f5fcf2;
            border-radius: 7px;
            padding: 1.1em 1.3em;
            color: #18833e;
            font-size: 1.02em;
            border-left: 2.4px solid #aef2be;
        }
        code, .expander-content code {
            background: #e4faee;
            color: #1c925f;
            border-radius: 4.5px;
            padding: 0.09em 0.5em;
            font-size: .99em;
        }
        a, a:visited { color: #218c39; text-decoration: underline dotted; }
        .st-emotion-cache-1y4p8pa, .st-emotion-cache-1c7y2kd { /* st.button */ background: linear-gradient(90deg, #e4faee 10%, #b4e3be 90%) !important; color: #208d42 !important; font-weight: bold !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-title">✅ Certificados</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Encontre e baixe seu certificado de Associados da Sociedade Brasileira de Biomecânica 2025</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Sociedade Brasileira de Biomecânica 2025</div>', unsafe_allow_html=True)

st.write(
    """
    <ul class='fancy-list'>
        <li>Digite <b>primeiro nome</b> e <b>último nome</b> nos campos abaixo.</li>
        <li>Os nomes precisam bater com o padrão dos arquivos salvos <span style="color:#65b078">no Google Drive Verde SBB</span>.</li>
    </ul>
    """,
    unsafe_allow_html=True
)

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        first_name = st.text_input("Primeiro nome", placeholder="Ex.: pedro")
    with col2:
        last_name = st.text_input("Último nome", placeholder="Ex.: silva")

manifest = load_manifest(MANIFEST_PATH)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# Minimal color palette
PRIMARY_COLOR = "#232B2B"  # Charcoal/Dark minimal
SECONDARY_COLOR = "#545E5E"  # Muted gray
ACCENT_COLOR = "#00695C"  # Subtle blue-green

if st.button("Buscar certificado", use_container_width=True):
    if not first_name.strip() or not last_name.strip():
        st.error(
            '<span style="font-family: \'Segoe UI\', Arial, sans-serif; color: %s;">Preencha o <b>primeiro nome</b> e o <b>último nome</b>.</span>'
            % ACCENT_COLOR,
            unsafe_allow_html=True,
        )
    else:
        expected_filename, certificate_url = find_certificate_url(first_name, last_name, manifest)
        st.markdown(
            f'<div class="info-file" style="font-family: \'Segoe UI\', Arial, sans-serif; color:{SECONDARY_COLOR};">📝 Nome do arquivo: <code style="background:#f2f2f2; color:{PRIMARY_COLOR};">{expected_filename}</code></div>',
            unsafe_allow_html=True
        )
        if certificate_url:
            st.markdown(
                f"""
                <div class="success-badge" style="background:#eef4f2; border-left: 4px solid {ACCENT_COLOR}; color:{PRIMARY_COLOR}; font-family: 'Segoe UI', Arial, sans-serif; font-size:1.02em;">
                    <b>Seu certificado foi encontrado!</b><br>
                    <span style="font-size:0.96em">Clique no botão abaixo para acessar ou baixar o arquivo.</span>
                </div>
                """, unsafe_allow_html=True
            )
            st.link_button(
                "Abrir certificado",
                certificate_url,
                use_container_width=True
            )
        else:
            st.markdown(
                f"""
                <div class="warn-badge" style="background:#f8f8f8; border-left: 4px solid #bfbfbf; color:{SECONDARY_COLOR}; font-family: 'Segoe UI', Arial, sans-serif;">
                    <b>Certificado não localizado.</b><br>
                    <span style="font-size:0.96em">Verifique se digitou os nomes corretamente ou entre em contato com a organização.</span>
                </div>
                """, unsafe_allow_html=True
            )

with st.expander("Instruções e detalhes"):
    st.markdown(
        f"""
        <div class="expander-content" style="font-family: 'Segoe UI', Arial, sans-serif; color:{SECONDARY_COLOR}; font-size:1.00em;">
            <b>Nome esperado do arquivo:</b><br>
            <code style="background:#ededed; color:{PRIMARY_COLOR};">primeiro_ultimo_{EXPECTED_SUFFIX}</code>
            <br><br>
            <b>Pasta Drive do evento:</b><br>
            <a style="color:{ACCENT_COLOR}; text-decoration: underline;" href="{DRIVE_FOLDER_URL}" target="_blank">{DRIVE_FOLDER_URL}</a>
            <br><br>
            <b>Sobre este aplicativo:</b>
            <ul>
                <li>O app usa um arquivo <code style="background:#ededed; color:{PRIMARY_COLOR};">certificados.json</code> local para fazer a correspondência com os links do Drive.</li>
                <li style="margin-top:.17em">Se houver dúvidas ou problema na localização, contate a organização do evento.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )
