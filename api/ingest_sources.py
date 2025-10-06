# api/ingest_sources.py
# Uso:
#   .\.venv\Scripts\python.exe api\ingest_sources.py data\news_sources.json data\sample_articles.json
import json, sys, os, urllib.request, datetime

HERE = os.path.dirname(__file__)
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")

def _load_local(relpath: str):
    path = os.path.join(DATA, relpath)
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def _load_http(url: str):
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read().decode("utf-8"))

def fetch(url_or_local: str):
    if url_or_local.startswith("local://"):
        return _load_local(url_or_local[len("local://"):])
    return _load_http(url_or_local)

def map_article(a: dict) -> dict:
    title = a.get("title") or ""
    content = a.get("content") or a.get("description") or ""
    published = a.get("publishedAt") or a.get("published_at") or datetime.datetime.utcnow().isoformat() + "Z"
    src = (a.get("source") or {}).get("name") if isinstance(a.get("source"), dict) else a.get("source")
    aid = a.get("url") or a.get("id") or f"{hash(title)}"
    return {
        "id": str(aid),
        "title": title,
        "content": content,
        "published_at": published,
        "source": src or "unknown",
        "tickers": [],
        "topics": [],
        "sentiment": None
    }

def main(in_path: str, out_path: str):
    with open(in_path, "r", encoding="utf-8-sig") as f:
        sources = json.load(f)

    all_articles = []
    for s in sources:
        url = s.get("api_endpoint")
        if not url:
            continue
        try:
            payload = fetch(url)
            arts = payload.get("articles") if isinstance(payload, dict) else payload
            if isinstance(arts, list):
                all_articles.extend(map(map_article, arts))
        except Exception as e:
            print(f"[warn] falha em {url}: {e}")

    # dedupe por id
    seen, dedup = set(), []
    for a in all_articles:
        if a["id"] in seen:
            continue
        seen.add(a["id"]); dedup.append(a)

    with open(out_path, "w", encoding="utf-8") as f:  # utf-8 sem BOM
        json.dump(dedup, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else os.path.join(DATA, "news_sources.json")
    outp = sys.argv[2] if len(sys.argv) > 2 else os.path.join(DATA, "sample_articles.json")
    main(inp, outp)
    print(f"OK: {outp}")
