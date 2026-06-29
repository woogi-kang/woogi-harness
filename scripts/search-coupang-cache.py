#!/usr/bin/env python3
"""Search the local intro_tip_links.csv Coupang affiliate-link snapshot."""

from __future__ import annotations

import argparse
import csv
import difflib
import json
import re
from pathlib import Path
from typing import Any


DEFAULT_CSV = Path("intro_tip_links.csv")


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.casefold()).strip()


def tokenize(value: str) -> list[str]:
    return [token for token in re.split(r"\s+", normalize(value)) if token]


def load_rows(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return [
            {
                "category": row.get("구분", "").strip(),
                "number": row.get("번호", "").strip(),
                "name": row.get("제품명", "").strip(),
                "url": row.get("URL", "").strip(),
                "image_url": row.get("이미지URL", "").strip(),
            }
            for row in reader
        ]


def is_coupang_row(row: dict[str, str]) -> bool:
    haystack = " ".join([row["category"], row["url"], row["image_url"]]).casefold()
    return "쿠팡" in row["category"] or "coupang" in haystack


def score_row(row: dict[str, str], query: str) -> float:
    name = normalize(row["name"])
    category = normalize(row["category"])
    url = normalize(row["url"])
    query_norm = normalize(query)
    terms = tokenize(query)

    if not query_norm:
        return 1.0

    score = 0.0
    if query_norm in name:
        score += 100.0
    if query_norm in category:
        score += 20.0
    if query_norm in url:
        score += 10.0

    for term in terms:
        if term in name:
            score += 25.0
        elif term in category:
            score += 5.0

    score += difflib.SequenceMatcher(None, query_norm, name).ratio() * 25.0

    if is_coupang_row(row):
        score += 5.0

    return score


def matches_query(row: dict[str, str], query: str) -> bool:
    query_norm = normalize(query)
    if not query_norm:
        return True

    haystacks = [
        normalize(row["name"]),
        normalize(row["category"]),
        normalize(row["url"]),
    ]
    if any(query_norm in haystack for haystack in haystacks):
        return True

    terms = tokenize(query)
    if not terms:
        return True

    # For multi-term product names, require every term to appear somewhere in
    # the row. A single broad term such as "프로" should not match unrelated
    # entries like "빔프로젝트" for a query such as "m5 맥북 프로".
    return all(any(term in haystack for haystack in haystacks) for term in terms)


def search(
    rows: list[dict[str, str]],
    query: str,
    limit: int,
    include_all_sources: bool,
) -> list[dict[str, Any]]:
    candidates = rows if include_all_sources else [row for row in rows if is_coupang_row(row)]
    scored = []
    for row in candidates:
        if not matches_query(row, query):
            continue
        score = score_row(row, query)
        scored.append((score, row))

    scored.sort(key=lambda item: (-item[0], item[1]["name"]))
    results = []
    for score, row in scored[:limit]:
        results.append(
            {
                **row,
                "score": round(score, 2),
                "source": "local_cache",
                "freshness": "static snapshot; price, stock, and delivery status are not verified",
                "confidence": "link candidate only",
            }
        )
    return results


def print_markdown(results: list[dict[str, Any]], query: str) -> None:
    title = f'# Local Coupang Cache Results for "{query}"' if query else "# Local Coupang Cache Results"
    print(title)
    print()

    if not results:
        print("No cached Coupang link candidates matched the query.")
        print()
        print("> This fallback searches only the local static link snapshot; it does not verify live price, stock, or delivery.")
        return

    print("> Static fallback: links may be stale; live price, stock, reviews, ranking, and delivery status are not verified.")
    print()
    for index, row in enumerate(results, start=1):
        number = f' #{row["number"]}' if row["number"] else ""
        print(f'{index}. {row["name"]}{number}')
        print(f'   - category: {row["category"] or "unknown"}')
        print(f'   - score: {row["score"]}')
        print(f'   - url: {row["url"]}')
        if row["image_url"]:
            print(f'   - image: {row["image_url"]}')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="?", default="", help="Search keyword, for example: 버터")
    parser.add_argument("--csv", default=str(DEFAULT_CSV), help="Path to intro_tip_links.csv")
    parser.add_argument("--limit", type=int, default=10, help="Maximum result count")
    parser.add_argument(
        "--include-all-sources",
        action="store_true",
        help="Search non-Coupang rows too. Default searches only Coupang-like rows.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON instead of Markdown")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    csv_path = Path(args.csv)
    if not csv_path.exists():
        raise SystemExit(f"CSV file not found: {csv_path}")
    if args.limit < 1:
        raise SystemExit("--limit must be >= 1")

    rows = load_rows(csv_path)
    results = search(rows, args.query, args.limit, args.include_all_sources)

    if args.json:
        print(json.dumps({"query": args.query, "count": len(results), "results": results}, ensure_ascii=False, indent=2))
    else:
        print_markdown(results, args.query)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
