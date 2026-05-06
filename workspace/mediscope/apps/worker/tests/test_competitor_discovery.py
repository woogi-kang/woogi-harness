"""Tests for regional competitor discovery."""

from types import SimpleNamespace

import pytest

from app.services import competitor_discovery
from app.services.competitor_discovery import (
    _build_insight,
    _calculate_grade,
    _extract_domain,
    discover_competitors,
)


class FakeQuery:
    def __init__(self, data):
        self.data = data
        self.not_ = self

    def select(self, *args, **kwargs):
        return self

    def ilike(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def eq(self, *args, **kwargs):
        return self

    def in_(self, *args, **kwargs):
        return self

    def is_(self, *args, **kwargs):
        return self

    def order(self, *args, **kwargs):
        return self

    def execute(self):
        return SimpleNamespace(data=self.data)


class FakeSupabase:
    def __init__(self, responses):
        self.responses = {table: list(items) for table, items in responses.items()}

    def table(self, name):
        return FakeQuery(self.responses[name].pop(0))


def test_extract_domain_normalizes_urls():
    assert _extract_domain("https://www.example.com/path") == "example.com"
    assert _extract_domain("example.com/path") == "example.com"
    assert _extract_domain("") == ""


def test_calculate_grade():
    assert _calculate_grade(95) == "A"
    assert _calculate_grade(75) == "B"
    assert _calculate_grade(55) == "C"
    assert _calculate_grade(25) == "D"
    assert _calculate_grade(10) == "F"


def test_build_insight_handles_missing_score():
    assert _build_insight(None, None, 3, 80) == "지역 내 3곳의 경쟁 피부과가 있습니다."


@pytest.mark.asyncio
async def test_discover_competitors_builds_region_and_portal_comparison(monkeypatch):
    fake_sb = FakeSupabase(
        {
            "beauty_clinics": [
                [
                    {
                        "id": 1,
                        "name": "내 병원",
                        "sido": "서울",
                        "sggu": "강남구",
                        "website": "https://myclinic.co.kr",
                        "latest_score": 70,
                    }
                ],
                [
                    {
                        "id": 1,
                        "name": "내 병원",
                        "website": "https://myclinic.co.kr",
                        "latest_score": 70,
                        "sggu": "강남구",
                    },
                    {
                        "id": 2,
                        "name": "A 피부과",
                        "website": "https://a-clinic.kr",
                        "latest_score": 90,
                        "sggu": "강남구",
                    },
                    {
                        "id": 3,
                        "name": "B 피부과",
                        "website": "https://b-clinic.kr",
                        "latest_score": 80,
                        "sggu": "서초구",
                    },
                ],
            ],
            "audits": [
                [
                    {
                        "url": "https://a-clinic.kr",
                        "details": {
                            "portal_scores": {
                                "naver": {"score": 90},
                                "google": {"score": 80},
                            }
                        },
                    }
                ],
                [
                    {
                        "url": "https://b-clinic.kr",
                        "details": {
                            "portal_scores": {
                                "naver": {"score": 80},
                                "google": {"score": 75},
                            }
                        },
                    }
                ],
                [
                    {
                        "url": "https://myclinic.co.kr",
                        "details": {
                            "portal_scores": {
                                "naver": {"score": 60},
                                "google": {"score": 70},
                            }
                        },
                    }
                ],
            ],
        }
    )

    monkeypatch.setattr(competitor_discovery, "get_supabase_client", lambda: fake_sb)
    monkeypatch.setattr(
        competitor_discovery,
        "get_region_name",
        lambda sido, sggu: "강남권",
    )
    monkeypatch.setattr(
        competitor_discovery,
        "get_region_sggus",
        lambda region_name: {"강남구", "서초구"},
    )

    result = await discover_competitors("https://myclinic.co.kr")

    assert result is not None
    assert result["region_name"] == "강남권"
    assert result["your_rank"] == 3
    assert result["total_competitors"] == 3
    assert result["top_competitors"][0]["name"] == "A 피부과"
    assert result["regional_avg_score"] == 80
    assert result["portal_comparison"]["naver"]["your"] == 60
    assert result["portal_comparison"]["naver"]["top3_avg"] == 76.7
    assert result["portal_comparison"]["naver"]["gap"] == -17
    assert "3곳 중 3위" in result["insight"]


@pytest.mark.asyncio
async def test_discover_competitors_returns_none_without_supabase(monkeypatch):
    monkeypatch.setattr(competitor_discovery, "get_supabase_client", lambda: None)

    assert await discover_competitors("https://myclinic.co.kr") is None
