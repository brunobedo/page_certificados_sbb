# Certificados SBB 2025

Página para consulta e download de certificados de **Associados da Sociedade Brasileira de Biomecânica** (2025). O usuário informa primeiro e último nome e obtém o link do certificado quando houver correspondência.

## Como rodar

```bash
pip install -r requiments.txt
streamlit run app.py
```

Abra no navegador o endereço indicado (em geral `http://localhost:8501`).

## Estrutura

| Arquivo | Descrição |
|--------|------------|
| `app.py` | Aplicação Streamlit (busca por nome e exibe link do certificado). |
| `certificados.json` | Mapeamento `nome_do_arquivo` → `url` (um por linha; não versionado se contiver dados sensíveis). |
| `drive_list_files.py` | Script opcional para preencher `certificados.json` a partir de uma pasta do Google Drive (requer API e credenciais). |
| `DRIVE_APPS_SCRIPT.md` | Instruções e script para listar arquivos de uma pasta do Drive via Google Apps Script (sem Python). |

## Requisitos

- Python 3.10+
- Dependências em `requiments.txt` (principal: `streamlit`).

Para usar `drive_list_files.py`, é necessário configurar o Google Drive API e ter um arquivo `credentials.json` na pasta do projeto (detalhes no próprio script).

## Licença

Uso interno / Sociedade Brasileira de Biomecânica.
