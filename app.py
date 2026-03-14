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
st.set_page_config(
    page_title="Certificados SBB - Ano 2025",
    page_icon="✓",
    layout="centered"
)

st.markdown(
    """
    <style>
        :root {
            --sbb-dark: #016131;
            --sbb-green: #1ecc42;
            --sbb-soft: #eef7f1;
            --sbb-soft-2: #f7fbf8;
            --text-main: #111111;
            --text-soft: #4b5563;
            --line-soft: rgba(1, 97, 49, 0.14);
        }

        html, body, .main, [data-testid="stAppViewContainer"],
        [data-testid="stAppViewBlockContainer"], [data-testid="stDecoration"] {
            background: linear-gradient(180deg, #f3faf5 0%, #ffffff 34%, #ffffff 100%) !important;
            color: var(--text-main) !important;
        }

        .block-container {
            max-width: 860px;
            padding-top: 0rem;
            padding-bottom: 2.5rem;
        }

        /* remove aparência de containers padrão */
        [data-testid="stForm"] {
            border: none !important;
            background: transparent !important;
            padding: 0 !important;
        }

        /* HERO */
        .hero {
            position: relative;
            overflow: hidden;
            margin-top: 0.8rem;
            margin-bottom: 2.2rem;
            padding: 2.4rem 2rem 2.1rem 2rem;
            border-radius: 24px;
            background:
                radial-gradient(circle at top right, rgba(30, 204, 66, 0.14), transparent 28%),
                radial-gradient(circle at left center, rgba(1, 97, 49, 0.10), transparent 24%),
                linear-gradient(135deg, #016131 0%, #0b7a42 58%, #14914f 100%);
            box-shadow: 0 18px 50px rgba(1, 97, 49, 0.18);
        }

        .hero::after {
            content: "";
            position: absolute;
            inset: 0;
            background:
                linear-gradient(90deg, rgba(255,255,255,0.08) 1px, transparent 1px),
                linear-gradient(180deg, rgba(255,255,255,0.06) 1px, transparent 1px);
            background-size: 28px 28px;
            opacity: 0.15;
            pointer-events: none;
        }

        .hero-content {
            position: relative;
            z-index: 2;
            text-align: center;
        }

        .hero-kicker {
            display: inline-block;
            padding: 0.38rem 0.95rem;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.14);
            border: 1px solid rgba(255, 255, 255, 0.18);
            color: #ffffff;
            font-size: 0.84rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 1rem;
            backdrop-filter: blur(4px);
        }

        .hero-title {
            color: #ffffff;
            font-size: 2.45rem;
            line-height: 1.08;
            font-weight: 800;
            letter-spacing: -0.02em;
            margin-bottom: 0.7rem;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        .hero-subtitle {
            max-width: 660px;
            margin: 0 auto;
            color: rgba(255,255,255,0.92);
            font-size: 1.03rem;
            line-height: 1.6;
            font-weight: 400;
        }

        /* CONTEÚDO PRINCIPAL */
        .section-wrap {
            padding: 0 0.15rem;
        }

        .section-header {
            text-align: center;
            margin-bottom: 1.2rem;
        }

        .section-title {
            color: var(--sbb-dark);
            font-size: 1.2rem;
            font-weight: 750;
            letter-spacing: -0.01em;
            margin-bottom: 0.2rem;
        }

        .section-text {
            color: var(--text-soft);
            font-size: 0.98rem;
            line-height: 1.55;
        }

        /* Inputs */
        .stTextInput label {
            font-weight: 650 !important;
            color: #173324 !important;
            margin-bottom: 0.28rem !important;
        }

        .stTextInput > div > div > input {
            background: #ffffff !important;
            border: 1.3px solid #d6e8dc !important;
            border-radius: 14px !important;
            color: #111111 !important;
            min-height: 48px;
            padding-left: 0.95rem !important;
            transition: all 0.2s ease;
            box-shadow: none !important;
        }

        .stTextInput > div > div > input:hover {
            border-color: #b8d8c3 !important;
        }

        .stTextInput > div > div > input:focus {
            border-color: var(--sbb-green) !important;
            box-shadow: 0 0 0 4px rgba(30, 204, 66, 0.14) !important;
        }

        /* botão */
        [data-testid="stFormSubmitButton"] button,
        [data-testid="stButton"] button {
            min-height: 50px;
            border-radius: 14px !important;
            border: 1px solid var(--sbb-dark) !important;
            background: var(--sbb-dark) !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 8px 18px rgba(1, 97, 49, 0.14);
        }

        [data-testid="stFormSubmitButton"] button:hover,
        [data-testid="stButton"] button:hover {
            background: #014b27 !important;
            border-color: #014b27 !important;
            transform: translateY(-1px);
            box-shadow: 0 12px 24px rgba(1, 97, 49, 0.18);
        }

        /* mensagens */
        .result-box {
            margin-top: 1.2rem;
            padding: 1rem 1.1rem;
            border-radius: 16px;
            text-align: center;
            line-height: 1.55;
            font-size: 0.98rem;
        }

        .result-ok {
            background: #f2fcf5;
            border: 1px solid rgba(30, 204, 66, 0.32);
            color: var(--sbb-dark);
        }

        .result-none {
            background: #f8faf8;
            border: 1px solid #dde5df;
            color: #374151;
        }

        .filename {
            display: inline-block;
            margin-top: 0.35rem;
            color: #0f5132;
            font-weight: 700;
        }

        .helper-line {
            margin-top: 1.4rem;
            padding-top: 1rem;
            border-top: 1px solid var(--line-soft);
            text-align: center;
            color: #5f6d65;
            font-size: 0.92rem;
            line-height: 1.6;
        }

        .foot {
            text-align: center;
            font-size: 0.88rem;
            color: #6b7280;
            margin-top: 2.3rem;
            padding-top: 0.4rem;
        }

        @media (max-width: 640px) {
            .block-container {
                padding-top: 0rem;
            }

            .hero {
                padding: 2rem 1.2rem 1.8rem 1.2rem;
                border-radius: 20px;
                margin-bottom: 1.8rem;
            }

            .hero-title {
                font-size: 1.85rem;
            }

            .hero-subtitle {
                font-size: 0.97rem;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <div class="hero-content">
            <div class="hero-kicker">Sociedade Brasileira de Biomecânica</div>
            <div class="hero-title">Certificados de Associação 2025</div>
            <div class="hero-subtitle">
                Consulte seu certificado de associado de forma rápida e segura.
                <br>Informe seus dados para localizar o documento cadastrado.<br>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

_mtime = MANIFEST_PATH.stat().st_mtime if MANIFEST_PATH.exists() else 0.0
manifest = load_manifest(MANIFEST_PATH, _mtime)

st.markdown('<div class="section-wrap">', unsafe_allow_html=True)
st.markdown(
    """
    <div class="section-header">
        <div class="section-title">Buscar certificado</div>
        <div class="section-text">Informe o primeiro nome e o último sobrenome cadastrados.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("certificate_search_form"):
    col1, col2 = st.columns(2)

    with col1:
        first_name = st.text_input("Primeiro nome", placeholder="Ex.: João")

    with col2:
        last_name = st.text_input("Último sobrenome", placeholder="Ex.: Silva")

    submitted = st.form_submit_button("Buscar certificado", use_container_width=True)

if submitted:
    if not first_name.strip() or not last_name.strip():
        st.markdown(
            """
            <div class="result-box result-none">
                Preencha o primeiro nome e o último sobrenome para continuar.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        filename, certificate_url = find_certificate_url(first_name, last_name, manifest)

        if certificate_url:
            st.markdown(
                f"""
                <div class="result-box result-ok">
                    Certificado localizado com sucesso.
                    <br>
                        Clique no botão abaixo para abrir o certificado.
                    <br>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.link_button("Abrir certificado", certificate_url, use_container_width=True)
        else:
            st.markdown(
                """
                <div class="result-box result-none">
                    Nenhum certificado foi encontrado para os dados informados.
                    Revise a digitação e tente novamente.
                    <br>Se o problema persistir, entre em contato com a SBB.<br>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.markdown(
    """
    <div class="helper-line">
        Dica: em nomes compostos ou com preposições, tente buscar pelo primeiro nome e pelo último sobrenome
        cadastrado.  <br>Ex.: <em>Ana Maria da Silva Coutinho</em> → <em>Ana</em> <em>Coutinho</em>. <br>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    '<div class="foot">© Sociedade Brasileira de Biomecânica · Associação 2025</div>',
    unsafe_allow_html=True,
)