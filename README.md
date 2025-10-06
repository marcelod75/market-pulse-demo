# Market Pulse (demo local)

API FastAPI + evidências de arquitetura para ingestão, busca e briefing diário.

## Como rodar local
- Abra Swagger: http://127.0.0.1:8020/docs
- Endpoints principais:
  - GET /api/articles
  - GET /api/articles/search?q=...
  - GET /api/briefing/daily

## Entregáveis (evidências)
Pasta \entregaveis\ com:
- \openapi.json\ (contrato), \postman_collection.json\
- \rchitecture_diagram.mmd\ (colar em https://mermaid.live)
- \example_daily_briefing.md\
- \df_pipeline_market_pulse.json\, \df_trigger_schedule.json\
- \Azure-pipelines.yml\, \dbx_etl_news.py\, \cosmos_setup.bicep\
- (opcional) \swagger.png\ (screenshot do Swagger)
