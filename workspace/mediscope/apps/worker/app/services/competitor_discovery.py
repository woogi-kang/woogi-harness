"""Competitor discovery: find same-region competitors and compare scores."""

import logging
import statistics
from urllib.parse import urlparse

from ..db.supabase import get_supabase_client
from .regions import get_region_name, get_region_sggus

logger = logging.getLogger("checkyourhospital.competitor_discovery")


def _extract_domain(url: str) -> str:
    """Extract bare domain from URL (no www prefix)."""
    parsed = urlparse(url if "://" in url else f"https://{url}")
    host = parsed.hostname or ""
    if host.startswith("www."):
        host = host[4:]
    return host.lower()


def _calculate_grade(score: int | float) -> str:
    if score >= 80:
        return "A"
    if score >= 60:
        return "B"
    if score >= 40:
        return "C"
    if score >= 20:
        return "D"
    return "F"


async def discover_competitors(
    url: str,
    hospital_name: str | None = None,
) -> dict | None:
    """Find same-region competitor clinics and compare scores.

    1. Extract domain from url → match in beauty_clinics
    2. Use matched clinic's sido/sggu to find same-region clinics
    3. Query latest_score for each competitor
    4. Compute portal-level comparison from audits.details.portal_scores

    Returns comparison dict or None if matching fails.
    """
    sb = get_supabase_client()
    if sb is None:
        return None

    domain = _extract_domain(url)
    if not domain:
        return None

    # Step 1: Find this hospital in beauty_clinics
    try:
        result = (
            sb.table("beauty_clinics")
            .select("id,name,sido,sggu,website,latest_score")
            .ilike("website", f"%{domain}%")
            .limit(1)
            .execute()
        )
        rows = result.data or []
    except Exception:
        logger.exception("Failed to find clinic by domain: %s", domain)
        return None

    if not rows:
        return None

    my_clinic = rows[0]
    sido = my_clinic.get("sido", "")
    sggu = my_clinic.get("sggu", "")
    my_score = my_clinic.get("latest_score")

    if not sido or not sggu:
        return None

    # Step 2: Resolve region and find same-region clinics
    region_name = get_region_name(sido, sggu)
    region_sggus = get_region_sggus(region_name)
    if not region_sggus:
        region_sggus = {sggu}

    try:
        query = (
            sb.table("beauty_clinics")
            .select("id,name,website,latest_score,sggu")
            .eq("sido", sido)
            .in_("sggu", list(region_sggus))
            .not_.is_("latest_score", "null")
        )
        comp_result = query.execute()
        competitors_raw = comp_result.data or []
    except Exception:
        logger.exception("Failed to query regional competitors")
        return None

    if not competitors_raw:
        return None

    # Step 3: Build competitor list (exclude self)
    my_id = my_clinic["id"]
    all_clinics = []
    for c in competitors_raw:
        score = c.get("latest_score")
        if score is None:
            continue
        c_domain = _extract_domain(c.get("website", "")) if c.get("website") else ""
        all_clinics.append({
            "id": c["id"],
            "name": c.get("name", ""),
            "score": score,
            "grade": _calculate_grade(score),
            "domain": c_domain,
        })

    # Sort by score descending
    all_clinics.sort(key=lambda x: x["score"], reverse=True)

    total_competitors = len(all_clinics)
    scores = [c["score"] for c in all_clinics]

    # Find my rank
    my_rank = None
    if my_score is not None:
        my_rank = sum(1 for s in scores if s > my_score) + 1

    # Top 3 competitors (excluding self)
    top_competitors = [
        {"name": c["name"], "score": c["score"], "grade": c["grade"], "domain": c["domain"]}
        for c in all_clinics
        if c["id"] != my_id
    ][:3]

    # Averages
    regional_avg = round(statistics.mean(scores), 1) if scores else 0
    top3_scores = scores[:3] if len(scores) >= 3 else scores
    top3_avg = round(statistics.mean(top3_scores), 1) if top3_scores else 0

    # Percentile
    percentile = 0
    if my_score is not None and len(scores) > 0:
        lower_count = sum(1 for s in scores if s < my_score)
        percentile = round((lower_count / len(scores)) * 100)

    # Step 4: Portal comparison from audits.details
    portal_comparison = await _build_portal_comparison(sb, url, domain, all_clinics, my_id)

    # Build insight
    insight = _build_insight(
        my_score=my_score,
        my_rank=my_rank,
        total=total_competitors,
        top3_avg=top3_avg,
    )

    return {
        "region_name": region_name,
        "your_score": my_score,
        "your_rank": my_rank,
        "total_competitors": total_competitors,
        "competitors_with_score": len(scores),
        "regional_avg_score": regional_avg,
        "top3_avg_score": top3_avg,
        "top_competitors": top_competitors,
        "portal_comparison": portal_comparison,
        "percentile": percentile,
        "insight": insight,
    }


async def _build_portal_comparison(
    sb,
    url: str,
    my_domain: str,
    all_clinics: list[dict],
    my_id: int,
) -> dict:
    """Build per-portal score comparison from audits.details.portal_scores."""
    portals = ("naver", "google", "baidu", "yahoo_jp", "ai_search")
    comparison: dict[str, dict] = {}

    # Collect all domains for batch query
    domains = []
    for c in all_clinics:
        d = c.get("domain", "")
        if d:
            domains.append(d)

    if not domains:
        return comparison

    # Query latest audits for all competitor domains
    portal_data: dict[str, list[float]] = {p: [] for p in portals}
    my_portal_scores: dict[str, float | None] = {p: None for p in portals}

    try:
        # Get latest audit per domain via ordering
        for d in domains:
            audit_result = (
                sb.table("audits")
                .select("url,details")
                .ilike("url", f"%{d}%")
                .eq("status", "completed")
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            audit_rows = audit_result.data or []
            if not audit_rows:
                continue

            details = audit_rows[0].get("details") or {}
            ps = details.get("portal_scores") or {}

            is_me = d == my_domain

            for portal in portals:
                portal_info = ps.get(portal)
                if portal_info and isinstance(portal_info, dict):
                    score = portal_info.get("score")
                    if score is not None:
                        portal_data[portal].append(score)
                        if is_me:
                            my_portal_scores[portal] = score
    except Exception:
        logger.exception("Failed to build portal comparison")
        return comparison

    # Build comparison per portal
    for portal in portals:
        scores = portal_data[portal]
        if not scores:
            continue

        avg = round(statistics.mean(scores), 1)
        top3 = sorted(scores, reverse=True)[:3]
        top3_avg = round(statistics.mean(top3), 1) if top3 else 0
        my_val = my_portal_scores[portal]

        comparison[portal] = {
            "your": my_val,
            "avg": avg,
            "top3_avg": top3_avg,
            "gap": round(my_val - top3_avg) if my_val is not None else None,
        }

    return comparison


def _build_insight(
    my_score: int | None,
    my_rank: int | None,
    total: int,
    top3_avg: float,
) -> str:
    """Generate a Korean insight summary."""
    if my_score is None or my_rank is None:
        return f"지역 내 {total}곳의 경쟁 피부과가 있습니다."

    gap = round(top3_avg - my_score)
    parts = [f"{total}곳 중 {my_rank}위입니다."]
    if gap > 0:
        parts.append(f"상위 3곳 대비 평균 {gap}점 낮습니다.")
    elif gap < 0:
        parts.append(f"상위 3곳 평균보다 {abs(gap)}점 높습니다.")
    else:
        parts.append("상위 3곳 평균과 동일합니다.")

    return " ".join(parts)
