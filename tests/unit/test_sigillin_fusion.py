"""Tests für genesis_os Sigillin-Fusion — Phase E."""

from __future__ import annotations

import pytest

from genesis_os.aeon.metaquest_bridge import AeonMetaQuestBridge
from genesis_os.aeon.nullkern import Nullkern
from genesis_os.sigillin.metaquest_client import (
    MetaQuestClient,
    MetaQuestResponse,
    compute_tier,
)


class TestMetaQuestTierMapping:
    def test_tier_1_low_phi(self) -> None:
        assert compute_tier(0.0) == 1
        assert compute_tier(0.1) == 1
        assert compute_tier(0.29) == 1

    def test_tier_2_mid_phi(self) -> None:
        assert compute_tier(0.3) == 2
        assert compute_tier(0.5) == 2
        assert compute_tier(0.59) == 2

    def test_tier_3_upper_phi(self) -> None:
        assert compute_tier(0.6) == 3
        assert compute_tier(0.7) == 3
        assert compute_tier(0.84) == 3

    def test_tier_4_high_phi(self) -> None:
        assert compute_tier(0.85) == 4
        assert compute_tier(0.95) == 4
        assert compute_tier(1.0) == 4


class TestMetaQuestLocalFallback:
    def _client(self) -> MetaQuestClient:
        return MetaQuestClient(base_url="http://localhost:9998")

    def test_fallback_returns_response(self) -> None:
        client = self._client()
        responses = client.generate(H=0.5, K=1.0, gamma=0.7)
        assert len(responses) >= 1
        assert isinstance(responses[0], MetaQuestResponse)

    def test_fallback_tier_matches_phi(self) -> None:
        client = self._client()
        responses = client.generate(H=0.8, K=1.0, gamma=0.7)
        assert responses[0].tier == 3

    def test_fallback_phi_computed(self) -> None:
        client = self._client()
        responses = client.generate(H=0.6, K=2.0, gamma=0.5)
        assert responses[0].phi == pytest.approx(0.3)
        assert responses[0].tier == 2

    def test_fallback_entropy_is_1_minus_gamma(self) -> None:
        client = self._client()
        responses = client.generate(H=0.5, K=1.0, gamma=0.7)
        assert responses[0].entropy == pytest.approx(1.0 - 0.7, rel=1e-5)

    def test_fallback_question_contains_phi(self) -> None:
        client = self._client()
        responses = client.generate(H=0.5, K=1.0, gamma=0.7)
        assert "φ=" in responses[0].question or "phi" in responses[0].question.lower()

    def test_tier_4_question_meta_kognition(self) -> None:
        client = self._client()
        responses = client.generate(H=0.9, K=1.0, gamma=0.8)
        assert responses[0].tier == 4
        assert "Meta" in responses[0].question or "meta" in responses[0].question.lower() or "Grenze" in responses[0].question

    def test_close_no_error(self) -> None:
        client = self._client()
        client.close()


class TestAeonMetaQuestBridge:
    def _bridge(self) -> AeonMetaQuestBridge:
        nullkern = Nullkern()
        return AeonMetaQuestBridge(nullkern, metaquest_url="http://localhost:9998")

    def test_tick_returns_response_above_threshold(self) -> None:
        bridge = self._bridge()
        result = bridge.tick(H=0.8, K=1.0, gamma=0.7)
        assert result is not None
        assert isinstance(result, MetaQuestResponse)

    def test_tick_returns_none_below_threshold(self) -> None:
        bridge = self._bridge()
        result = bridge.tick(H=0.1, K=1.0, gamma=0.7)
        assert result is None

    def test_consciousness_log_grows(self) -> None:
        bridge = self._bridge()
        for _ in range(3):
            bridge.tick(H=0.8, K=1.0, gamma=0.7)
        assert len(bridge.consciousness_log) == 3

    def test_consciousness_log_is_copy(self) -> None:
        bridge = self._bridge()
        bridge.tick(H=0.8, K=1.0, gamma=0.7)
        log = bridge.consciousness_log
        log.clear()
        assert len(bridge.consciousness_log) == 1

    def test_current_tier_after_ticks(self) -> None:
        bridge = self._bridge()
        bridge.tick(H=0.8, K=1.0, gamma=0.7)
        assert bridge.current_tier == 3

    def test_current_tier_before_ticks(self) -> None:
        bridge = self._bridge()
        assert bridge.current_tier == 0

    def test_reset_log(self) -> None:
        bridge = self._bridge()
        bridge.tick(H=0.8, K=1.0, gamma=0.7)
        bridge.reset_log()
        assert len(bridge.consciousness_log) == 0
