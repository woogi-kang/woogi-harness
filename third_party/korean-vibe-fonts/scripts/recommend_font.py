#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = BASE_DIR / "references" / "font_catalog.json"

TAG_LABELS = {
    "accent": "포인트",
    "ai": "AI",
    "art": "아트",
    "b2b": "B2B",
    "bold": "강한 존재감",
    "brand": "브랜드감",
    "campaign": "캠페인",
    "casual": "캐주얼",
    "clean": "깔끔함",
    "code": "코드 친화",
    "community": "커뮤니티",
    "condensed": "좁고 밀도 높은 타이틀",
    "cozy": "포근함",
    "culture": "문화/에디토리얼",
    "cute": "귀여움",
    "dashboard": "대시보드",
    "data": "데이터 제품",
    "developer": "개발자 감성",
    "display": "디스플레이 타이틀",
    "docs": "문서형",
    "ecommerce": "이커머스",
    "editorial": "에디토리얼",
    "energetic": "활기",
    "enterprise": "엔터프라이즈",
    "essay": "에세이",
    "experimental": "실험적 무드",
    "family": "가족형 서비스",
    "friendly": "친근함",
    "gaming": "게임 감성",
    "geometric": "기하학적 리듬",
    "gentle": "부드러움",
    "handwritten": "손글씨",
    "hackathon": "해커톤",
    "hero": "히어로 섹션",
    "impact": "강한 임팩트",
    "institution": "기관/공신력",
    "international": "다국어 대응",
    "landing": "랜딩 페이지",
    "legal": "정책/법률형",
    "lifestyle": "라이프스타일",
    "literary": "문학적",
    "luxury": "럭셔리",
    "minimal": "미니멀",
    "mobile": "모바일 친화",
    "modern": "모던",
    "monospace": "고정폭",
    "multilingual": "다국어",
    "music": "뮤직/스트리트",
    "neutral": "중립적",
    "onboarding": "온보딩",
    "orderly": "정돈된 구조",
    "personal": "개인적 무드",
    "playful": "발랄함",
    "poetic": "시적인 여백",
    "portfolio": "포트폴리오",
    "poster": "포스터성",
    "premium": "프리미엄",
    "product": "프로덕트 UI",
    "promo": "프로모션",
    "readable": "가독성",
    "safe": "안전한 기본값",
    "saas": "SaaS",
    "serene": "잔잔함",
    "serif": "부리체",
    "soft": "부드러움",
    "sporty": "스포티함",
    "startup": "스타트업",
    "story": "브랜드 스토리",
    "support": "헬프/지원",
    "tech": "테크",
    "technical": "기술적",
    "terminal": "터미널",
    "trust": "신뢰감",
    "ui": "UI 중심",
    "versatile": "범용성",
    "warm": "온기",
    "wellness": "웰니스",
    "youth": "젊은 무드"
}

TAG_SYNONYMS = {
    "ai": ["ai", "인공지능", "llm", "agent", "에이전트"],
    "art": ["art", "아트", "전시", "갤러리"],
    "b2b": ["b2b", "기업용", "엔터프라이즈", "saas"],
    "bold": ["bold", "강렬", "묵직", "강한", "헤비"],
    "brand": ["brand", "브랜드", "브랜딩", "identity"],
    "campaign": ["campaign", "캠페인", "이벤트", "프로모션"],
    "casual": ["casual", "캐주얼", "편안", "가벼운"],
    "clean": ["clean", "깔끔", "정갈", "단정", "미니멀", "심플"],
    "code": ["code", "코드", "개발", "코딩", "terminal", "cli"],
    "community": ["community", "커뮤니티", "포럼", "소셜"],
    "condensed": ["condensed", "압축", "좁은", "빽빽"],
    "cozy": ["cozy", "포근", "아늑", "따뜻", "cozy"],
    "culture": ["culture", "문화", "예술", "아카이브"],
    "cute": ["cute", "귀여운", "아기자기", "러블리"],
    "dashboard": ["dashboard", "대시보드", "admin", "운영툴", "관리자"],
    "data": ["data", "analytics", "분석", "지표", "메트릭"],
    "developer": ["developer", "dev", "개발자", "엔지니어"],
    "display": ["display", "타이틀", "히어로", "헤드라인"],
    "docs": ["docs", "문서", "가이드", "헬프", "knowledge base"],
    "ecommerce": ["ecommerce", "commerce", "쇼핑", "세일", "특가", "상품"],
    "editorial": ["editorial", "에디토리얼", "잡지", "매거진", "저널"],
    "energetic": ["energetic", "활기", "역동", "에너지"],
    "enterprise": ["enterprise", "엔터프라이즈", "대기업", "기업"],
    "essay": ["essay", "에세이", "수필", "긴 글"],
    "experimental": ["experimental", "실험적", "독특", "파격"],
    "family": ["family", "가족", "패밀리", "키즈"],
    "friendly": ["friendly", "친근", "편한", "접근성 높은"],
    "gaming": ["gaming", "game", "게임", "esports"],
    "geometric": ["geometric", "기하학", "직선", "각진"],
    "gentle": ["gentle", "잔잔", "순한", "은은"],
    "handwritten": ["handwritten", "손글씨", "메모", "낙서", "다이어리"],
    "hackathon": ["hackathon", "해커톤"],
    "hero": ["hero", "히어로", "첫 화면"],
    "impact": ["impact", "임팩트", "강한 존재감", "펀치"],
    "institution": ["institution", "기관", "공공", "정책", "정부"],
    "international": ["global", "국제", "다국어", "멀티랭귀지", "multilingual"],
    "landing": ["landing", "랜딩", "마이크로사이트", "프로모션 페이지"],
    "legal": ["legal", "법률", "약관", "정책"],
    "lifestyle": ["lifestyle", "라이프스타일", "취향", "리빙"],
    "literary": ["literary", "문학", "시집", "소설"],
    "luxury": ["luxury", "럭셔리", "고급", "하이엔드", "프리미엄"],
    "minimal": ["minimal", "미니멀", "절제", "군더더기 없는"],
    "mobile": ["mobile", "모바일", "앱"],
    "modern": ["modern", "모던", "현대적", "세련"],
    "multilingual": ["multilingual", "다국어", "영문혼용"],
    "music": ["music", "뮤직", "힙합", "스트리트", "k-pop"],
    "neutral": ["neutral", "중립", "무난", "기본"],
    "onboarding": ["onboarding", "온보딩", "가입", "시작하기"],
    "orderly": ["orderly", "질서정연", "정돈된", "구조적"],
    "personal": ["personal", "개인적", "개인 브랜드", "1인"],
    "playful": ["playful", "발랄", "유쾌", "장난스러운", "재미있는"],
    "poetic": ["poetic", "시적인", "감성적", "서정적"],
    "portfolio": ["portfolio", "포트폴리오", "작업물"],
    "poster": ["poster", "포스터", "전단", "배너"],
    "premium": ["premium", "프리미엄", "고급", "브랜드 스토리"],
    "product": ["product", "프로덕트", "서비스", "웹앱", "제품"],
    "promo": ["promo", "프로모", "할인", "런칭", "launch"],
    "readable": ["readable", "가독성", "읽기 쉬운", "본문"],
    "safe": ["safe", "안전", "무난", "보편적"],
    "saas": ["saas", "서비스형 소프트웨어", "b2b saas"],
    "serene": ["serene", "고요", "차분", "잔잔"],
    "serif": ["serif", "명조", "부리", "세리프"],
    "soft": ["soft", "부드", "말랑", "라운드"],
    "sporty": ["sporty", "스포티", "속도감", "역동적"],
    "startup": ["startup", "스타트업", "런칭", "early-stage"],
    "story": ["story", "스토리", "서사", "브랜드 소개"],
    "support": ["support", "지원", "고객센터", "faq"],
    "tech": ["tech", "테크", "기술", "엔지니어링"],
    "technical": ["technical", "기술적", "공학적", "정밀한"],
    "terminal": ["terminal", "터미널", "명령줄", "cli"],
    "trust": ["trust", "신뢰", "공신력", "안정감"],
    "ui": ["ui", "인터페이스", "앱", "웹서비스"],
    "versatile": ["versatile", "범용", "어디든", "올라운드"],
    "warm": ["warm", "온기", "따뜻", "감성"],
    "wellness": ["wellness", "웰니스", "명상", "건강", "힐링"],
    "youth": ["youth", "젊은", "z세대", "학생", "영한"]
}

PROFILE_DEFS = {
    "product": {
        "label": "제품형/모던 UI",
        "tags": ["modern", "clean", "ui", "product", "startup", "saas", "ai", "dashboard", "tech", "developer", "b2b"]
    },
    "editorial": {
        "label": "에디토리얼/브랜드 스토리",
        "tags": ["editorial", "serif", "story", "essay", "literary", "luxury", "premium", "culture", "poetic", "warm"]
    },
    "playful": {
        "label": "친근/발랄/생활형",
        "tags": ["playful", "cute", "friendly", "community", "family", "wellness", "lifestyle", "cozy", "soft", "handwritten", "youth"]
    },
    "impact": {
        "label": "강한 캠페인/프로모션",
        "tags": ["display", "impact", "poster", "promo", "campaign", "gaming", "music", "ecommerce", "sporty", "energetic", "condensed"]
    }
}

PROFILE_RECIPES = {
    "product": {
        "body": ["pretendard-variable", "spoqa-han-sans-neo", "goorm-sans", "ibm-plex-sans-kr", "noto-sans-kr", "nanum-gothic", "nanum-square", "nanum-square-neo", "gmarket-sans"],
        "heading": ["nanum-square-neo", "gmarket-sans", "goorm-sans", "pretendard-variable", "spoqa-han-sans-neo", "ibm-plex-sans-kr", "nanum-square", "noto-sans-kr"],
        "code": ["nanum-gothic-coding"]
    },
    "editorial": {
        "body": ["maruburi", "noto-serif-kr", "hahmlet", "gowun-batang", "gowun-dodum"],
        "heading": ["hahmlet", "maruburi", "noto-serif-kr", "gowun-batang", "nanum-square-neo"],
        "code": []
    },
    "playful": {
        "body": ["nanum-square-round", "gowun-dodum", "nanum-square", "goorm-sans", "noto-sans-kr"],
        "heading": ["yg-jalnan", "jua", "nanum-square-round", "single-day", "gaegu", "nanum-pen", "nanum-square"],
        "code": []
    },
    "impact": {
        "body": ["pretendard-variable", "gmarket-sans", "spoqa-han-sans-neo", "noto-sans-kr", "nanum-square", "ibm-plex-sans-kr"],
        "heading": ["black-han-sans", "do-hyeon", "yg-jalnan", "gmarket-sans", "nanum-square-neo", "jua", "pretendard-variable"],
        "code": ["nanum-gothic-coding"]
    }
}

TECH_TAGS = {
    "ai",
    "b2b",
    "code",
    "dashboard",
    "data",
    "developer",
    "docs",
    "product",
    "saas",
    "startup",
    "tech",
    "technical",
    "terminal"
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Recommend commercially usable Korean webfonts by vibe and emit paste-ready CSS."
    )
    parser.add_argument("--theme", required=True, help="Theme, vibe, or page description.")
    parser.add_argument(
        "--catalog",
        default=str(DEFAULT_CATALOG),
        help="Path to font_catalog.json. Defaults to the bundled catalog."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit structured JSON instead of Markdown."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=3,
        help="Number of alternative fonts to include."
    )
    return parser.parse_args()


def load_catalog(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_text(text: str) -> str:
    lowered = text.lower()
    lowered = re.sub(r"[^0-9a-zA-Z가-힣\s\-_/]", " ", lowered)
    lowered = re.sub(r"\s+", " ", lowered).strip()
    return lowered


def derive_tags(theme: str) -> list[str]:
    normalized = normalize_text(theme)
    tags = set()
    for tag, synonyms in TAG_SYNONYMS.items():
        if any(syn in normalized for syn in synonyms):
            tags.add(tag)

    if "ai" in tags or "developer" in tags or "technical" in tags:
        tags.update({"product", "tech"})
    if "luxury" in tags:
        tags.add("premium")
    if "campaign" in tags or "promo" in tags:
        tags.add("impact")
    if "poetic" in tags or "literary" in tags:
        tags.update({"editorial", "serif"})
    if "cute" in tags:
        tags.add("playful")
    if "safe" in tags and "modern" not in tags:
        tags.add("neutral")

    if not tags:
        tags.update({"modern", "clean", "product", "ui"})

    return sorted(tags)


def choose_profile(tags: list[str]) -> str:
    scored: list[tuple[int, int, str]] = []
    profile_order = ["product", "editorial", "playful", "impact"]
    tag_set = set(tags)
    for index, profile in enumerate(profile_order):
        matched = sum(1 for tag in PROFILE_DEFS[profile]["tags"] if tag in tag_set)
        scored.append((matched, -index, profile))
    return max(scored)[2]


def score_font(font: dict[str, Any], tags: set[str], role: str) -> int:
    font_tags = set(font["tags"])
    roles = set(font["roles"])
    overlap = len(font_tags & tags)
    score = overlap * 4

    if role in roles:
        score += 8
    if role == "body" and "body" in roles:
        score += 5
    if role == "heading" and "heading" in roles:
        score += 4
    if role == "code" and "code" in roles:
        score += 12

    if role == "body":
        if "heading" in roles and "body" not in roles:
            score -= 10
        if "code" in roles:
            score -= 14
        if "serif" in font_tags and not tags.intersection({"editorial", "serif", "premium", "luxury", "essay", "culture", "story", "poetic"}):
            score -= 5
        if tags.intersection({"product", "dashboard", "developer", "saas", "ai", "tech", "docs"}) and font_tags.intersection({"modern", "technical", "safe", "readable", "product", "ui", "neutral"}):
            score += 4
        if tags.intersection({"playful", "cute", "community", "wellness", "soft"}) and font_tags.intersection({"friendly", "soft", "cozy", "community"}):
            score += 4
        if tags.intersection({"editorial", "serif", "story", "luxury", "premium"}) and font_tags.intersection({"editorial", "serif", "warm", "poetic", "literary"}):
            score += 5

    if role == "heading":
        if "code" in roles:
            score -= 8
        if tags.intersection({"campaign", "promo", "poster", "gaming", "music", "impact", "sporty", "ecommerce"}) and font_tags.intersection({"display", "impact", "poster", "promo", "condensed", "bold"}):
            score += 6
        if tags.intersection({"playful", "cute", "handwritten", "family", "community"}) and font_tags.intersection({"playful", "handwritten", "youth", "friendly", "cute"}):
            score += 6
        if tags.intersection({"editorial", "serif", "luxury", "literary", "premium"}) and font_tags.intersection({"editorial", "serif", "literary", "premium", "poetic"}):
            score += 5
        if tags.intersection({"product", "startup", "ai", "tech", "dashboard"}) and font_tags.intersection({"modern", "geometric", "brand", "hero", "tech"}):
            score += 5

    if role == "code":
        if font_tags.intersection({"code", "monospace", "developer", "technical", "terminal"}):
            score += 8

    score += int(font.get("stability_bonus", 0))
    return score


def ranked_fonts(
    catalog: dict[str, Any],
    candidate_ids: list[str],
    tags: list[str],
    role: str
) -> list[dict[str, Any]]:
    font_map = {font["id"]: font for font in catalog["fonts"]}
    tag_set = set(tags)
    ranked = []
    for order, font_id in enumerate(candidate_ids):
        font = font_map[font_id]
        if font.get("automatic_webfont_recommendation", True) is False:
            continue
        score = score_font(font, tag_set, role)
        ranked.append((score, -order, font))
    ranked.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [item[2] for item in ranked]


def use_code_font(tags: list[str]) -> bool:
    return bool(set(tags) & TECH_TAGS)


def format_reason(font: dict[str, Any], tags: list[str]) -> str:
    overlap = [tag for tag in font["tags"] if tag in set(tags)]
    if not overlap:
        return font["tone_note"]
    labels = [TAG_LABELS.get(tag, tag) for tag in overlap[:4]]
    return f"{font['tone_note']} 핵심 태그: {', '.join(labels)}."


def render_styles(selected: dict[str, dict[str, Any]]) -> dict[str, Any]:
    stylesheets: list[str] = []
    setup_notes: list[str] = []
    seen = set()
    for font in selected.values():
        if not font:
            continue
        key = font.get("stylesheet_url") or font["id"]
        integration = font.get("integration", {})
        snippet = integration.get("html_link") or integration.get("style_tag")
        if key not in seen:
            if snippet:
                stylesheets.append(snippet)
            note = integration.get("setup_note")
            if note:
                setup_notes.append(f"{font['name']}: {note}")
            seen.add(key)

    lines = [":root {"]

    body = selected.get("body")
    heading = selected.get("heading")
    code = selected.get("code")

    if body:
        lines.append(f"  --font-body: {body['application']['body_family']};")
    if heading:
        heading_family = heading["application"].get("heading_family", heading["application"].get("body_family", "inherit"))
        lines.append(f"  --font-heading: {heading_family};")
    if code:
        code_family = code["application"].get("code_family", code["application"].get("code_family_ligature"))
        lines.append(f"  --font-code: {code_family};")
    lines.append("}")
    lines.append("")

    if body:
        lines.append("body {")
        lines.append("  font-family: var(--font-body);")
        lines.append(f"  font-weight: {body['application'].get('body_weight', 400)};")
        lines.append("}")
        lines.append("")

    if heading:
        lines.append("h1, h2, h3, h4, .display, .headline {")
        lines.append("  font-family: var(--font-heading);")
        lines.append(f"  font-weight: {heading['application'].get('heading_weight', 700)};")
        lines.append("  letter-spacing: -0.02em;")
        lines.append("}")
        lines.append("")

    if code:
        lines.append("code, pre, kbd, samp {")
        lines.append("  font-family: var(--font-code);")
        lines.append(f"  font-weight: {code['application'].get('code_weight', 400)};")
        lines.append("}")

    return {
        "stylesheets": stylesheets,
        "setup_notes": setup_notes,
        "css": "\n".join(lines).strip()
    }


def build_recommendation(catalog: dict[str, Any], theme: str, limit: int) -> dict[str, Any]:
    tags = derive_tags(theme)
    profile = choose_profile(tags)
    recipe = PROFILE_RECIPES[profile]

    body_rank = ranked_fonts(catalog, recipe["body"], tags, "body")
    body = body_rank[0]

    heading_rank = ranked_fonts(catalog, recipe["heading"], tags, "heading")
    heading = next((font for font in heading_rank if font["id"] != body["id"]), heading_rank[0])

    code = None
    if use_code_font(tags) and recipe["code"]:
        code_rank = ranked_fonts(catalog, recipe["code"], tags, "code")
        code = code_rank[0]

    alternatives = []
    chosen_ids = {body["id"], heading["id"]}
    if code:
        chosen_ids.add(code["id"])

    union_candidates = []
    union_candidates.extend(body_rank)
    union_candidates.extend(heading_rank)
    if recipe["code"]:
        union_candidates.extend(ranked_fonts(catalog, recipe["code"], tags, "code"))

    for font in union_candidates:
        if font["id"] in chosen_ids:
            continue
        if font["id"] in [item["id"] for item in alternatives]:
            continue
        alternatives.append(font)
        if len(alternatives) >= limit:
            break

    selected = {"body": body, "heading": heading, "code": code}
    rendered = render_styles(selected)

    return {
        "theme": theme,
        "derived_tags": tags,
        "profile": {
            "id": profile,
            "label": PROFILE_DEFS[profile]["label"]
        },
        "consistency_rule": "Keep the same font family for the same text role across screens or slides.",
        "role_map": {
            "heading": "page title, slide title, section heading, hero headline",
            "body": "paragraph, bullet, subtitle, caption, label, table text",
            "code": "code block, terminal, CLI snippet"
        },
        "selected": {
            "body": {
                "id": body["id"],
                "name": body["name"],
                "reason": format_reason(body, tags)
            },
            "heading": {
                "id": heading["id"],
                "name": heading["name"],
                "reason": format_reason(heading, tags)
            },
            "code": None if not code else {
                "id": code["id"],
                "name": code["name"],
                "reason": format_reason(code, tags)
            }
        },
        "stylesheets": rendered["stylesheets"],
        "setup_notes": rendered["setup_notes"],
        "css": rendered["css"],
        "alternatives": [
            {
                "id": font["id"],
                "name": font["name"],
                "reason": format_reason(font, tags)
            }
            for font in alternatives
        ]
    }


def render_markdown(result: dict[str, Any]) -> str:
    parts = []
    parts.append(f"Theme: {result['theme']}")
    parts.append(f"Detected profile: {result['profile']['label']}")
    parts.append(f"Derived tags: {', '.join(result['derived_tags'])}")
    parts.append("")
    parts.append("Recommended set")
    parts.append(f"- Body: {result['selected']['body']['name']} - {result['selected']['body']['reason']}")
    parts.append(f"- Heading: {result['selected']['heading']['name']} - {result['selected']['heading']['reason']}")
    if result["selected"]["code"]:
        parts.append(f"- Code: {result['selected']['code']['name']} - {result['selected']['code']['reason']}")
    parts.append("")
    parts.append("Consistency rule")
    parts.append(f"- {result['consistency_rule']}")
    parts.append(f"- Heading role: {result['role_map']['heading']}")
    parts.append(f"- Body role: {result['role_map']['body']}")
    parts.append(f"- Code role: {result['role_map']['code']}")
    parts.append("")
    parts.append("Stylesheets")
    for line in result["stylesheets"]:
        parts.append("```html")
        parts.append(line)
        parts.append("```")
    if result["setup_notes"]:
        parts.append("")
        parts.append("Setup notes")
        for note in result["setup_notes"]:
            parts.append(f"- {note}")
    parts.append("")
    parts.append("CSS")
    parts.append("```css")
    parts.append(result["css"])
    parts.append("```")
    if result["alternatives"]:
        parts.append("")
        parts.append("Alternatives")
        for alt in result["alternatives"]:
            parts.append(f"- {alt['name']} - {alt['reason']}")
    return "\n".join(parts)


def main() -> int:
    args = parse_args()
    catalog = load_catalog(args.catalog)
    recommendation = build_recommendation(catalog, args.theme, args.limit)
    if args.json:
        json.dump(recommendation, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0

    print(render_markdown(recommendation))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
