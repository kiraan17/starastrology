from __future__ import annotations

from datetime import datetime

from bhava360.engines.ashtakavarga.engine import run_ashtakavarga_engine
from bhava360.engines.ashtakavarga.tables import (
    BAV_PLANETS,
    compute_bhinna_ashtakavarga,
    compute_sarva_ashtakavarga,
    kakshya_for_longitude,
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


def test_bav_total_reconstructible_from_contributions():
    bav = compute_bhinna_ashtakavarga(
        planet_signs=FIXED_SIGNS,
        lagna_sign=LAGNA,
        target=PlanetName.SUN,
    )
    assert bav["reconstruction_ok"] is True
    assert bav["total_bindus"] == bav["reconstructed_from_contributions"]
    assert sum(bav["sign_bindus"].values()) == bav["total_bindus"]
    # Each contribution lands in the counted sign.
    rebuilt = {s: 0 for s in bav["sign_bindus"]}
    for c in bav["contributions"]:
        rebuilt[c["to_sign"]] += 1
    assert rebuilt == bav["sign_bindus"]


def test_sav_is_sum_of_seven_bavs():
    sav = compute_sarva_ashtakavarga(planet_signs=FIXED_SIGNS, lagna_sign=LAGNA)
    manual = {s: 0 for s in sav["sign_bindus"]}
    for p in BAV_PLANETS:
        bav = sav["bhinnas"][p.value]
        assert bav["reconstruction_ok"] is True
        for sign, n in bav["sign_bindus"].items():
            manual[sign] += n
    assert manual == sav["sign_bindus"]
    # Classical total of all bindus across 7 BAVs is typically 337.
    assert sav["total_bindus"] == 337


def test_kakshya_boundaries():
    assert kakshya_for_longitude(0.0)["kakshya_lord"] == "Saturn"
    assert kakshya_for_longitude(3.75 - 1e-9)["kakshya_index"] == 1
    assert kakshya_for_longitude(3.75)["kakshya_index"] == 2
    assert kakshya_for_longitude(3.75)["kakshya_lord"] == "Jupiter"
    assert kakshya_for_longitude(29.9)["kakshya_index"] == 8


def test_run_ashtakavarga_engine_live_chart():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_offset_minutes=330,
        latitude=13.0827,
        longitude=80.2707,
        location_label="Chennai",
    )
    out = run_ashtakavarga_engine(subject)
    assert out["engine"] == "Ashtakavarga"
    assert out["engine_version"] == "0.3.0-prastara"
    assert out["sarvashtakavarga"]["total_bindus"] == 337
    assert "Sun" in out["bhinnashtakavarga"]
    assert out["bhinnashtakavarga"]["Sun"]["reconstruction_ok"] is True
    assert "Sun" in out["natal_sign_scores"]
    assert "kakshya" in out["natal_sign_scores"]["Sun"]
    assert "prastara" in out
