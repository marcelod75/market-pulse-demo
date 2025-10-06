from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import json, os, datetime

APP_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(os.path.dirname(APP_DIR), "data", "sample_articles.json")

class Article(BaseModel):
    id: str
    title: str
    content: str
    published_at: str
    source: Optional[str] = None
    tickers: List[str] = []
    topics: List[str] = []
    sentiment: Optional[str] = None

class Page(BaseModel):
    items: List[Article]
    page: int
    per_page: int
    total: int

class TopicBriefing(BaseModel):
    topic: str
    count: int
    sentiment: str
    impact: str

class DailyBriefing(BaseModel):
    date: str
    topics: List[TopicBriefing]
    summary: str

def _json_load_bom_safe(path: str):
    if not os.path.exists(path):
        return []
    for enc in ("utf-8-sig", "utf-8"):
        try:
            with open(path, "r", encoding=enc) as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    with open(path, "rb") as fb:
        data = fb.read()
    if data.startswith(b"\xef\xbb\xbf"):
        data = data[3:]
    text = data.decode("utf-8", errors="ignore").lstrip("\ufeff")
    return json.loads(text) if text.strip() else []

def load_articles() -> List[Article]:
    raw = _json_load_bom_safe(DATA_PATH)
    if not raw:
        raw = [
            {
                "id": "a1",
                "title": "Taxa de juros cai",
                "content": "Banco Central reduz a taxa básica, impulsionando setores sensíveis a crédito.",
                "published_at": "2025-09-28T10:00:00Z",
                "source": "Demo",
                "tickers": ["^BVSP"],
                "topics": ["juros"],
                "sentiment": "Positivo"
            },
            {
                "id": "a2",
                "title": "Greve em setor logístico",
                "content": "Interrupções em portos aumentam risco de desabastecimento e pressionam prazos.",
                "published_at": "2025-09-28T12:00:00Z",
                "source": "Demo",
                "tickers": [],
                "topics": ["logística"],
                "sentiment": "Negativo"
            }
        ]
    arts: List[Article] = []
    for a in raw:
        try:
            arts.append(Article(**a))
        except Exception:
            mapped = {
                "id": str(a.get("id") or a.get("url") or hash(a.get("title",""))),
                "title": a.get("title",""),
                "content": a.get("content") or a.get("description") or "",
                "published_at": a.get("published_at") or a.get("publishedAt") or datetime.datetime.utcnow().isoformat()+"Z",
                "source": (a.get("source") or {}).get("name") if isinstance(a.get("source"), dict) else a.get("source"),
                "tickers": a.get("tickers") or [],
                "topics": a.get("topics") or [],
                "sentiment": a.get("sentiment"),
            }
            arts.append(Article(**mapped))
    return arts

app = FastAPI(
    title="Market Pulse  Demo API",
    version="1.3.0",
    description="API de artigos + briefing diário (demo local)."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.get("/api/articles", response_model=Page)
def list_articles(page: int = Query(1, ge=1), per_page: int = Query(10, ge=1, le=100)):
    data = load_articles()
    total = len(data)
    start = (page-1)*per_page
    end = start + per_page
    return Page(items=data[start:end], page=page, per_page=per_page, total=total)

@app.get("/api/articles/search", response_model=Page)
def search_articles(q: str = Query(..., min_length=2), page: int = 1, per_page: int = 10):
    data = load_articles()
    qn = q.lower()
    hits = [a for a in data if qn in a.title.lower() or qn in a.content.lower()]
    total = len(hits)
    start = (page-1)*per_page
    end = start + per_page
    return Page(items=hits[start:end], page=page, per_page=per_page, total=total)

@app.get("/api/articles/{article_id}", response_model=Article)
def get_article(article_id: str):
    data = load_articles()
    for a in data:
        if a.id == article_id:
            return a
    raise HTTPException(status_code=404, detail="Article not found")

_POS = {"alta","otimista","positivo","cresce","queda de juros","expansão","recorde","avanço","reduz","redução","aumenta demanda"}
_NEG = {"queda","cai","baixa","piora","crise","greve","atraso","pressão de custos","inflação","risco","escassez","demissão"}
_TOPIC_SEEDS = ["juros","logística","saúde","tecnologia","energia","inflação","câmbio","commodities","resultado","regulação"]
_IMPACT_TEMPLATES: Dict[str,str] = {
    "juros": "Queda de juros tende a favorecer consumo, varejo e construção; alta encarece crédito.",
    "logística": "Restrição logística pode elevar custos e prazos, pressionando margens.",
    "saúde": "Temas de saúde afetam consumo, seguros e comportamento do trabalho.",
    "tecnologia": "Adoção tecnológica impacta produtividade e competição setorial.",
    "energia": "Volatilidade de energia mexe com custos industriais e inflação.",
    "inflação": "Inflação altera juros e poder de compra, com efeito amplo no mercado.",
    "câmbio": "Oscilação cambial afeta exportadoras/importadoras e inflação de tradables.",
    "commodities": "Preços de commodities movem setores exportadores e cadeia agrícola/mineral.",
    "resultado": "Safra de resultados aumenta volatilidade com revisões de guidance.",
    "regulação": "Mudanças regulatórias trazem risco e oportunidades setoriais."
}

def _detect_topics(a: Article) -> List[str]:
    topics = list(a.topics or [])
    text = f"{a.title} {a.content}".lower()
    for seed in _TOPIC_SEEDS:
        if seed in text and seed not in topics:
            topics.append(seed)
    return topics

def _sentiment_score(text: str) -> int:
    t = text.lower()
    score = 0
    for w in _POS:
        if w in t:
            score += 1
    for w in _NEG:
        if w in t:
            score -= 1
    return score

def _topic_sentiment(articles: List[Article], topic: str) -> str:
    score = 0
    for a in articles:
        t = (a.title or "") + " " + (a.content or "")
        if topic in (a.topics or []) or topic in t.lower():
            score += _sentiment_score(t)
    if score > 0:
        return "Positivo"
    if score < 0:
        return "Negativo"
    return "Neutro"

def _build_briefing():
    arts = load_articles()
    counts: Dict[str,int] = {}
    topic_articles: Dict[str, List[Article]] = {}
    for a in arts:
        ts = _detect_topics(a)
        for t in ts:
            counts[t] = counts.get(t, 0) + 1
            topic_articles.setdefault(t, []).append(a)
    if not counts:
        return DailyBriefing(
            date=datetime.date.today().isoformat(),
            topics=[],
            summary="Sem dados suficientes para extrair tópicos hoje."
        )
    top = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:3]
    topics_out: List[TopicBriefing] = []
    for t, c in top:
        sentiment = _topic_sentiment(topic_articles[t], t)
        impact = _IMPACT_TEMPLATES.get(t, "Impacto varia por setor; monitorar próximos desdobramentos.")
        topics_out.append(TopicBriefing(topic=t, count=c, sentiment=sentiment, impact=impact))
    resumo_parts = [f"{i+1}) {tb.topic} ({tb.sentiment})" for i, tb in enumerate(topics_out)]
    summary = "Top 3 do dia: " + "; ".join(resumo_parts) + "."
    return DailyBriefing(date=datetime.date.today().isoformat(), topics=topics_out, summary=summary)

@app.get("/api/briefing/daily", response_model=DailyBriefing)
def daily_briefing():
    return _build_briefing()

@app.get("/briefing/daily", response_model=DailyBriefing)
def daily_briefing_alias():
    return _build_briefing()
