import os, re, json, logging
from datetime import datetime, timezone
from db import get_db, mark_processed
from llm import write_article

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("generate")

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DOCS = os.path.join(REPO, "docs", "automation")
PLAN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plan.json")

def slugify(t, n=60):
    t = re.sub(r"[^a-z0-9\s-]", "", t.lower().strip())
    return re.sub(r"[\s_-]+", "-", t).strip("-")[:n]

def filename(item):
    p = item.get("published","")
    try: d = datetime.fromisoformat(p.replace("Z","+00:00")).strftime("%Y-%m-%d")
    except: d = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return f"{d}-{slugify(item.get('title','untitled'))}.md"

def build_page(item, body):
    now = datetime.now(timezone.utc).isoformat()
    t, u = item.get("title",""), item.get("url","")
    p, c = item.get("published",""), item.get("category_hint","")
    d = p[:10] if len(p)>=10 else now[:10]
    return f"---\ntitle: \"{t}\"\ndate: {d}\ncategory: {c}\n"\
           f"source_url: \"{u}\"\ngenerated: \"{now}\"\n---\n\n"\
           f"# {t}\n\n"\
           f"**Source:** [{item.get('source_name','')}]({u})\n"\
           f"**Published:** {d} | **Category:** {c.replace('-',' ').title()}"\
           f"\n\n{body}\n\n---\n"\
           f"*Published {now[:10]} on k8s.guide*\n"

def update_index(cat, entries):
    idx = os.path.join(DOCS, cat, "index.md")
    if not os.path.exists(idx): return
    lines = [f"- [{e['title']}]({e['file']}) ({e['date']})" for e in entries]
    with open(idx) as f: content = f.read()
    marker = "<!-- AUTO-GENERATED-LIST -->"
    if marker in content:
        parts = content.split(marker)
        content = parts[0]+marker+"\n"+"\n".join(lines)+"\n"+(
            parts[1] if len(parts)>1 else "")
    else:
        content = content.rstrip()+"\n\n"+"\n".join(lines)+"\n"
    with open(idx,"w") as f: f.write(content)

def run_generate():
    if not os.path.exists(PLAN):
        log.error("No plan.json")
        return 0
    with open(PLAN) as f: plan = json.load(f)
    items = plan.get("items",[])
    if not items:
        log.info("Empty plan.")
        return 0
    db = get_db()
    gen, updates = 0, {}
    for item in items:
        cat = item.get("category_hint","ecosystem")
        out = os.path.join(DOCS, cat)
        os.makedirs(out, exist_ok=True)
        fn = filename(item)
        fp = os.path.join(out, fn)
        if os.path.exists(fp):
            log.info(f"Skip (exists): {fn}")
            continue
        body = write_article(item)
        if not body:
            log.error(f"LLM failed for {fn}")
            continue
        with open(fp,"w") as f: f.write(build_page(item, body))
        if item.get("id"): mark_processed(db, item["id"], fn)
        updates.setdefault(cat,[]).append({"title":item.get("title",""),
            "file":fn, "date":item.get("published","")[:10]})
        gen += 1
    for cat, entries in updates.items():
        update_index(cat, entries)
    db.close()
    log.info(f"Generated {gen} articles.")
    return gen

if __name__ == "__main__":
    run_generate()
