import html
import json
import re
import unicodedata
from pathlib import Path
from typing import Optional
import streamlit as st

SCRIPT_DIR = Path(__file__).resolve().parent

# Atualize esta data sempre que os manifestos de certificados forem atualizados.
LAST_UPDATE = "09/11/2026"

YEAR_CONFIG = {
    "2025": {
        "manifest": SCRIPT_DIR / "certificados25.json",
        "suffix": "certificado_sbb_2025.png",
    },
    "2026": {
        "manifest": SCRIPT_DIR / "certificados26.json",
        "suffix": "certificado_sbb_2026.png",
    },
}


def normalize_name(value: str) -> str:
    if value is None:
        return ""
    value = unicodedata.normalize("NFD", value)
    value = "".join(ch for ch in value if unicodedata.category(ch) != "Mn")
    value = value.lower().strip()
    value = re.sub(r"\s+", "_", value)
    value = re.sub(r"[^a-z0-9_]", "", value)
    return value


def normalize_cpf_prefix(value: str) -> str:
    """Mantém apenas dígitos do valor informado (ex.: '123' -> '123')."""
    return re.sub(r"\D", "", value or "")


def build_filename(last_name: str, cpf_prefix: str, suffix: str) -> str:
    # Os arquivos seguem o padrão: sobrenome_XXX_certificado_sbb_ANO.ext,
    # onde XXX são os 3 primeiros dígitos do CPF.
    last = normalize_name(last_name)
    cpf = normalize_cpf_prefix(cpf_prefix)
    return f"{last}_{cpf}_{suffix}"


@st.cache_data
def load_manifest(path: Path, _mtime: float) -> dict:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def find_certificate_url(
    last_name: str, cpf_prefix: str, manifest: dict, suffix: str
) -> tuple[str, Optional[str]]:
    filename = build_filename(last_name, cpf_prefix, suffix)
    stem = filename[:-4] if filename.endswith(".png") else filename

    # O manifesto pode ter a extensão .png ou .pdf
    for candidate in (filename, stem, stem + ".png", stem + ".pdf"):
        url = manifest.get(candidate)
        if url:
            return filename, url

    return filename, None


# === PAGE ===
st.set_page_config(
    page_title="Certificados SBB",
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

        .hero-updated {
            display: inline-block;
            margin-top: 1.2rem;
            padding: 0.35rem 0.9rem;
            border-radius: 999px;
            background: rgba(0, 0, 0, 0.16);
            border: 1px solid rgba(255, 255, 255, 0.18);
            color: rgba(255, 255, 255, 0.92);
            font-size: 0.84rem;
            letter-spacing: 0.02em;
        }

        .hero-updated strong {
            color: #ffffff;
        }

        .year-picker-wrap {
            width: 100%;
            margin-bottom: 0 !important;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .year-prompt {
            color: #111111;
            font-size: 0.98rem;
            margin: 0 0 0.75rem 0;
            font-weight: 500;
            letter-spacing: -0.01em;
            text-align: center;
        }

        [data-testid="stElementContainer"]:has([data-testid="stHorizontalBlock"]:has(#year-picker-start)) {
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }

        [data-testid="stHorizontalBlock"]:has(#year-picker-start) {
            width: 100% !important;
            gap: 0 !important;
            margin: 0 auto !important;
            transform: translateX(10px);
        }

        [data-testid="stHorizontalBlock"]:has(#year-picker-start) > [data-testid="column"]:nth-child(2) {
            display: flex !important;
            justify-content: flex-end !important;
            align-items: center !important;
        }

        [data-testid="stHorizontalBlock"]:has(#year-picker-start) > [data-testid="column"]:nth-child(3) {
            margin-left: 1.5rem !important;
            display: flex !important;
            justify-content: flex-start !important;
            align-items: center !important;
        }

        [data-testid="stHorizontalBlock"]:has(#year-picker-start) > [data-testid="column"]:nth-child(2),
        [data-testid="stHorizontalBlock"]:has(#year-picker-start) > [data-testid="column"]:nth-child(3) {
            width: auto !important;
            flex: 0 0 auto !important;
            min-width: 0 !important;
            padding: 0 !important;
        }

        [data-testid="stElementContainer"]:has(#year-picker-bridge) {
            margin-top: -0.5rem !important;
            margin-bottom: 0 !important;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }

        .year-bridge .section-wrap {
            padding: 0 0.15rem;
            margin-top: 0 !important;
        }

        .year-bridge .section-header {
            text-align: center;
            margin-bottom: 0.85rem;
            margin-top: 0 !important;
            padding-top: 0 !important;
        }

        .year-bridge .section-title {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }

        [data-testid="stHorizontalBlock"]:has(#year-picker-start) [data-testid="stButton"] {
            display: flex;
            justify-content: center;
            margin-bottom: 0 !important;
        }

        [data-testid="stHorizontalBlock"]:has(#year-picker-start) [data-testid="stButton"] button {
            border-radius: 8px !important;
            padding: 0.3rem 0.75rem !important;
            font-weight: 700 !important;
            font-size: 0.95rem !important;
            letter-spacing: 0.02em;
            min-width: 64px !important;
            min-height: 34px !important;
            box-shadow: none !important;
            transition: background 0.2s ease, border-color 0.2s ease !important;
        }

        [data-testid="stHorizontalBlock"]:has(#year-picker-start) [data-testid="stButton"] button[kind="secondary"],
        [data-testid="stHorizontalBlock"]:has(#year-picker-start) [data-testid="stButton"] button[data-testid="baseButton-secondary"] {
            background: #ebebeb !important;
            border: 1.5px solid #111111 !important;
            color: #111111 !important;
        }

        [data-testid="stHorizontalBlock"]:has(#year-picker-start) [data-testid="stButton"] button[kind="secondary"]:hover,
        [data-testid="stHorizontalBlock"]:has(#year-picker-start) [data-testid="stButton"] button[data-testid="baseButton-secondary"]:hover {
            background: #e0e0e0 !important;
            border-color: #111111 !important;
            color: #111111 !important;
        }

        [data-testid="stHorizontalBlock"]:has(#year-picker-start) [data-testid="stButton"] button[kind="primary"],
        [data-testid="stHorizontalBlock"]:has(#year-picker-start) [data-testid="stButton"] button[data-testid="baseButton-primary"] {
            background: #c8e6c9 !important;
            border: 1.5px solid #4caf50 !important;
            color: #1b5e20 !important;
        }

        [data-testid="stHorizontalBlock"]:has(#year-picker-start) [data-testid="stButton"] button[kind="primary"]:hover,
        [data-testid="stHorizontalBlock"]:has(#year-picker-start) [data-testid="stButton"] button[data-testid="baseButton-primary"]:hover {
            background: #b9dfbb !important;
            border-color: #43a047 !important;
            color: #1b5e20 !important;
        }

        [data-testid="stHorizontalBlock"]:has(#year-picker-start) [data-testid="stButton"] button:focus {
            box-shadow: none !important;
            outline: none !important;
        }

        /* CONTEÚDO PRINCIPAL */
        .section-wrap {
            padding: 0 0.15rem;
        }

        .section-header {
            text-align: center;
            margin-bottom: 0.85rem;
            margin-top: 0 !important;
            padding-top: 0 !important;
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

        /* wrapper do baseweb: evita fundo/borda escuros do tema e cantos pretos */
        .stTextInput [data-baseweb="input"],
        .stTextInput [data-baseweb="base-input"] {
            background: #ffffff !important;
            border: none !important;
            border-radius: 14px !important;
            color-scheme: light;
            min-height: 48px !important;
            height: auto !important;
            overflow: visible !important;
        }

        .stTextInput [data-baseweb="input"] > div,
        .stTextInput [data-baseweb="base-input"] {
            min-height: 48px !important;
            height: auto !important;
        }

        .stTextInput input {
            box-sizing: border-box !important;
            height: 48px !important;
        }

        /* autofill do navegador (deixava um campo escuro) */
        .stTextInput input:-webkit-autofill,
        .stTextInput input:-webkit-autofill:hover,
        .stTextInput input:-webkit-autofill:focus {
            -webkit-box-shadow: 0 0 0 1000px #ffffff inset !important;
            -webkit-text-fill-color: #111111 !important;
            caret-color: #111111 !important;
            border-radius: 14px !important;
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
        [data-testid="stElementContainer"]:not(:has(#year-picker-start)) [data-testid="stButton"] button {
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
        [data-testid="stElementContainer"]:not(:has(#year-picker-start)) [data-testid="stButton"] button:hover {
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

        .ok-card {
            display: flex;
            align-items: flex-start;
            gap: 1rem;
            margin: 1.2rem 0 0.9rem 0;
            padding: 1.3rem 1.5rem;
            border-radius: 16px;
            background: #ffffff;
            border: 1px solid rgba(30, 204, 66, 0.35);
            border-left: 5px solid var(--sbb-green);
            box-shadow: 0 8px 24px rgba(1, 97, 49, 0.08);
            text-align: left;
        }

        .ok-badge {
            flex: 0 0 auto;
            width: 38px;
            height: 38px;
            border-radius: 50%;
            background: var(--sbb-dark);
            color: #ffffff;
            font-size: 1.2rem;
            font-weight: 800;
            line-height: 38px;
            text-align: center;
        }

        .ok-title {
            color: var(--sbb-dark);
            font-size: 1.15rem;
            font-weight: 750;
            margin-bottom: 0.2rem;
        }

        .ok-text {
            color: var(--text-soft);
            font-size: 0.97rem;
            line-height: 1.6;
        }

        [data-testid="stLinkButton"] a {
            min-height: 50px;
            border-radius: 14px !important;
            border: 1px solid var(--sbb-dark) !important;
            background: var(--sbb-dark) !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 8px 18px rgba(1, 97, 49, 0.14);
        }

        [data-testid="stLinkButton"] a:hover {
            background: #014b27 !important;
            border-color: #014b27 !important;
            transform: translateY(-1px);
        }

        [data-testid="stLinkButton"] a * {
            color: #ffffff !important;
        }

        .nf-card {
            margin-top: 1.2rem;
            padding: 1.5rem 1.5rem 1.3rem 1.5rem;
            border-radius: 16px;
            background: #ffffff;
            border: 1px solid #dde5df;
            box-shadow: 0 8px 24px rgba(1, 97, 49, 0.07);
            text-align: left;
            color: #374151;
            font-size: 0.97rem;
            line-height: 1.6;
        }

        .nf-title {
            color: #c62828;
            font-size: 1.15rem;
            font-weight: 750;
            margin-bottom: 0.3rem;
        }

        .nf-text {
            color: var(--text-soft);
            margin: 0.2rem 0;
        }

        .nf-data {
            margin: 0.9rem 0 1.1rem 0;
            border: 1px solid #e3ece6;
            border-radius: 12px;
            background: var(--sbb-soft-2);
            overflow: hidden;
        }

        .nf-row {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            padding: 0.65rem 1rem;
            border-bottom: 1px solid #e3ece6;
        }

        .nf-row:last-child {
            border-bottom: none;
        }

        .nf-label {
            color: #5f6d65;
            font-size: 0.9rem;
        }

        .nf-value {
            color: #111111;
            font-weight: 650;
            text-align: right;
            word-break: break-word;
        }

        .nf-notice {
            margin: 0 0 1rem 0;
            padding: 0.9rem 1.1rem;
            border-radius: 12px;
            background: #fff8e1;
            border: 1px solid #f2d27a;
            border-left: 5px solid #e0a800;
            color: #5c4300;
            font-weight: 600;
        }

        .nf-notice-title {
            font-size: 0.78rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            font-weight: 800;
            margin-bottom: 0.2rem;
        }

        .nf-notice a {
            color: #5c4300;
            font-weight: 800;
        }

        .nf-contact {
            margin-top: 0.8rem;
            padding-top: 0.8rem;
            border-top: 1px solid var(--line-soft);
            font-size: 0.92rem;
            color: #5f6d65;
        }

        .nf-contact a {
            color: var(--sbb-dark);
            font-weight: 650;
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
    f"""
    <div class="hero">
        <div class="hero-content">
            <div class="hero-kicker">Sociedade Brasileira de Biomecânica</div>
            <div class="hero-title">Certificados de Associação</div>
            <div class="hero-subtitle">
                Consulte seu certificado de associado de forma rápida e segura.
                <br>Informe seus dados para localizar o documento cadastrado.
            </div>
            <div class="hero-updated">Última atualização: <strong>{LAST_UPDATE}</strong></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="year-picker-wrap">', unsafe_allow_html=True)
st.markdown(
    '<p class="year-prompt">Escolha o ano que você quer emitir o seu certificado</p>',
    unsafe_allow_html=True,
)

def _set_year(year: str) -> None:
    st.session_state.selected_year = year


if "selected_year" not in st.session_state:
    st.session_state.selected_year = "2025"

selected_year = st.session_state.selected_year

col_left, col_2025, col_2026, col_right = st.columns([2.35, 1, 1, 1.95], gap="small")
with col_left:
    st.markdown('<span id="year-picker-start"></span>', unsafe_allow_html=True)
with col_2025:
    st.button(
        "2025",
        type="primary" if selected_year == "2025" else "secondary",
        key="year_btn_2025",
        on_click=_set_year,
        args=("2025",),
    )
with col_2026:
    st.button(
        "2026",
        type="primary" if selected_year == "2026" else "secondary",
        key="year_btn_2026",
        on_click=_set_year,
        args=("2026",),
    )

st.markdown(
    """
    <span id="year-picker-bridge"></span>
    <div class="year-bridge">
        <div class="section-wrap">
            <div class="section-header">
                <div class="section-title" style="color:#111111;text-align:center;">Informações para emitir o certificado</div>
                <div class="section-text" style="color:#111111;text-align:center;">Informe o primeiro nome, o último sobrenome e os 3 primeiros dígitos do CPF cadastrados.</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)

year_cfg = YEAR_CONFIG[selected_year]
suffix = year_cfg["suffix"]

manifests = {}
for year, cfg in YEAR_CONFIG.items():
    path = cfg["manifest"]
    mtime = path.stat().st_mtime if path.exists() else 0.0
    manifests[year] = load_manifest(path, mtime)
manifest = manifests[selected_year]


with st.form("certificate_search_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        first_name = st.text_input("Primeiro nome", placeholder="Ex.: João")

    with col2:
        last_name = st.text_input("Último sobrenome", placeholder="Ex.: Silva")

    with col3:
        cpf_prefix = st.text_input(
            "3 primeiros dígitos do CPF", placeholder="Ex.: 123", max_chars=3
        )

    submitted = st.form_submit_button("Buscar certificado", use_container_width=True)

st.markdown(
    """
    <div class="helper-line">
        Dica: em nomes compostos ou com preposições, tente buscar pelo primeiro nome e pelo último sobrenome
        cadastrado.<br>Ex.: <em>Ana Maria da Silva Coutinho</em> → <em>Ana Coutinho</em>.
    </div>
    """,
    unsafe_allow_html=True,
)

if submitted:
    cpf_digits = normalize_cpf_prefix(cpf_prefix)
    if not first_name.strip() or not last_name.strip() or not cpf_prefix.strip():
        st.markdown(
            """
            <div class="result-box result-none">
                Preencha o primeiro nome, o último sobrenome e os 3 primeiros dígitos do CPF para continuar.
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif len(cpf_digits) != 3:
        st.markdown(
            """
            <div class="result-box result-none">
                Informe exatamente os 3 primeiros dígitos do CPF (apenas números).
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        filename, certificate_url = find_certificate_url(last_name, cpf_digits, manifest, suffix)

        if certificate_url:
            st.markdown(
                f"""
                <div class="ok-card">
                    <div class="ok-badge">✓</div>
                    <div class="ok-body">
                        <div class="ok-title">Certificado localizado</div>
                        <div class="ok-text">
                            Encontramos o certificado de associado de
                            <strong>{html.escape(first_name.strip())} {html.escape(last_name.strip())}</strong>
                            referente a {selected_year}. Utilize o botão abaixo para abri-lo e, se desejar, salvá-lo ou imprimi-lo.
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.link_button("Abrir certificado", certificate_url, use_container_width=True, type="primary")
        else:
            st.markdown(
                f"""
                <div class="nf-card">
                    <div class="nf-title">Certificado não localizado</div>
                    <div class="nf-text">Não encontramos um certificado para os dados informados. Confira se estão corretos:</div>
                    <div class="nf-data">
                        <div class="nf-row"><span class="nf-label">Nome</span><span class="nf-value">{html.escape(first_name.strip())}</span></div>
                        <div class="nf-row"><span class="nf-label">Sobrenome</span><span class="nf-value">{html.escape(last_name.strip())}</span></div>
                        <div class="nf-row"><span class="nf-label">3 primeiros dígitos do CPF</span><span class="nf-value">{html.escape(cpf_digits)}</span></div>
                    </div>
                    <div class="nf-notice">
                        <div class="nf-notice-title">Importante</div>
                        Os certificados são emitidos somente após o pagamento da associação, realizado em
                        <a href="https://bsb.org.br/" target="_blank" rel="noopener noreferrer">bsb.org.br</a>.
                    </div>
                    <div class="nf-text">Após o pagamento, a emissão dos certificados é atualizada periodicamente pelo sistema.</div>
                    <div class="nf-contact">Dúvidas: <a href="mailto:soc.bras.biomecanica@gmail.com">soc.bras.biomecanica@gmail.com</a></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    '<div class="foot">© Sociedade Brasileira de Biomecânica</div>',
    unsafe_allow_html=True,
)