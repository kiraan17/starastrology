from __future__ import annotations

from datetime import datetime

import pytest

from bhava360.engines.evidence import RuleOutcome
from bhava360.engines.kp.config_rules import evaluate_kp_config_isolation
from bhava360.engines.kp.engine import run_kp_engine
from bhava360.engines.kp.lords import kp_lord_chain
from bhava360.kernel.derived import NAKSHATRA_SPAN
from bhava360.kernel.errors import KernelError, KernelErrorCode
from bhava360.kernel.models import AyanamsaMode, ChartConfig, HouseSystem, PlanetName, SubjectInput
from bhava360.timing.vimshottari import VIMSHOTTARI_YEARS, TOTAL_YEARS


def test_ashwini_start_star_lord_ketu_and_first_sub_ketu():
    chain = kp_lord_chain(0.0)
    assert chain.nakshatra == "Aswini"
    assert chain.star_lord == PlanetName.KETU
    assert chain.sub_lord == PlanetName.KETU


def test_sub_lord_changes_after_ketu_portion():
    # Ketu sub spans 7/120 of nakshatra.
    ketu_span = NAKSHATRA_SPAN * VIMSHOTTARI_YEARS[PlanetName.KETU] / TOTAL_YEARS
    before = kp_lord_chain(ketu_span - 1e-9)
    after = kp_lord_chain(ketu_span + 1e-9)
    assert before.sub_lord == PlanetName.KETU
    assert after.sub_lord == PlanetName.VENUS
    assert before.star_lord == after.star_lord == PlanetName.KETU


def test_kp_config_isolation_accepts_kp_placidus():
    ev = evaluate_kp_config_isolation(
        {"ayanamsa": "kp", "house_system": "placidus", "kp_allow_nonstandard_config": False}
    )
    assert ev.outcome == RuleOutcome.MATCHED


def test_kp_config_isolation_rejects_lahiri_wholesign():
    ev = evaluate_kp_config_isolation(
        {"ayanamsa": "lahiri", "house_system": "whole_sign", "kp_allow_nonstandard_config": False}
    )
    assert ev.outcome == RuleOutcome.FAILED


def test_run_kp_engine_rejects_wrong_config():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_offset_minutes=330,
        latitude=13.0827,
        longitude=80.2707,
    )
    with pytest.raises(KernelError) as exc:
        run_kp_engine(
            subject,
            config=ChartConfig(ayanamsa=AyanamsaMode.LAHIRI, house_system=HouseSystem.WHOLE_SIGN),
        )
    assert exc.value.code == KernelErrorCode.UNSUPPORTED_CONFIG


def test_run_kp_engine_happy_path_chains():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_offset_minutes=330,
        latitude=13.0827,
        longitude=80.2707,
        location_label="Chennai",
    )
    out = run_kp_engine(subject)
    assert out["engine"] == "KP"
    assert out["config_isolation"]["outcome"] == "matched"
    assert out["chart"]["config"]["ayanamsa"] == "kp"
    assert out["chart"]["config"]["house_system"] == "placidus"
    assert "Sun" in out["planet_lord_chains"]
    assert set(out["planet_lord_chains"]["Sun"]) >= {
        "star_lord",
        "sub_lord",
        "sub_sub_lord",
        "nakshatra",
    }
    assert len(out["cuspal_lord_chains"]) == 12
    assert "significators" in out["cuspal_lord_chains"][0]
