#!/usr/bin/env python3
import argparse
import json
import os
import re
import uuid
from datetime import datetime, timezone

from content_policy import CATEGORY_CONFIG, infer_category, normalize_space

TOPIC_REQUESTS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "topic_requests.json",
)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _load():
    if not os.path.exists(TOPIC_REQUESTS_PATH):
        return []
    try:
        with open(TOPIC_REQUESTS_PATH) as handle:
            data = json.load(handle)
    except Exception:
        return []
    if isinstance(data, list):
        return data
    return []


def _save(entries):
    with open(TOPIC_REQUESTS_PATH, "w") as handle:
        json.dump(entries, handle, indent=2)


def _normalize_sources(values):
    normalized = []
    for value in values or []:
        for part in re.split(r"[,\s]+", value or ""):
            url = (part or "").strip()
            if not url:
                continue
            normalized.append(url)
    unique = []
    seen = set()
    for url in normalized:
        if url in seen:
            continue
        seen.add(url)
        unique.append(url)
    return unique


def _is_pending_duplicate(entries, topic):
    target = normalize_space(topic).lower()
    if not target:
        return False
    for entry in entries:
        if (entry.get("status") or "pending") != "pending":
            continue
        if normalize_space(entry.get("topic", "")).lower() == target:
            return True
    return False


def add_request(topic, category="", notes="", sources=None, requested_by="manual"):
    entries = _load()
    topic = normalize_space(topic)
    notes = normalize_space(notes)
    if not topic:
        raise ValueError("Topic must not be empty.")

    if _is_pending_duplicate(entries, topic):
        return None

    category = (category or "").strip().lower()
    if category and category not in CATEGORY_CONFIG:
        raise ValueError(
            "Invalid category. Use one of: " + ", ".join(sorted(CATEGORY_CONFIG.keys()))
        )

    inferred = infer_category(
        title=topic,
        summary=notes,
        default=category or "ecosystem",
        url=(sources or [""])[0] if sources else "",
    )

    entry = {
        "id": str(uuid.uuid4())[:12],
        "topic": topic,
        "category_hint": inferred,
        "notes": notes,
        "sources": _normalize_sources(sources),
        "status": "pending",
        "requested_by": requested_by,
        "requested_at": _now_iso(),
    }
    entries.append(entry)
    _save(entries)
    return entry


def pending_requests():
    entries = _load()
    return [entry for entry in entries if (entry.get("status") or "pending") == "pending"]


def resolve_requests(ids, status):
    want = {str(req_id) for req_id in (ids or [])}
    if not want:
        return 0
    status = (status or "").strip().lower()
    if status not in {"published", "skipped"}:
        raise ValueError("status must be 'published' or 'skipped'")

    entries = _load()
    changed = 0
    for entry in entries:
        if str(entry.get("id")) not in want:
            continue
        entry["status"] = status
        entry["resolved_at"] = _now_iso()
        changed += 1

    if changed:
        _save(entries)
    return changed


def _cmd_add(args):
    entry = add_request(
        topic=args.topic,
        category=args.category,
        notes=args.notes,
        sources=args.source,
        requested_by=args.requested_by or "cli",
    )
    if not entry:
        print("Topic already pending; skipped duplicate request.")
        return 0
    print(f"Added topic request: {entry['id']} | {entry['topic']} ({entry['category_hint']})")
    return 0


def _cmd_list(_args):
    entries = pending_requests()
    if not entries:
        print("No pending topic requests.")
        return 0
    for entry in entries:
        source_count = len(entry.get("sources") or [])
        print(
            f"{entry.get('id')} | {entry.get('category_hint')} | "
            f"{entry.get('topic')} | sources={source_count}"
        )
    return 0


def _cmd_clear(args):
    entries = _load()
    if args.all:
        _save([])
        print("Cleared all topic requests.")
        return 0

    keep = [entry for entry in entries if str(entry.get("id")) not in set(args.id or [])]
    _save(keep)
    print(f"Removed {len(entries) - len(keep)} topic request(s).")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Manage k8s.guide manual topic requests.")
    sub = parser.add_subparsers(dest="command", required=True)

    add_p = sub.add_parser("add", help="Add a custom topic request")
    add_p.add_argument("--topic", required=True, help="Requested article topic/title")
    add_p.add_argument("--category", default="", help="Optional category hint")
    add_p.add_argument("--notes", default="", help="Optional angle/context notes")
    add_p.add_argument("--source", action="append", default=[], help="Optional source URL")
    add_p.add_argument("--requested-by", default="cli", help="Origin marker for request")
    add_p.set_defaults(func=_cmd_add)

    list_p = sub.add_parser("list", help="List pending topic requests")
    list_p.set_defaults(func=_cmd_list)

    clear_p = sub.add_parser("clear", help="Remove topic requests")
    clear_p.add_argument("--id", action="append", default=[], help="Request id to remove")
    clear_p.add_argument("--all", action="store_true", help="Remove all requests")
    clear_p.set_defaults(func=_cmd_clear)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
