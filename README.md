# Certificados SBB

Página para consulta e download de certificados de **Associados da Sociedade Brasileira de Biomecânica** (anos 2025 e 2026). O usuário escolhe o ano e informa **primeiro nome, último sobrenome e os 3 primeiros dígitos do CPF**; quando há correspondência, a página exibe o link do certificado.

## Como rodar

```bash
pip install -r requiments.txt
streamlit run app.py
```

Abra no navegador o endereço indicado (em geral `http://localhost:8501`).

## Como a busca funciona

Os certificados são localizados por uma chave no formato:

```
sobrenome_XXX_certificado_sbb_ANO.pdf
```

em que `XXX` são os 3 primeiros dígitos do CPF. A busca usa o **último sobrenome** (acentos e maiúsculas são ignorados; sobrenomes compostos viram `sobrenome1_sobrenome2`) e o **CPF**. O primeiro nome é exigido no formulário, mas **não faz parte da chave**, pois não consta nos nomes dos arquivos.

Se nada for encontrado, a página pede a conferência dos dados informados e lembra que os certificados só são emitidos após o pagamento da associação, que a emissão é atualizada periodicamente e que dúvidas devem ser enviadas para soc.bras.biomecanica@gmail.com.

## Estrutura

| Arquivo | Descrição |
|--------|------------|
| `app.py` | Aplicação Streamlit (busca por sobrenome + 3 primeiros dígitos do CPF e exibe o link do certificado). |
| `certificados25.json` | Mapeamento `nome_do_arquivo` → `url` dos certificados de 2025. |
| `certificados26.json` | Mapeamento `nome_do_arquivo` → `url` dos certificados de 2026. |
| `requiments.txt` | Dependências Python. |
| `.devcontainer/devcontainer.json` | Configuração do dev container. |

## Atualizando os certificados

1. Gere o JSON do ano (`nome_do_arquivo` → `url`) a partir da pasta do Google Drive, por exemplo com um Google Apps Script que liste os arquivos.
2. Substitua `certificados25.json` ou `certificados26.json`.
3. Atualize a constante `LAST_UPDATE` no topo de `app.py`, que alimenta o selo "Última atualização" exibido na página.

Para incluir um novo ano, adicione uma entrada em `YEAR_CONFIG` no `app.py` e o botão correspondente na seleção de ano.

## Requisitos

- Python 3.10+
- Dependências em `requiments.txt` (principal: `streamlit`).

## Licença

Uso interno / Sociedade Brasileira de Biomecânica.
