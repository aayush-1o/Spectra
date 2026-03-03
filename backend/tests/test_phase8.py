"""
Phase 8 unit tests:
  test_risk_service.py — risk score computation
  test_nl_search_service.py — NL search filter parsing
  test_anomaly_service.py — new algorithm entries
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

# ── Task 8.2: Risk Score Unit Tests ───────────────────────────────────────────

from app.services.risk_service import compute_risk_score


class TestComputeRiskScore:
    def test_all_zeros(self):
        score = compute_risk_score(
            event_count=0,
            off_hours_pct=0.0,
            max_transfer_usd=0.0,
            anomaly_count=0,
            max_event_count=1,
        )
        assert score == pytest.approx(0.0)

    def test_max_score_is_100(self):
        score = compute_risk_score(
            event_count=100,
            off_hours_pct=1.0,
            max_transfer_usd=50_000.0,
            anomaly_count=10,
            max_event_count=100,
        )
        assert score == pytest.approx(100.0)

    def test_mid_score(self):
        score = compute_risk_score(
            event_count=50,
            off_hours_pct=0.5,
            max_transfer_usd=25_000.0,
            anomaly_count=5,
            max_event_count=100,
        )
        # 25 * 0.5 + 30 * 0.5 + 25 * 0.5 + 20 * 0.5 = 50
        assert score == pytest.approx(50.0)

    def test_clamped_at_100(self):
        # Even with absurd inputs, score must not exceed 100
        score = compute_risk_score(
            event_count=9999,
            off_hours_pct=2.0,  # > 1, should be clamped
            max_transfer_usd=999_999.0,
            anomaly_count=999,
            max_event_count=1,
        )
        assert score <= 100.0

    def test_transfer_cap(self):
        # Transfer of exactly $50,000 => full 25 points
        score_at_cap = compute_risk_score(0, 0.0, 50_000.0, 0, max_event_count=1)
        score_above_cap = compute_risk_score(0, 0.0, 100_000.0, 0, max_event_count=1)
        assert score_at_cap == score_above_cap == pytest.approx(25.0)

    def test_normalisation_by_max_event_count(self):
        score_10_of_100 = compute_risk_score(10, 0.0, 0.0, 0, max_event_count=100)
        score_10_of_10 = compute_risk_score(10, 0.0, 0.0, 0, max_event_count=10)
        # More events relative to max → higher volume score
        assert score_10_of_10 > score_10_of_100


# ── Task 8.6: NL Search Service Tests ────────────────────────────────────────

from app.services.nl_search_service import parse_nl_query


class TestParseNLQuery:
    @pytest.mark.asyncio
    async def test_returns_empty_dict_without_api_key(self):
        """Without ANTHROPIC_API_KEY, parse_nl_query returns empty dict gracefully."""
        with patch("app.services.nl_search_service.settings") as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = ""
            result = await parse_nl_query("find people who transferred money at night")
            assert result == {}

    @pytest.mark.asyncio
    async def test_claude_response_parsed(self):
        """Mock Claude response → filters extracted correctly."""
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text='{"min_transfer_usd": 5000, "after_hour": 22}')]

        with patch("app.services.nl_search_service.settings") as mock_settings, \
             patch("app.services.nl_search_service.anthropic.Anthropic") as mock_anthropic:
            mock_settings.ANTHROPIC_API_KEY = "sk-test-key"
            mock_anthropic.return_value.messages.create.return_value = mock_message
            result = await parse_nl_query("transfers over $5k after 10pm")

        assert result == {"min_transfer_usd": 5000, "after_hour": 22}

    @pytest.mark.asyncio
    async def test_invalid_json_returns_empty(self):
        """If Claude returns non-JSON, result is empty dict."""
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text='not valid json')]

        with patch("app.services.nl_search_service.settings") as mock_settings, \
             patch("app.services.nl_search_service.anthropic.Anthropic") as mock_anthropic:
            mock_settings.ANTHROPIC_API_KEY = "sk-test-key"
            mock_anthropic.return_value.messages.create.return_value = mock_message
            result = await parse_nl_query("some query")

        assert result == {}

    @pytest.mark.asyncio
    async def test_strips_markdown_fences(self):
        """Handles ```json ... ``` wrapping from Claude."""
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text='```json\n{"nationality": "Arcadian"}\n```')]

        with patch("app.services.nl_search_service.settings") as mock_settings, \
             patch("app.services.nl_search_service.anthropic.Anthropic") as mock_anthropic:
            mock_settings.ANTHROPIC_API_KEY = "sk-test-key"
            mock_anthropic.return_value.messages.create.return_value = mock_message
            result = await parse_nl_query("find Arcadians")

        assert result == {"nationality": "Arcadian"}


# ── Task 8.11: Anomaly Algorithm Tests ────────────────────────────────────────

from app.models.anomaly import AnomalyAlgorithm


class TestAnomalyAlgorithmEnum:
    def test_dbscan_in_enum(self):
        assert AnomalyAlgorithm.dbscan.value == "dbscan"

    def test_lof_in_enum(self):
        assert AnomalyAlgorithm.lof.value == "lof"

    def test_night_owl_in_enum(self):
        assert AnomalyAlgorithm.night_owl_rule.value == "night_owl_rule"

    def test_all_algorithms_present(self):
        expected = {
            "isolation_forest", "z_score", "rule_based",
            "dbscan", "lof", "night_owl_rule",
        }
        actual = {a.value for a in AnomalyAlgorithm}
        assert expected == actual
