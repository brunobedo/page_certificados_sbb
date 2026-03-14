import json
import re
import unicodedata
from pathlib import Path
from typing import Optional
import streamlit as st

EXPECTED_SUFFIX = "certificado_sbb_2025.png"
MANIFEST_PATH = Path(__file__).resolve().parent / "certificados.json"

def normalize_name(value: str) -> str:
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
def load_manifest(path: Path, _mtime: float) -> dict:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def find_certificate_url(first_name: str, last_name: str, manifest: dict) -> tuple[str, Optional[str]]:
    filename = build_filename(first_name, last_name)
    url = manifest.get(filename)
    if url is None and filename.endswith(".png"):
        url = manifest.get(filename[:-4])
    elif url is None:
        url = manifest.get(filename + ".png")
    return filename, url

# === PAGE ===
st.set_page_config(page_title="Certificados SBB 2025", page_icon="✓", layout="centered")

st.markdown(
    """
    <style>
        html, body, .main, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"], [data-testid="stDecoration"] {
            background: #fff !important;
            color: #111 !important;
        }
        .block-container {
            background: #fff;
        }
        .highlight-sbb {
            font-family: system-ui, -apple-system, sans-serif;
            font-weight: 900;
            font-size: 2.2rem;
            color: #016131;
            letter-spacing: 0.03em;
            background: #e6f3ea;
            border-radius: 10px;
            margin-bottom: 0.2rem;
            text-align: center;
            margin-top: 1.0rem;
            padding: 0.5rem 1rem 0.3rem 1rem;
            text-shadow: 0 2px 2px rgba(1,97,49,0.04);
            border: 2.5px solid #01613122;
        }
        .cert-ano {
            text-align: center;
            color: #1ecc42;
            font-size: 1.15rem;
            font-weight: 700;
            letter-spacing: 1px;
            background: #f4fcf8;
            border-radius: 7px;
            margin-bottom: 0.8rem;
            margin-top: 0.20rem;
            padding: 0.3rem 1rem 0.3rem 1rem;
            border: 1.5px solid #1ecc4235;
            text-shadow: 0 1px 1px #fff0;
        }
        .subtitle {
            font-size: 1rem;
            color: #141f1a;
            text-align: center;
            margin-bottom: 1.3rem;
            font-weight: 500;
            letter-spacing: 0.5px;
        }
        .stTextInput>div>div>input {
            background: #fff !important;
            border: 1.7px solid #016131 !important;
            border-radius: 10px;
            color: #111;
        }
        .stTextInput>div>div>input:focus {
            border-color: #1ecc42 !important;
            box-shadow: 0 0 0 1.5px #01613170 !important;
            color: #111 !important;
        }
        [data-testid="stButton"] button {
            background: #016131 !important;
            color: #fff !important;
            font-weight: 700;
            border-radius: 9px;
            border: 2px solid #111;
        }
        [data-testid="stButton"] button:hover {
            background: #111 !important;
            color: #1ecc42 !important;
            border: 2px solid #1ecc42;
        }
        .msg {
            font-size: 1.05rem;
            font-weight: 500;
            padding: 0.9rem 1.1rem;
            border-radius: 8px;
            margin: 0.7rem 0;
            text-align: center;
        }
        .msg-ok {
            background: #f0fdf4;
            color: #016131;
            border: 1.8px solid #22c55e;
        }
        .msg-none {
            background: #e5e7eb;
            color: #1f2937;
            border: 1.6px solid #222827;
        }
        .foot {
            text-align: center;
            font-size: 0.92rem;
            color: #111;
            margin-top: 2.8rem;
            font-weight: 400;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="highlight-sbb">Sociedade Brasileira de Biomecânica</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="cert-ano">Certificados de Associação · Ano 2025</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitle">Consulte e baixe seu certificado de associado à Sociedade Brasileira de Biomecânica.</div>',
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)
with col1:
    first_name = st.text_input("Primeiro nome", placeholder="Ex.: Maria")
with col2:
    last_name = st.text_input("Último nome", placeholder="Ex.: Silva")

_mtime = MANIFEST_PATH.stat().st_mtime if MANIFEST_PATH.exists() else 0.0
manifest = load_manifest(MANIFEST_PATH, _mtime)

if st.button("Buscar", use_container_width=True):
    if not first_name.strip() or not last_name.strip():
        st.error("Preencha primeiro e último nome.")
    else:
        _, certificate_url = find_certificate_url(first_name, last_name, manifest)
        if certificate_url:
            st.markdown(
                '<div class="msg msg-ok">Certificado encontrado.<br>Use o botão abaixo para acessar.</div>',
                unsafe_allow_html=True,
            )
            st.link_button("Abrir certificado", certificate_url, use_container_width=True)
        else:
            st.markdown(
                '<div class="msg msg-none">Nenhum certificado encontrado para esse nome.<br>Verifique os dados ou entre em contato com a SBB.</div>',
                unsafe_allow_html=True,
            )

st.markdown('<div class="foot">© Sociedade Brasileira de Biomecânica · Associação 2025</div>', unsafe_allow_html=True)
