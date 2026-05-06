"""Scanner orchestrator: runs all checks and produces a score."""

import logging

import httpx

from ..checks.base import CheckResult, Grade
from ..checks.canonical import check_canonical
from ..checks.conversion_elements import check_conversion_elements
from ..checks.errors import check_errors
from ..checks.geo_aeo import check_ai_search_mention, check_content_clarity
from ..checks.headings import check_headings
from ..checks.https_check import check_https
from ..checks.images import check_images
from ..checks.international_search import check_international_search
from ..checks.links import check_links
from ..checks.meta_tags import check_meta_tags
from ..checks.mobile import check_mobile
from ..checks.multilingual import (
    check_hreflang,
    check_multilingual_pages,
    check_overseas_channels,
)
from ..checks.performance import check_performance
from ..checks.robots import check_robots
from ..checks.sitemap import check_sitemap
from ..checks.structured_data import (
    check_eeat_signals,
    check_faq_content,
    check_structured_data,
)
from ..checks.url_structure import check_url_structure
from ..config import settings
from .competitor_discovery import discover_competitors
from .content_freshness_analyzer import analyze_content_freshness
from .crawler import Crawler
from .international_usability import analyze_international_usability
from .keyword_engine import extract_and_generate_keywords
from .medical_compliance import check_medical_compliance
from .multilingual_analyzer import analyze_multilingual_readiness
from .patient_journey_scorer import calculate_journey_scores
from .portal_scorer import calculate_portal_scores
from .procedure_completeness import analyze_procedure_completeness
from .review_sentiment import analyze_review_sentiment
from .scorer import calculate_score
from .season_insight import get_season_insight
from .serp_checker import check_keyword_rankings
from .tech_stack_detector import detect_tech_stack
from .video_presence import analyze_video_presence
from .voice_search_analyzer import analyze_voice_search_readiness

logger = logging.getLogger("checkyourhospital.scanner")


async def _safe_check(coro, name: str) -> CheckResult | None:
    """Run a check safely — return None on unexpected crash instead of killing scan."""
    try:
        return await coro
    except Exception as e:
        logger.error(f"Check {name} crashed: {e}")
        return CheckResult(
            name=name, score=0.0, grade=Grade.FAIL,
            fail_type="api_error",
            display_name=name,
            description="이 항목 측정 중 오류가 발생했습니다",
            recommendation="다시 진단을 시도해주세요",
            issues=[f"측정 중 오류: {type(e).__name__}"],
        )


def _safe_sync(fn, name: str) -> CheckResult:
    """Run a sync check safely."""
    try:
        return fn()
    except Exception as e:
        logger.error(f"Check {name} crashed: {e}")
        return CheckResult(
            name=name, score=0.0, grade=Grade.FAIL,
            fail_type="api_error",
            display_name=name,
            description="이 항목 측정 중 오류가 발생했습니다",
            recommendation="다시 진단을 시도해주세요",
            issues=[f"측정 중 오류: {type(e).__name__}"],
        )


async def run_scan(
    url: str,
    *,
    max_pages: int = 50,
    max_depth: int = 3,
    check_geo: bool = True,
    hospital_name: str = "",
    specialty: str = "",
    region: str = "",
    hospital_id: str | None = None,
) -> dict:
    """Run full SEO + GEO/AEO scan on a URL. Returns scored results."""
    crawler = Crawler(max_pages=max_pages, max_depth=max_depth)

    # Crawl pages
    pages = await crawler.crawl(url)
    if not pages:
        return {
            "url": url,
            "error": "사이트에 접근할 수 없습니다",
            "total_score": 0,
            "grade": "F",
            "category_scores": {},
        }

    main_page = pages[0]
    crawled_urls = [p.url for p in pages]
    all_results: list[CheckResult] = []

    # Auto-extract hospital name from page title if not provided
    if not hospital_name:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(main_page.html, "lxml")
        title_tag = soup.find("title")
        if title_tag and title_tag.string:
            # Clean title: remove common suffixes like " - 홈페이지", " | 공식 사이트"
            raw_title = title_tag.string.strip()
            for sep in [" - ", " | ", " :: ", " – ", " — "]:
                if sep in raw_title:
                    raw_title = raw_title.split(sep)[0].strip()
                    break
            hospital_name = raw_title

    # Run checks — async checks need an HTTP client
    async with httpx.AsyncClient(
        timeout=settings.crawler_timeout,
        follow_redirects=True,
        headers={"User-Agent": "CheckYourHospital-Bot/1.0"},
    ) as client:
        # Async checks (each wrapped for safety)
        for coro, name in [
            (check_robots(client, url), "robots_txt"),
            (check_sitemap(client, url), "sitemap"),
            (check_https(client, url), "https"),
            (check_links(client, main_page.html, url), "links"),
            (check_errors(client, crawled_urls), "errors_404"),
        ]:
            r = await _safe_check(coro, name)
            if r:
                all_results.append(r)

        # Performance checks (returns 4 results)
        try:
            perf_results = await check_performance(client, url)
            all_results.extend(perf_results)
        except Exception as e:
            logger.error(f"Performance check crashed: {e}")

        # GEO/AEO: AI search mention (async, optional)
        if check_geo:
            for coro, name in [
                (
                    check_ai_search_mention(client, url, hospital_name, specialty, region),
                    "ai_search_mention",
                ),
                (
                    check_international_search(client, url, hospital_name, specialty, region),
                    "international_search",
                ),
            ]:
                r = await _safe_check(coro, name)
                if r:
                    all_results.append(r)

    # Sync checks (HTML parsing, each wrapped for safety)
    for fn, name in [
        (lambda: check_meta_tags(main_page.html, url), "meta_tags"),
        (lambda: check_headings(main_page.html), "headings"),
        (lambda: check_images(main_page.html), "images_alt"),
        (lambda: check_canonical(main_page.html, url), "canonical"),
        (lambda: check_url_structure(url, crawled_urls), "url_structure"),
        (lambda: check_mobile(main_page.html), "mobile"),
        (lambda: check_multilingual_pages(main_page.html, crawled_urls), "multilingual_pages"),
        (lambda: check_hreflang(main_page.html), "hreflang"),
        (lambda: check_overseas_channels(main_page.html), "overseas_channels"),
    ]:
        all_results.append(_safe_sync(fn, name))

    # GEO/AEO: HTML-based checks (sync)
    if check_geo:
        for fn, name in [
            (lambda: check_structured_data(main_page.html), "structured_data"),
            (lambda: check_faq_content(main_page.html), "faq_content"),
            (lambda: check_eeat_signals(main_page.html, url, pages), "eeat_signals"),
            (lambda: check_content_clarity(main_page.html), "content_clarity"),
        ]:
            all_results.append(_safe_sync(fn, name))

    # Multilingual readiness analysis (uses all crawled pages)
    page_dicts = [{"url": p.url, "html": p.html, "status_code": p.status_code} for p in pages]
    multilingual_readiness = analyze_multilingual_readiness(page_dicts)

    # Content freshness analysis
    content_freshness = analyze_content_freshness(page_dicts)

    # Score
    score_data = calculate_score(all_results)

    portal_scores = calculate_portal_scores(score_data.get("category_scores", {}))

    # Regional competitor comparison. This depends on optional Supabase data and
    # must not block the core scan when benchmark tables are unavailable.
    competitor_analysis = None
    try:
        competitor_analysis = await discover_competitors(url, hospital_name=hospital_name)
    except Exception as e:
        logger.error("Competitor discovery crashed: %s", e)

    # Patient journey funnel scores
    patient_journey = calculate_journey_scores(score_data.get("category_scores", {}))

    # Conversion element analysis
    conversion_result = _safe_sync(
        lambda: check_conversion_elements(
            [{"url": p.url, "html": p.html, "status_code": p.status_code} for p in pages]
        ),
        "conversion_elements",
    )
    conversion_analysis = {
        "score": round(conversion_result.score * 100),
        "grade": conversion_result.grade.value,
        **conversion_result.details,
    }

    # Procedure completeness analysis
    procedure_completeness = analyze_procedure_completeness(
        [{"url": p.url, "html": p.html} for p in pages]
    )

    # Medical advertising compliance check
    medical_compliance = check_medical_compliance(
        [{"url": p.url, "html": p.html} for p in pages]
    )

    # Voice search readiness analysis
    voice_search = analyze_voice_search_readiness(
        [{"url": p.url, "html": p.html} for p in pages],
        score_data.get("category_scores", {}),
    )

    # Tech stack detection
    tech_stack = detect_tech_stack(
        [{"url": p.url, "html": p.html} for p in pages]
    )

    # Video presence analysis
    video_presence = analyze_video_presence(
        [{"url": p.url, "html": p.html} for p in pages]
    )

    # International usability analysis
    page_dicts = [{"url": p.url, "html": p.html} for p in pages]
    international_usability = analyze_international_usability(page_dicts, multilingual_readiness)

    # Review sentiment analysis
    review_sentiment = analyze_review_sentiment(
        [{"url": p.url, "html": p.html} for p in pages]
    )

    # Keyword engine: extract procedures and generate search keywords
    generated_keywords = extract_and_generate_keywords(
        [{"url": p.url, "html": p.html} for p in pages],
        region_name=region,
    )

    # Season insight (date-based, no URL dependency)
    season_insight = get_season_insight()

    # Keyword rankings (SERP check) — uses keyword_analysis if available
    keyword_rankings = {}
    keyword_analysis = score_data.get("keyword_analysis", {})
    kw_list = keyword_analysis.get("keywords", [])
    if kw_list:
        try:
            keyword_rankings = await check_keyword_rankings(url, kw_list)
        except Exception as e:
            logger.error("SERP checker crashed: %s", e)

    scan_result = {
        "url": url,
        "pages_crawled": len(pages),
        **score_data,
        "portal_scores": portal_scores,
        "competitor_analysis": competitor_analysis,
        "multilingual_readiness": multilingual_readiness,
        "content_freshness": content_freshness,
        "patient_journey": patient_journey,
        "conversion_analysis": conversion_analysis,
        "procedure_completeness": procedure_completeness,
        "medical_compliance": medical_compliance,
        "voice_search": voice_search,
        "tech_stack": tech_stack,
        "international_usability": international_usability,
        "review_sentiment": review_sentiment,
        "season_insight": season_insight,
        "video_presence": video_presence,
        "generated_keywords": generated_keywords,
        "keyword_rankings": keyword_rankings,
    }

    if hospital_id:
        from .monitoring import record_score_history

        await record_score_history(
            hospital_id=hospital_id,
            audit_id=None,
            total_score=score_data.get("total_score", 0),
            grade=score_data.get("grade", "F"),
            category_scores=score_data.get("category_scores", {}),
        )

    return scan_result
