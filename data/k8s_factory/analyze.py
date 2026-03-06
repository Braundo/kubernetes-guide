import json, os, re, logging
from datetime import datetime, timezone
from db import get_db, get_unprocessed_items

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("analyze")

PLAN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plan.json")
MAX = {"security": 5, "releases": 3, "ecosystem": 3, "tool-radar": 3}

def score(item):
    cat, title = item.get("category_hint",""), item.get("title","").lower()
    s = {"security":80,"releases":60,"ecosystem":40,"tool-radar":30}.get(cat,20)
    if cat == "security" and "cve" in title: s += 10
    if cat == "releases" and re.search(r"v\d+\.\d+", title): s += 20
    if "kubernetes" in item.get("source_name","").lower(): s += 10
    if "cncf" in item.get("source_name","").lower(): s += 5
    s += min(int(item.get("stars",0)/100), 30)
    pub = item.get("published","")
    if pub:
        try:
            age = (datetime.now(timezone.utc) -
                   datetime.fromisoformat(pub.replace("Z","+00:00"))).days
            if age <= 7: s += 10
            elif age <= 14: s += 5
        except: pass
    return min(s, 100)

def generate_plan():
    db = get_db()
    items = get_unprocessed_items(db)
    db.close()
    if not items:
        log.info("Nothing to plan.")
        return {"items": []}
    for i in items: i["score"] = score(i)
    items.sort(key=lambda x: x["score"], reverse=True)
    sel, counts = [], {}
    for i in items:
        c = i.get("category_hint","ecosystem")
        if counts.get(c,0) < MAX.get(c,3):
            sel.append(i)
            counts[c] = counts.get(c,0) + 1
    plan = {"generated_at": datetime.now(timezone.utc).isoformat(),
            "total_selected": len(sel), "items": sel}
    with open(PLAN, "w") as f:
        json.dump(plan, f, indent=2, default=str)
    log.info(f"Plan: {len(sel)} items selected")
    return plan

if __name__ == "__main__":
    generate_plan()
