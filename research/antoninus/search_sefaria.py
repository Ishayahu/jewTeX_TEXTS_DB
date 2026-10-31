#!/usr/bin/env python3
"""Reproducible, paginated Sefaria search harvest for the Antoninus dossier."""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path


SEARCH_URL = "https://www.sefaria.org/api/search-wrapper"
QUERIES = [
    "אנטונינוס",
    "אנטונוס",
    "אנטולינוס",
    "אנטלימוס",
    "אנטוניוס",
    "אנטונין",
    "אנטולימוס",
    "אנטינוס",
    "אנטינינוס",
    "אנטונינס",
    "אנטנינוס",
    "אנטוניניס",
    "אנטינינס",
    "אנטולינס",
    "Antoninus",
    "Antoninos",
    "Antonios",
    "Antolinus",
]
FIELDS = ["exact", "naive_lemmatizer"]
PAGE_SIZE = 100


def post(payload: dict, attempts: int = 5) -> dict:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        SEARCH_URL,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                return json.load(response)
        except (urllib.error.URLError, TimeoutError):
            if attempt == attempts - 1:
                raise
            time.sleep(2**attempt)
    raise AssertionError("unreachable")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    log: list[dict] = []
    hits_by_id: dict[str, dict] = {}
    for query in QUERIES:
        for field in FIELDS:
            start = 0
            total = None
            while total is None or start < total:
                payload = {
                    "query": query,
                    "type": "text",
                    "field": field,
                    "start": start,
                    "size": PAGE_SIZE,
                    # Preserve the complete indexed segment and metadata so every
                    # registry entry can be checked without a second API round-trip.
                    "source_proj": True,
                }
                result = post(payload)
                total_info = result.get("hits", {}).get("total", 0)
                total = total_info.get("value", 0) if isinstance(total_info, dict) else total_info
                page_hits = result.get("hits", {}).get("hits", [])
                log.append(
                    {
                        "query": query,
                        "field": field,
                        "start": start,
                        "size": PAGE_SIZE,
                        "reported_total": total,
                        "returned": len(page_hits),
                    }
                )
                for hit in page_hits:
                    hit_id = hit.get("_id") or json.dumps(hit, sort_keys=True)
                    item = hits_by_id.setdefault(
                        hit_id,
                        {
                            "id": hit_id,
                            "source": hit.get("_source", {}),
                            "highlight": hit.get("highlight", {}),
                            "matches": [],
                        },
                    )
                    item["matches"].append({"query": query, "field": field})
                if not page_hits:
                    break
                start += len(page_hits)
                time.sleep(0.08)

    output = {
        "search_url": SEARCH_URL,
        "queries": QUERIES,
        "fields": FIELDS,
        "page_size": PAGE_SIZE,
        "request_log": log,
        "raw_hit_count_after_id_deduplication": len(hits_by_id),
        "hits": list(hits_by_id.values()),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
