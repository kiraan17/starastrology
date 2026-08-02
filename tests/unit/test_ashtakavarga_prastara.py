"""Tests for Prastara Ashtakavarga (P12c)."""

from __future__ import annotations

from datetime import datetime

from bhava360.engines.ashtakavarga.engine import run_ashtakavarga_engine
from bhava360.engines.ashtakavarga.prastara import (
    compute_prastara_ashtakavarga,
    kakshya_bindu_active,
)
from bhava360.engines.ashtakavarga.tables import (
    KAKSHYA_LORD_NAMES,
    compute_bhinna_ashtakavarga,
)
from bhava360.kernel.models import PlanetName, SubjectInput

FIXED_SIGNS = {
    "Sun": "Cancer",
    "Moon": "Taurus",
    "Mars": "Aries",
    "Mercury": "Leo",
    "Jupiter": "Cancer",
    "Venus": "Cancer",
    "Saturn": "Sagittarius",
}
LAGNA = "Libra"


def test_prastara_reconstructs_bav_sign_totals():
    bav = compute_bhinna_ashtakavarga(
        planet_signs=FIXED_SIGNS,
        lagna_sign=LAGNA,
        target=PlanetName.SUN,
    )
    out = compute_prastara_ashtakavarga(
        planet_signs=FIXED_SIGNS,
        lagna_sign=LAGNA,
        target=PlanetName.SUN,
    )
    sun = out["by_planet"]["Sun"]
    assert sun["reconstruction_ok"] is True
    assert sun["prastara"]["contributor_order"] == list(KAKSHYA_LORD_NAMES)
    assert sun["prastara"]["sign_totals_from_prastara"] == bav["sign_bindus"]
    # Each cell is binary.
    for contrib, row in sun["prastara"]["grid"].items():
        for sign, val in row.items():
            assert val in (0, 1)
            assert val == (1 if bav["bindus_by_contributor"][contrib][sign] > 0 else 0)


def test_prastara_all_seven_planets():
    out = compute_prastara_ashtakavarga(planet_signs=FIXED_SIGNS, lagna_sign=LAGNA)
    assert set(out["by_planet"]) == {
        "Sun",
        "Moon",
        "Mars",
        "Mercury",
        "Jupiter",
        "Venus",
        "Saturn",
    }
    assert all(v["reconstruction_ok"] for v in out["by_planet"].values())


def test_kakshya_bindu_active_uses_prastara_cell():
    out = compute_prastara_ashtakavarga(
        planet_signs=FIXED_SIGNS,
        lagna_sign=LAGNA,
        target=PlanetName.SUN,
    )
    grid = out["by_planet"]["Sun"]["prastara"]["grid"]
    # Degree 0 → Saturn kakshya
    hit = kakshya_bindu_active(prastara_grid=grid, sign="Aries", sign_degree=0.0)
    assert hit["kakshya_lord"] == "Saturn"
    assert hit["kakshya_lord_bindu"] == (grid["Saturn"]["Aries"] == 1)


def test_engine_includes_prastara():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_id="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
        location_label="Chennai",
    )
    out = run_ashtakavarga_engine(subject)
    assert out["engine_version"] == "0.3.0-prastara"
    assert "TEC-050" in out["technique_ids"]
    assert "prastara" in out
    assert out["prastara"]["by_planet"]["Sun"]["reconstruction_ok"] is True
    assert "kakshya_lord_bindu" in out["natal_sign_scores"]["Sun"]
