from __future__ import annotations

import pytest

from bhava360.chart.dignity import DignityState, classify_dignity
from bhava360.chart.vargas import VargaId, assert_d150_accuracy_gate, varga_sign
from bhava360.kernel.errors import KernelError, KernelErrorCode
from bhava360.kernel.models import PlanetName


def test_d9_known_boundaries():
    # 0° Aries movable → D9 starts Aries; first navamsa Aries
    p0 = varga_sign(0.0, VargaId.D9)
    assert p0.sign == "Aries"
    part = 30.0 / 9.0
    # Just below first boundary still Aries
    p1 = varga_sign(part - 1e-9, VargaId.D9)
    assert p1.sign == "Aries"
    # At / just above 3°20' second navamsa Taurus
    p2 = varga_sign(part, VargaId.D9)
    assert p2.sign == "Taurus"


def test_d1_matches_sign():
    p = varga_sign(118.455, VargaId.D1)
    assert p.sign == "Cancer"


def test_sun_exalted_in_aries():
    # Sun at 10° Aries
    d = classify_dignity(PlanetName.SUN, 10.0)
    assert DignityState.EXALTED in d.states
    assert d.primary == DignityState.EXALTED


def test_moon_own_in_cancer():
    d = classify_dignity(PlanetName.MOON, 100.0)  # Cancer 10°
    assert DignityState.OWN in d.states


def test_combustion_candidate_near_sun():
    d = classify_dignity(
        PlanetName.MERCURY,
        120.0,
        sun_longitude_sidereal_deg=118.0,
        combustion_orb_deg=8.4,
    )
    assert d.is_combust_candidate is True


def test_d150_gate_requires_uncertainty():
    with pytest.raises(KernelError) as exc:
        assert_d150_accuracy_gate(None)
    assert exc.value.code == KernelErrorCode.UNSUPPORTED_CONFIG


def test_d150_gate_blocks_large_uncertainty():
    with pytest.raises(KernelError):
        assert_d150_accuracy_gate(5.0, max_uncertainty_minutes=1.0)
