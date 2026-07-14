#!/usr/bin/env python3
"""Dedupe state per company. Standard library only.

Each company has companies/<TICKER>/news/state.json holding fingerprints of items
already shown, so the daily run never repeats a story ("nothing new -> nothing sent").

Fingerprint = sha1 of normalized (title + url). Entries older than KEEP_DAYS are
pruned so the file doesn't grow forever.

CLI (used by the daily run):
    # given a JSON list of {title,url,date} on stdin, print only the NEW ones:
    python state.py filter FERG < items.json
    # mark a JSON list of items as seen (as of an ISO date you pass in):
    python state.py mark FERG 2026-06-07 < items.json
"""
import hashlib
import json
import re
import sys
from pathlib import Path

KEEP_DAYS = 60
COMPANIES_DIR = Path(__file__).resolve().parent.parent / "companies"


def _state_path(ticker: str) -> Path:
    return COMPANIES_DIR / ticker.upper() / "news" / "state.json"


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def fingerprint(item: dict) -> str:
    key = _norm(item.get("title", "")) + "|" + _norm(item.get("url", ""))
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]


def _load(ticker: str) -> dict:
    p = _state_path(ticker)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"seen": {}}  # fingerprint -> iso date first seen


def _save(ticker: str, data: dict) -> None:
    p = _state_path(ticker)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _prune(data: dict, today_iso: str) -> dict:
    try:
        from datetime import date
        cutoff = date.fromisoformat(today_iso).toordinal() - KEEP_DAYS
        data["seen"] = {k: v for k, v in data["seen"].items()
                        if date.fromisoformat(v).toordinal() >= cutoff}
    except Exception:
        pass
    return data


def cmd_filter(ticker: str):
    items = json.load(sys.stdin)
    seen = _load(ticker)["seen"]
    fresh = [it for it in items if fingerprint(it) not in seen]
    json.dump(fresh, sys.stdout, indent=2)


def cmd_mark(ticker: str, today_iso: str):
    items = json.load(sys.stdin)
    data = _load(ticker)
    for it in items:
        data["seen"].setdefault(fingerprint(it), today_iso)
    _save(ticker, _prune(data, today_iso))
    print(f"marked {len(items)} item(s) seen for {ticker.upper()}")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "filter":
        cmd_filter(sys.argv[2])
    elif len(sys.argv) >= 4 and sys.argv[1] == "mark":
        cmd_mark(sys.argv[2], sys.argv[3])
    else:
        sys.exit(__doc__)
