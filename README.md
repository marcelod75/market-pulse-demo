Market Pulse — Demo (Azure-first)

Plataforma para ingestão, curadoria e consulta de notícias, com FastAPI + Swagger e um Boletim Diário (tópicos, impacto e sentimento).
Arquitetura orientada a Azure: ADF, Functions, ADLS, Databricks, AI Search/OpenAI e Cosmos DB.

✅ Inclui API funcional local + artefatos de arquitetura (evidências) prontos para apresentação.

### 📁 Estrutura do projeto
```text
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

🚀 Como executar localmente

Pré-requisitos: Windows, VS Code, Python 3.11+

# (opcional) criar e ativar venv, instalar deps
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt

# subir a API
$ADDR=127.0.0.1; $PORT=8020
.\.venv\Scripts\python.exe -m uvicorn api.api_app:app --host $ADDR --port $PORT --reload


Swagger: http://127.0.0.1:8020/docs

Endpoints:

GET /api/articles

GET /api/articles/search?q=termo

GET /api/articles/{id}

GET /api/briefing/daily

Exemplos (curl):

BASE=http://127.0.0.1:8020/api
curl "$BASE/articles"
curl "$BASE/articles/search?q=juros"
curl "$BASE/articles/a1"
curl "$BASE/briefing/daily"

🧱 Modelo de dados (resumo)

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

{ "items": [/* Article[] */], "page": 1, "per_page": 10, "total": 2 }

🧠 Boletim Diário (entrega)

Top 3 tópicos do dia (contagem por topics)

Impacto potencial resumido por tópico

Sentimento por tópico (Positivo / Negativo / Neutro)

Exemplo de resposta:

{
  "date": "2025-10-03",
  "topics": [
    { "topic": "juros", "count": 1, "sentiment": "Neutro", "impact": "Queda de juros tende a favorecer consumo..." },
    { "topic": "economia", "count": 1, "sentiment": "Neutro", "impact": "Impacto varia por setor..." },
    { "topic": "logística", "count": 1, "sentiment": "Negativo", "impact": "Restrição logística pode elevar custos..." }
  ],
  "summary": "Top 3 do dia: 1) juros (Neutro); 2) economia (Neutro); 3) logística (Negativo)."
}

🧰 Ingestão de fontes (opcional)

Se houver data/news_sources.json, a ingestão automática gera data/sample_articles.json no esquema unificado (UTF-8 sem BOM):

.\.venv\Scripts\python.exe api\ingest_sources.py data\news_sources.json data\sample_articles.json

🧩 Arquitetura (Azure-ready)

Orquestração: ADF (trigger) → ForEach → Azure Function por fonte (paralelismo controlado)

Raw landing: ADLS Gen2 (raw/) com JSON + metadados

Curadoria/ETL: Databricks (PySpark), normalização + dedupe + enriquecimento → Parquet particionado (curated/)

Busca & Vetores: Azure AI Search (full-text + vetorial) com embeddings do Azure OpenAI

Consulta quente: Cosmos DB (metadados/ponteiros, baixa latência)

Analytics: Synapse Serverless SQL / Databricks SQL

API & Segurança: Azure Functions + APIM com JWT (Azure AD)

Observabilidade/Qualidade: App Insights / Log Analytics (+ roadmap: Great Expectations)

Diagrama: entregaveis/architecture_diagram.mmd (visualize em https://mermaid.live
)

🔎 Evidências (onde comprovar)

Coleta/Processamento/Armazenamento: adf_pipeline_market_pulse.json, adf_trigger_schedule.json, dbx_etl_news.py, cosmos_setup.bicep, architecture_diagram.mmd

API: openapi.json, postman_collection.json

Boletim Diário: rota GET /api/briefing/daily + example_daily_briefing.md

🐞 Troubleshooting

404 em /api/briefing/daily → confirme host/porta e que a API está rodando.

Porta ocupada → libere a 8020 antes de iniciar.

Acentos estranhos → salve .json/.md em UTF-8 (sem BOM).

Licença: uso educacional/demonstração.
