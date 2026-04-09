"""Integration tests — run scenarios and verify assertions pass."""

from __future__ import annotations

import os
import shutil
import tempfile

import pytest

from chamber_sentinel_sim.config import ScenarioConfig
from chamber_sentinel_sim.scenarios.assertions import AssertionEngine
from chamber_sentinel_sim.scenarios.runner import SimulationRunner


SCENARIOS_DIR = os.path.join(os.path.dirname(__file__), "..", "scenarios")


def _run_scenario(yaml_name: str, tmpdir: str) -> tuple[dict, list]:
    path = os.path.join(SCENARIOS_DIR, yaml_name)
    config = ScenarioConfig.load(path)
    output = os.path.join(tmpdir, config.name)
    runner = SimulationRunner(config, output)
    stats = runner.run(verbose=False)
    engine = AssertionEngine(output)
    results = engine.run_all(config.assertions)
    return stats, results


class TestHappyPath:
    def test_scn001(self, tmp_path):
        stats, results = _run_scenario("SCN-001.yaml", str(tmp_path))
        assert stats["items_generated"] > 0
        assert stats["reports_generated"] > 0
        for r in results:
            assert r.passed, f"{r.name} failed: {r.details}"


class TestSensorTransition:
    def test_scn002(self, tmp_path):
        stats, results = _run_scenario("SCN-002.yaml", str(tmp_path))
        assert stats["items_generated"] > 0
        for r in results:
            assert r.passed, f"{r.name} failed: {r.details}"


class TestConsentRevocation:
    def test_scn003(self, tmp_path):
        stats, results = _run_scenario("SCN-003.yaml", str(tmp_path))
        for r in results:
            assert r.passed, f"{r.name} failed: {r.details}"


class TestPortableRecordLoss:
    def test_scn005(self, tmp_path):
        stats, results = _run_scenario("SCN-005.yaml", str(tmp_path))
        for r in results:
            assert r.passed, f"{r.name} failed: {r.details}"


class TestOffline:
    def test_scn006(self, tmp_path):
        stats, results = _run_scenario("SCN-006.yaml", str(tmp_path))
        for r in results:
            assert r.passed, f"{r.name} failed: {r.details}"


class TestEmergencyBurn:
    def test_scn009(self, tmp_path):
        stats, results = _run_scenario("SCN-009.yaml", str(tmp_path))
        for r in results:
            assert r.passed, f"{r.name} failed: {r.details}"


class TestMultiDevice:
    def test_scn010(self, tmp_path):
        stats, results = _run_scenario("SCN-010.yaml", str(tmp_path))
        assert stats["items_generated"] > 0
        assert stats["reports_generated"] > 0
        for r in results:
            assert r.passed, f"{r.name} failed: {r.details}"
