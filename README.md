Market Pulse — Demo (Azure-first)

Plataforma demo para ingestão, curadoria e consulta de notícias, com API FastAPI, Swagger e um Boletim Diário (tópicos + impacto + sentimento).
Arquitetura pensada para Azure (ADF, Functions, ADLS, Databricks, AI Search/OpenAI, Cosmos) com entregáveis para apresentação.

✅ Este repositório inclui API funcional local + artefatos de arquitetura para evidenciar as decisões.

🚀 Como rodar local

Pré-requisitos

Windows + PowerShell

Python 3.11+

(Opcional) VS Code

Passos

# PowerShell na pasta do projeto:
$ADDR='127.0.0.1'; $PORT=8020
.\.venv\Scripts\python.exe -m uvicorn api.api_app:app --host $ADDR --port $PORT --reload


Abra o Swagger:
http://127.0.0.1:8020/docs

Endpoints principais

GET /api/articles

GET /api/articles/search?q=termo

GET /api/articles/{id}

GET /api/briefing/daily

🔎 Exemplos rápidos (PowerShell)
$BASE = "http://127.0.0.1:8020/api"

# Lista com paginação padrão (page=1, per_page=10)
Invoke-RestMethod "$BASE/articles"

# Busca por palavra
Invoke-RestMethod "$BASE/articles/search?q=juros"

# Detalhe por ID
Invoke-RestMethod "$BASE/articles/a1"

# Boletim Diário (tópicos + impacto + sentimento)
Invoke-RestMethod "$BASE/briefing/daily"

🧱 Modelo de dados (API)
Article
{
  "id": "a1",
  "title": "Taxa de juros cai",
  "content": "Banco Central reduz a taxa básica...",
  "published_at": "2025-09-28T10:00:00Z",
  "source": "Reuters",
  "tickers": ["^BVSP"],
  "topics": ["juros", "economia"],
  "sentiment": "Positivo"
}

Page
{
  "items": [ /* Article[] */ ],
  "page": 1,
  "per_page": 10,
  "total": 2
}

🧠 Boletim Diário (o que ele entrega)

Top 3 tópicos do dia (contagem por topics)

Impacto potencial resumido por tópico

Sentimento (Positivo, Negativo, Neutro)

Exemplo de resposta:

{
  "date": "2025-10-03",
  "topics": [
    { "topic": "juros",     "count": 1, "sentiment": "Neutro",   "impact": "Queda de juros tende a favorecer consumo..." },
    { "topic": "economia",  "count": 1, "sentiment": "Neutro",   "impact": "Impacto varia por setor..." },
    { "topic": "logística", "count": 1, "sentiment": "Negativo", "impact": "Restrição logística pode elevar custos..." }
  ],
  "summary": "Top 3 do dia: 1) juros (Neutro); 2) economia (Neutro); 3) logística (Negativo)."
}

🧰 Ingestão de fontes (opcional, para gerar data/sample_articles.json)

O script abaixo lê um arquivo de fontes (ex.: data/news_sources.json), baixa conteúdo e grava no esquema da demo, garantindo UTF-8 sem BOM.

# Se tiver um news_sources.json, rode:
.\.venv\Scripts\python.exe api\ingest_sources.py data\news_sources.json data\sample_articles.json


Arquivo: api/ingest_sources.py

🗂️ Estrutura do projeto
.'''
├─ api/
│  ├─ api_app.py              # FastAPI (rotas /api/articles, /api/briefing/daily, etc.)
│  └─ ingest_sources.py       # (opcional) ingestão a partir de news_sources.json
├─ data/
│  └─ sample_articles.json    # dataset demo (UTF-8)
├─ entregaveis/
│  ├─ openapi.json            # contrato OpenAPI (export da API local)
│  ├─ postman_collection.json # coleção Postman (baseUrl + requests)
│  ├─ architecture_diagram.mmd# diagrama Mermaid
│  ├─ example_daily_briefing.md
│  ├─ adf_pipeline_market_pulse.json
│  ├─ adf_trigger_schedule.json
│  ├─ azure-pipelines.yml
│  ├─ dbx_etl_news.py
│  ├─ cosmos_setup.bicep
│  └─ market-pulse-entregaveis.zip  # pacote com tudo acima
├─ requirements.txt
└─ README.md
'''
🧩 Arquitetura (Azure-ready)

Orquestração: Azure Data Factory (trigger de tempo) → ForEach chama Azure Function por fonte (paralelismo controlado).

Raw landing: ADLS Gen2 (raw/) guarda JSON original + metadados.

Curadoria/ETL: Databricks (PySpark) normaliza, deduplica, enriquece (Text Analytics/LLM) e grava Parquet particionado (curated/).

Busca & Vetores: Azure AI Search (full-text + vetor) com embeddings do Azure OpenAI.

Consulta quente: Cosmos DB guarda metadados e ponteiros (baixa latência).

Analytics: Synapse Serverless SQL ou Databricks SQL.

API & Segurança: Azure Functions (consumption), APIM com JWT AAD.

Qualidade/Obs: Great Expectations + Application Insights / Log Analytics + alertas Azure Monitor.

Diagrama (Mermaid): entregaveis/architecture_diagram.mmd

Cole o conteúdo em https://mermaid.live
 para visualizar.

📄 Contrato da API

Especificação OpenAPI: entregaveis/openapi.json

Coleção Postman: entregaveis/postman_collection.json

Endpoints

GET /api/articles?page=1&per_page=10

GET /api/articles/search?q=termo&page=1&per_page=10

GET /api/articles/{id}

GET /api/briefing/daily

🧪 CI/CD e qualidade

CI (placeholder): entregaveis/azure-pipelines.yml (lint/test demonstrativo).

Dados/ETL: entregaveis/dbx_etl_news.py (PySpark — leitura raw → curated particionado).

Infra Cosmos: entregaveis/cosmos_setup.bicep (contêiner articles, partição por dt_partition).

📦 Entregáveis (evidências)

Na pasta entregaveis/ você encontra:

openapi.json (contrato da API)

postman_collection.json (pronto para importar)

architecture_diagram.mmd (diagrama)

example_daily_briefing.md (exemplo do boletim)

adf_pipeline_market_pulse.json e adf_trigger_schedule.json (orquestração)

dbx_etl_news.py (ETL Databricks)

cosmos_setup.bicep (infra Cosmos)

azure-pipelines.yml (pipeline CI)

market-pulse-entregaveis.zip (bundle de tudo acima)

🛠️ Solução dos 3 cenários do case (onde comprovar)

Coleta/Processamento/Armazenamento

Orquestração: ADF (adf_*.json)

Unificação: Databricks (dbx_etl_news.py)

Armazenamento: ADLS (Parquet) + Cosmos (metadados) (cosmos_setup.bicep)

Diagrama: architecture_diagram.mmd

API de acesso

Contrato: openapi.json + postman_collection.json

Resiliência/escala: Functions + APIM (descritas no README/diagrama)

Segurança: JWT AAD via APIM (descrita no README/diagrama)

Boletim Diário (IA)

Resultado: example_daily_briefing.md + rota /api/briefing/daily

Abordagem: seção “Arquitetura (Azure-ready)” e “Boletim Diário” explicam agentes/fluxo

🐞 Troubleshooting

404 em /api/briefing/daily
Garanta que você está na pasta do projeto e subiu a API com:
python -m uvicorn api.api_app:app --host 127.0.0.1 --port 8020 --reload

Porta 8020 ocupada

Get-NetTCPConnection -LocalPort 8020 | Select-Object -First 5
# mate o processo:
Stop-Process -Id <PID> -Force


JSON com BOM / acentos quebrados
Mantenha arquivos .json e .md em UTF-8 (sem BOM). No VS Code: Save with Encoding → UTF-8.

ExecutionPolicy bloqueando venv/Activate.ps1
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

📌 Roadmap breve

Incluir Great Expectations no ETL (validação de dados).

Deploy da API em Azure Functions com APIM e AAD.

Indexação vetorial em Azure AI Search + RAG para briefing.

Licença

Uso educacional/demonstração.

Se quiser, eu já deixo esse conteúdo salvo como README.md no repo — só dizer “sim”.

Você disse:
sim
O ChatGPT disse:
Pensou por 36s

perfeito — segue um bloco único de PowerShell para você copiar e colar no terminal do VS Code. Ele sobrescreve o README.md com a versão completa, faz commit e dá push para o seu repositório marcelod75/market-pulse-demo.

# === Atualiza README.md, commita e faz push ===
# (execute na pasta C:\Users\marce\market-pulse-demo)

$readme = @'
# Market Pulse — Demo (Azure-first)

Plataforma **demo** para ingestão, curadoria e consulta de notícias, com **API FastAPI**, **Swagger** e um **Boletim Diário** (tópicos + impacto + sentimento).  
Arquitetura pensada para **Azure** (ADF, Functions, ADLS, Databricks, AI Search/OpenAI, Cosmos) com entregáveis para apresentação.

> ✅ Este repositório inclui **API funcional local** + **artefatos de arquitetura** para evidenciar as decisões.

---

## 🚀 Como rodar local

**Pré-requisitos**
- Windows + PowerShell
- Python 3.11+
- (Opcional) VS Code

**Passos**
```ps1
# PowerShell na pasta do projeto:
$ADDR='127.0.0.1'; $PORT=8020
.\.venv\Scripts\python.exe -m uvicorn api.api_app:app --host $ADDR --port $PORT --reload


Abra o Swagger:
http://127.0.0.1:8020/docs

Endpoints principais

GET /api/articles

GET /api/articles/search?q=termo

GET /api/articles/{id}

GET /api/briefing/daily

🔎 Exemplos rápidos (PowerShell)
$BASE = "http://127.0.0.1:8020/api"

# Lista com paginação padrão (page=1, per_page=10)
Invoke-RestMethod "$BASE/articles"

# Busca por palavra
Invoke-RestMethod "$BASE/articles/search?q=juros"

# Detalhe por ID
Invoke-RestMethod "$BASE/articles/a1"

# Boletim Diário (tópicos + impacto + sentimento)
Invoke-RestMethod "$BASE/briefing/daily"

🧱 Modelo de dados (API)
Article
{
  "id": "a1",
  "title": "Taxa de juros cai",
  "content": "Banco Central reduz a taxa básica...",
  "published_at": "2025-09-28T10:00:00Z",
  "source": "Reuters",
  "tickers": ["^BVSP"],
  "topics": ["juros", "economia"],
  "sentiment": "Positivo"
}

Page
{
  "items": [ /* Article[] */ ],
  "page": 1,
  "per_page": 10,
  "total": 2
}

🧠 Boletim Diário (o que ele entrega)

Top 3 tópicos do dia (contagem por topics)

Impacto potencial resumido por tópico

Sentimento (Positivo, Negativo, Neutro)

Exemplo de resposta:

{
  "date": "2025-10-03",
  "topics": [
    { "topic": "juros",     "count": 1, "sentiment": "Neutro",   "impact": "Queda de juros tende a favorecer consumo..." },
    { "topic": "economia",  "count": 1, "sentiment": "Neutro",   "impact": "Impacto varia por setor..." },
    { "topic": "logística", "count": 1, "sentiment": "Negativo", "impact": "Restrição logística pode elevar custos..." }
  ],
  "summary": "Top 3 do dia: 1) juros (Neutro); 2) economia (Neutro); 3) logística (Negativo)."
}

🧰 Ingestão de fontes (opcional, para gerar data/sample_articles.json)

O script abaixo lê um arquivo de fontes (ex.: data/news_sources.json), baixa conteúdo e grava no esquema da demo, garantindo UTF-8 sem BOM.

# Se tiver um news_sources.json, rode:
.\.venv\Scripts\python.exe api\ingest_sources.py data\news_sources.json data\sample_articles.json


Arquivo: api/ingest_sources.py

🗂️ Estrutura do projeto
.
├─ api/
│  ├─ api_app.py              # FastAPI (rotas /api/articles, /api/briefing/daily, etc.)
│  └─ ingest_sources.py       # (opcional) ingestão a partir de news_sources.json
├─ data/
│  └─ sample_articles.json    # dataset demo (UTF-8)
├─ entregaveis/
│  ├─ openapi.json            # contrato OpenAPI (export da API local)
│  ├─ postman_collection.json # coleção Postman (baseUrl + requests)
│  ├─ architecture_diagram.mmd# diagrama Mermaid
│  ├─ example_daily_briefing.md
│  ├─ adf_pipeline_market_pulse.json
│  ├─ adf_trigger_schedule.json
│  ├─ azure-pipelines.yml
│  ├─ dbx_etl_news.py
│  ├─ cosmos_setup.bicep
│  └─ market-pulse-entregaveis.zip  # pacote com tudo acima
├─ requirements.txt
└─ README.md

🧩 Arquitetura (Azure-ready)

Orquestração: Azure Data Factory (trigger de tempo) → ForEach chama Azure Function por fonte (paralelismo controlado).

Raw landing: ADLS Gen2 (raw/) guarda JSON original + metadados.

Curadoria/ETL: Databricks (PySpark) normaliza, deduplica, enriquece (Text Analytics/LLM) e grava Parquet particionado (curated/).

Busca & Vetores: Azure AI Search (full-text + vetor) com embeddings do Azure OpenAI.

Consulta quente: Cosmos DB guarda metadados e ponteiros (baixa latência).

Analytics: Synapse Serverless SQL ou Databricks SQL.

API & Segurança: Azure Functions (consumption), APIM com JWT AAD.

Qualidade/Obs: Great Expectations + Application Insights / Log Analytics + alertas Azure Monitor.

Diagrama (Mermaid): entregaveis/architecture_diagram.mmd

Cole o conteúdo em https://mermaid.live
 para visualizar.

📄 Contrato da API

Especificação OpenAPI: entregaveis/openapi.json

Coleção Postman: entregaveis/postman_collection.json

Endpoints

GET /api/articles?page=1&per_page=10

GET /api/articles/search?q=termo&page=1&per_page=10

GET /api/articles/{id}

GET /api/briefing/daily

🧪 CI/CD e qualidade

CI (placeholder): entregaveis/azure-pipelines.yml (lint/test demonstrativo).

Dados/ETL: entregaveis/dbx_etl_news.py (PySpark — leitura raw → curated particionado).

Infra Cosmos: entregaveis/cosmos_setup.bicep (contêiner articles, partição por dt_partition).

📦 Entregáveis (evidências)

Na pasta entregaveis/ você encontra:

openapi.json (contrato da API)

postman_collection.json (pronto para importar)

architecture_diagram.mmd (diagrama)

example_daily_briefing.md (exemplo do boletim)

adf_pipeline_market_pulse.json e adf_trigger_schedule.json (orquestração)

dbx_etl_news.py (ETL Databricks)

cosmos_setup.bicep (infra Cosmos)

azure-pipelines.yml (pipeline CI)

market-pulse-entregaveis.zip (bundle de tudo acima)

🐞 Troubleshooting

404 em /api/briefing/daily
Garanta que você está na pasta do projeto e subiu a API com:
python -m uvicorn api.api_app:app --host 127.0.0.1 --port 8020 --reload

Porta 8020 ocupada

Get-NetTCPConnection -LocalPort 8020 | Select-Object -First 5
# mate o processo:
Stop-Process -Id <PID> -Force


JSON com BOM / acentos quebrados
Mantenha arquivos .json e .md em UTF-8 (sem BOM). No VS Code: Save with Encoding → UTF-8.

ExecutionPolicy bloqueando venv/Activate.ps1
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

📌 Roadmap breve

Incluir Great Expectations no ETL (validação de dados).

Deploy da API em Azure Functions com APIM e AAD.

Indexação vetorial em Azure AI Search + RAG para briefing.

Licença

Uso educacional/demonstração.
'@

Grava o arquivo (UTF-8)

$readme | Out-File -FilePath README.md -Encoding utf8

Commit e push

git add README.md
if (-not (git diff --cached --quiet)) {
git commit -m "docs: README completo (arquitetura Azure, API, evidências e troubleshooting)"
}

Garante branch/main e remoto

git branch -M main
if (-not (git remote | Select-String -SimpleMatch "origin")) {
git remote add origin https://github.com/marcelod75/market-pulse-demo.git

} else {
git remote set-url origin https://github.com/marcelod75/market-pulse-demo.git

}

git push -u origin main

Abre o README no GitHub

Start-Process "https://github.com/marcelod75/market-pulse-demo/blob/main/README.md
"
