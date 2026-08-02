"""Shadbala components — Candidate TEC-023 (P27b + P28a)."""

from __future__ import annotations

import math
from datetime import datetime, timedelta
from typing import Any

from bhava360.chart.aspects import GRAHA_ASPECT_HOUSES, relative_house
from bhava360.chart.dignity import (
    DEBILITATION_SIGN,
    EXALTATION_DEGREE,
    MOOLATRIKONA_RANGE,
    OWN_SIGNS,
    sign_lord,
)
from bhava360.chart.vargas import VargaId, varga_sign
from bhava360.kernel.derived import normalize_longitude
from bhava360.kernel.models import PlanetName, SIGNS
from bhava360.timing.panchanga import VARA_LORDS, lunar_elongation_deg

SHADBALA_VARIANT = "shadbala_chesta_motion_candidate_v1"

CLASSICAL_PLANETS: tuple[str, ...] = (
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
)

NAISARGIKA_VIRUPA: dict[str, float] = {
    "Sun": 60.0,
    "Moon": 51.428571,
    "Venus": 42.857143,
    "Jupiter": 34.285714,
    "Mercury": 25.714286,
    "Mars": 17.142857,
    "Saturn": 8.571429,
}

DIG_STRONG_HOUSE: dict[str, int] = {
    "Sun": 10,
    "Mars": 10,
    "Jupiter": 1,
    "Mercury": 1,
    "Moon": 4,
    "Venus": 4,
    "Saturn": 7,
}

FULL_MINIMUM_VIRUPA: dict[str, float] = {
    "Sun": 390.0,
    "Moon": 360.0,
    "Mars": 300.0,
    "Mercury": 420.0,
    "Jupiter": 390.0,
    "Venus": 330.0,
    "Saturn": 300.0,
}

MALE_PLANETS = frozenset({"Sun", "Mars", "Jupiter"})
FEMALE_PLANETS = frozenset({"Moon", "Venus"})
NEUTRAL_OJAYUGMA = frozenset({"Mercury", "Saturn"})

DAY_STRONG = frozenset({"Sun", "Jupiter", "Venus"})
NIGHT_STRONG = frozenset({"Moon", "Mars", "Saturn"})
NATURAL_BENEFICS = frozenset({"Jupiter", "Venus", "Mercury", "Moon"})
NATURAL_MALEFICS = frozenset({"Sun", "Mars", "Saturn"})
CHESTA_MOTION_PLANETS = frozenset({"Mars", "Mercury", "Jupiter", "Venus", "Saturn"})

# Mean sidereal daily motion (°/day) for Saravali Chesta speed bands (Candidate).
MEAN_DAILY_MOTION_DEG: dict[str, float] = {
    "Mars": 0.524,
    "Mercury": 1.383,
    "Jupiter": 0.0831,
    "Venus": 1.200,
    "Saturn": 0.0335,
}

# Saptavarga set for Saptavargaja Bala (Saravali / BPHS overview).
SAPTAVARGA_IDS: tuple[str, ...] = ("D1", "D2", "D3", "D7", "D9", "D12", "D30")

# Permanent natural friendship (Candidate; temporal / Adhi-mitra deferred).
_PERM_FRIENDS: dict[str, frozenset[str]] = {
    "Sun": frozenset({"Moon", "Mars", "Jupiter"}),
    "Moon": frozenset({"Sun", "Mercury"}),
    "Mars": frozenset({"Sun", "Moon", "Jupiter"}),
    "Mercury": frozenset({"Sun", "Venus"}),
    "Jupiter": frozenset({"Sun", "Moon", "Mars"}),
    "Venus": frozenset({"Mercury", "Saturn"}),
    "Saturn": frozenset({"Mercury", "Venus"}),
}
_PERM_NEUTRALS: dict[str, frozenset[str]] = {
    "Sun": frozenset({"Mercury"}),
    "Moon": frozenset({"Mars", "Jupiter", "Venus", "Saturn"}),
    "Mars": frozenset({"Venus", "Saturn"}),
    "Mercury": frozenset({"Mars", "Jupiter", "Saturn"}),
    "Jupiter": frozenset({"Saturn"}),
    "Venus": frozenset({"Mars", "Jupiter"}),
    "Saturn": frozenset({"Jupiter"}),
}

# BPHS / Saravali Saptavargaja points (permanent levels only).
_SAPTA_POINTS = {
    "moolatrikona": 45.0,
    "own": 30.0,
    "friend": 15.0,
    "neutral": 10.0,
    "enemy": 4.0,
}


def _planet_enum(name: str) -> PlanetName:
    return PlanetName(name)


def _debilitation_longitude(planet: str) -> float:
    p = _planet_enum(planet)
    sign = DEBILITATION_SIGN[p]
    deg = EXALTATION_DEGREE[p]
    return SIGNS.index(sign) * 30.0 + deg


def angular_distance_deg(a: float, b: float) -> float:
    return abs((normalize_longitude(a) - normalize_longitude(b) + 180.0) % 360.0 - 180.0)


def naisargika_bala(planet: str) -> float:
    return float(NAISARGIKA_VIRUPA[planet])


def dig_bala(*, planet: str, rasi_house: int) -> float:
    strong = DIG_STRONG_HOUSE[planet]
    steps = min((rasi_house - strong) % 12, (strong - rasi_house) % 12)
    return max(0.0, 60.0 * (1.0 - steps / 6.0))


def uchcha_bala(*, planet: str, longitude_sidereal_deg: float) -> float:
    deb = _debilitation_longitude(planet)
    dist = angular_distance_deg(longitude_sidereal_deg, deb)
    return (dist / 180.0) * 60.0


def kendradi_bala(*, rasi_house: int) -> float:
    if rasi_house in {1, 4, 7, 10}:
        return 60.0
    if rasi_house in {2, 5, 8, 11}:
        return 30.0
    return 15.0


def ojayugma_rasi_bala(*, planet: str, sign: str) -> float:
    """Odd/even rasi strength (Saravali): male+neutral odd; female even."""
    odd = (SIGNS.index(sign) % 2) == 0
    if planet in MALE_PLANETS or planet in NEUTRAL_OJAYUGMA:
        return 15.0 if odd else 0.0
    if planet in FEMALE_PLANETS:
        return 15.0 if not odd else 0.0
    return 0.0


def ojayugma_navamsa_bala(*, planet: str, navamsa_sign: str) -> float:
    """Odd/even navamsa strength — same parity rule as rasi (Saravali)."""
    return ojayugma_rasi_bala(planet=planet, sign=navamsa_sign)


def drekkana_bala(*, planet: str, longitude_sidereal_deg: float) -> float:
    """
    Drekkana Bala (Saravali Candidate).

    Male → 1st 10°; female → 2nd 10°; neutral → 3rd 10°. Else 0.
    """
    deg = normalize_longitude(longitude_sidereal_deg) % 30.0
    if planet in MALE_PLANETS:
        return 15.0 if deg < 10.0 else 0.0
    if planet in FEMALE_PLANETS:
        return 15.0 if 10.0 <= deg < 20.0 else 0.0
    if planet in NEUTRAL_OJAYUGMA:
        return 15.0 if deg >= 20.0 else 0.0
    return 0.0


def _perm_relation(planet: str, other: str) -> str:
    if planet == other:
        return "own"
    if other in _PERM_FRIENDS.get(planet, ()):
        return "friend"
    if other in _PERM_NEUTRALS.get(planet, ()):
        return "neutral"
    return "enemy"


def _in_moolatrikona_d1(planet: str, sign: str, sign_degree: float) -> bool:
    pe = PlanetName(planet)
    spec = MOOLATRIKONA_RANGE.get(pe)
    if not spec:
        return False
    m_sign, start, end = spec
    return sign == m_sign and start <= sign_degree < end


def saptavargaja_points(
    *,
    planet: str,
    varga: str,
    sign: str,
    sign_degree: float = 0.0,
) -> dict[str, Any]:
    """
    One-varga Saptavargaja contribution (Candidate).

    Moolatrikona 45 only in D1 with degree window; other vargas use own=30
    for own/moolatrikona signs. Extreme friend/enemy deferred (permanent only).
    Exaltation/debilitation ignored (Saravali).
    """
    pe = PlanetName(planet)
    lord = sign_lord(sign)
    lord_name = lord.value if lord else None

    if varga == "D1" and _in_moolatrikona_d1(planet, sign, sign_degree):
        return {
            "points": _SAPTA_POINTS["moolatrikona"],
            "basis": "moolatrikona",
            "sign_lord": lord_name,
        }
    if sign in OWN_SIGNS.get(pe, set()) or lord_name == planet:
        return {
            "points": _SAPTA_POINTS["own"],
            "basis": "own",
            "sign_lord": lord_name,
        }
    if lord_name is None:
        return {"points": 0.0, "basis": "unknown_sign", "sign_lord": None}

    rel = _perm_relation(planet, lord_name)
    return {
        "points": _SAPTA_POINTS[rel],
        "basis": rel,
        "sign_lord": lord_name,
    }


def compute_saptavargaja_bala(
    *,
    planet: str,
    longitude_sidereal_deg: float,
    varga_signs: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Sum Saptavargaja across D1/D2/D3/D7/D9/D12/D30."""
    rows: list[dict[str, Any]] = []
    total = 0.0
    lon = normalize_longitude(longitude_sidereal_deg)
    for vid in SAPTAVARGA_IDS:
        if varga_signs and vid in varga_signs and varga_signs[vid].get("sign"):
            sign = str(varga_signs[vid]["sign"])
            sign_deg = float(varga_signs[vid].get("sign_degree") or 0.0)
        else:
            place = varga_sign(lon, VargaId(vid))
            sign, sign_deg = place.sign, place.sign_degree
        part = saptavargaja_points(
            planet=planet, varga=vid, sign=sign, sign_degree=sign_deg
        )
        total += float(part["points"])
        rows.append(
            {
                "varga": vid,
                "sign": sign,
                "points": part["points"],
                "basis": part["basis"],
                "sign_lord": part["sign_lord"],
            }
        )
    return {
        "value": round(total, 6),
        "parts": rows,
        "basis": "saptavargaja_permanent_friendship_candidate",
        "deferred": ["adhi_mitra", "adhi_satru", "temporal_friendship"],
    }

def natonnata_bala(*, planet: str, is_day: bool) -> float:
    """Day/night strength (Candidate): Mercury always 60."""
    if planet == "Mercury":
        return 60.0
    if planet in DAY_STRONG:
        return 60.0 if is_day else 0.0
    if planet in NIGHT_STRONG:
        return 60.0 if not is_day else 0.0
    return 0.0


def paksha_bala(*, planet: str, sun_lon: float, moon_lon: float) -> float:
    """
    Lunar-phase strength (Candidate).

    Benefics rise toward Full Moon; malefics toward New Moon.
    """
    elong = lunar_elongation_deg(sun_lon, moon_lon)
    bright = elong if elong <= 180.0 else 360.0 - elong  # 0 new → 180 full
    benefic = (bright / 180.0) * 60.0
    if planet in NATURAL_BENEFICS:
        return benefic
    if planet in NATURAL_MALEFICS:
        return 60.0 - benefic
    return 30.0


def vara_bala(*, planet: str, vara_lord: str | None) -> float:
    """Weekday-lord strength: 45 virupa if planet lords the day (Candidate)."""
    if vara_lord and planet == vara_lord:
        return 45.0
    return 0.0


def hora_bala(*, planet: str, hora_lord: str | None) -> float:
    """Hora-lord strength: 60 virupa if planet lords the birth hora (Candidate)."""
    if hora_lord and planet == hora_lord:
        return 60.0
    return 0.0


def abda_bala(*, planet: str, abda_lord: str | None) -> float:
    """Year-lord strength: 15 virupa (Candidate sankranti-weekday approx)."""
    if abda_lord and planet == abda_lord:
        return 15.0
    return 0.0


def masa_bala(*, planet: str, masa_lord: str | None) -> float:
    """Month-lord strength: 30 virupa (Candidate sankranti-weekday approx)."""
    if masa_lord and planet == masa_lord:
        return 30.0
    return 0.0


def tribhaga_bala(*, planet: str, is_day: bool, portion_index: int | None) -> float:
    """
    Tribhaga Bala (Saravali Candidate).

    Day portions: Mercury / Sun / Saturn. Night: Moon / Venus / Mars.
    Jupiter always 60. ``portion_index`` is 0..2 within day or night.
    """
    if planet == "Jupiter":
        return 60.0
    if portion_index is None or not 0 <= portion_index <= 2:
        return 0.0
    lords = ("Mercury", "Sun", "Saturn") if is_day else ("Moon", "Venus", "Mars")
    return 60.0 if planet == lords[portion_index] else 0.0


def ayana_bala(*, planet: str, tropical_longitude_deg: float) -> float:
    """
    Ayana Bala via length-based formula (Saravali Candidate).

    ``ayanabala = 30 * (1 ± |sin(tropical_lon)|)`` with hemisphere rules.
    """
    lon = normalize_longitude(tropical_longitude_deg)
    amp = abs(math.sin(math.radians(lon)))
    northern = lon < 180.0  # Aries–Virgo ≈ northern declination hemisphere
    if planet == "Mercury":
        return round(30.0 * (1.0 + amp), 6)
    if planet in {"Moon", "Saturn"}:
        # Strong in southern hemisphere.
        signed = amp if not northern else -amp
        return round(30.0 * (1.0 + signed), 6)
    if planet in {"Sun", "Mars", "Jupiter", "Venus"}:
        signed = amp if northern else -amp
        return round(30.0 * (1.0 + signed), 6)
    return 30.0


def _sankranti_weekday_lord(
    *,
    birth_local: datetime,
    sun_sidereal_lon: float,
    target_lon: float,
) -> str:
    """
    Approximate weekday lord of a sidereal Sun sankranti.

    Classical rule uses Hora lord at sankranti instant; Candidate uses the
    weekday lord of the civil day ~``(sun - target) % 360`` days earlier.
    """
    from bhava360.timing.muhurta import sunday_index

    days = (normalize_longitude(sun_sidereal_lon) - normalize_longitude(target_lon)) % 360.0
    sank = birth_local.replace(tzinfo=None) - timedelta(days=float(days))
    return VARA_LORDS[sunday_index(sank)]


def compute_kala_bala(
    *,
    planet: str,
    is_day: bool,
    sun_lon: float,
    moon_lon: float,
    vara_lord: str | None,
    hora_lord: str | None,
    abda_lord: str | None = None,
    masa_lord: str | None = None,
    tribhaga_portion: int | None = None,
    tropical_longitude_deg: float | None = None,
) -> dict[str, Any]:
    nat = natonnata_bala(planet=planet, is_day=is_day)
    pak = paksha_bala(planet=planet, sun_lon=sun_lon, moon_lon=moon_lon)
    trib = tribhaga_bala(planet=planet, is_day=is_day, portion_index=tribhaga_portion)
    abda = abda_bala(planet=planet, abda_lord=abda_lord)
    masa = masa_bala(planet=planet, masa_lord=masa_lord)
    vara = vara_bala(planet=planet, vara_lord=vara_lord)
    hora = hora_bala(planet=planet, hora_lord=hora_lord)
    ayana = (
        ayana_bala(planet=planet, tropical_longitude_deg=float(tropical_longitude_deg))
        if tropical_longitude_deg is not None
        else 0.0
    )
    # Yuddha applied later at pack level (needs all planets).
    pre_yuddha = nat + pak + trib + abda + masa + vara + hora
    subtotal = pre_yuddha + ayana
    return {
        "natonnata": round(nat, 6),
        "paksha": round(pak, 6),
        "tribhaga": round(trib, 6),
        "abda": round(abda, 6),
        "masa": round(masa, 6),
        "vara": round(vara, 6),
        "hora": round(hora, 6),
        "ayana": round(ayana, 6),
        "yuddha": 0.0,
        "pre_yuddha_subtotal": round(pre_yuddha, 6),
        "subtotal": round(subtotal, 6),
        "deferred_subs": ["abda_masa_hora_at_sankranti"],
    }


def apply_yuddha_bala(
    rows: list[dict[str, Any]],
    *,
    longitudes: dict[str, float],
) -> list[dict[str, Any]]:
    """
    Planetary war (Saravali Candidate): Mars–Saturn within 1°.

    Higher longitude wins; difference of pre-Ayana Kala is added to winner
    and subtracted from loser. Ayana excluded from the redistribution base.
    """
    war_planets = ("Mars", "Mercury", "Jupiter", "Venus", "Saturn")
    by_name = {r["planet"]: r for r in rows}
    adjustments: dict[str, float] = {p: 0.0 for p in by_name}

    for i, a in enumerate(war_planets):
        if a not in longitudes or a not in by_name:
            continue
        for b in war_planets[i + 1 :]:
            if b not in longitudes or b not in by_name:
                continue
            la, lb = longitudes[a], longitudes[b]
            if abs((la - lb + 180.0) % 360.0 - 180.0) >= 1.0:
                continue
            ka = float(by_name[a]["components_virupa"]["kala_partial"]["pre_yuddha_subtotal"])
            kb = float(by_name[b]["components_virupa"]["kala_partial"]["pre_yuddha_subtotal"])
            diff = abs(ka - kb)
            if la >= lb:
                winner, loser = a, b
            else:
                winner, loser = b, a
            adjustments[winner] += diff
            adjustments[loser] -= diff

    for row in rows:
        name = row["planet"]
        adj = adjustments.get(name, 0.0)
        if adj == 0.0:
            continue
        kala = row["components_virupa"]["kala_partial"]
        kala["yuddha"] = round(adj, 6)
        kala["subtotal"] = round(float(kala["subtotal"]) + adj, 6)
        # Recompute planet partial total.
        comps = row["components_virupa"]
        sth = float(comps["sthana_partial"]["subtotal"])
        row["partial_total_virupa"] = round(
            float(comps["naisargika"])
            + float(comps["dig"])
            + sth
            + float(kala["subtotal"])
            + float(comps["chesta"]["value"])
            + float(comps["drik"]["value"]),
            6,
        )
        row["partial_total_rupa"] = round(row["partial_total_virupa"] / 60.0, 6)
    return rows


def chesta_bala(
    *,
    planet: str,
    is_retrograde: bool,
    speed_longitude: float | None = None,
    sign_degree: float | None = None,
    ayana_value: float | None = None,
    paksha_value: float | None = None,
) -> dict[str, Any]:
    """
    Motional strength (Saravali / BPHS Candidate).

    - Sun: identical to Ayana Bala
    - Moon: identical to Paksha Bala
    - Mars–Saturn: 8-fold motion bands from daily speed vs mean
      (Vakra/Anuvakra/Vikala/Mandatara/Manda/Sama/Chara/Atichara)

    Seeghra-kendra alternate method deferred.
    """
    if planet == "Sun":
        val = float(ayana_value) if ayana_value is not None else 0.0
        return {
            "value": round(val, 6),
            "basis": "ayana_as_chesta",
            "motion": "luminary",
            "is_retrograde": False,
            "speed_longitude": None,
            "speed_ratio_vs_mean": None,
        }
    if planet == "Moon":
        val = float(paksha_value) if paksha_value is not None else 0.0
        return {
            "value": round(val, 6),
            "basis": "paksha_as_chesta",
            "motion": "luminary",
            "is_retrograde": False,
            "speed_longitude": None,
            "speed_ratio_vs_mean": None,
        }
    if planet not in CHESTA_MOTION_PLANETS:
        return {
            "value": 0.0,
            "basis": "unsupported",
            "motion": "unsupported",
            "is_retrograde": bool(is_retrograde),
            "speed_longitude": speed_longitude,
            "speed_ratio_vs_mean": None,
        }

    mean = MEAN_DAILY_MOTION_DEG[planet]
    if speed_longitude is None:
        # Fallback when speed missing: retrograde→Vakra else Sama.
        if is_retrograde:
            return {
                "value": 60.0,
                "basis": "vakra_retrograde_flag_fallback",
                "motion": "vakra",
                "is_retrograde": True,
                "speed_longitude": None,
                "speed_ratio_vs_mean": None,
            }
        return {
            "value": 7.5,
            "basis": "sama_missing_speed_fallback",
            "motion": "sama",
            "is_retrograde": False,
            "speed_longitude": None,
            "speed_ratio_vs_mean": None,
        }

    speed = float(speed_longitude)
    if speed < 0.0:
        # Anuvakra: retrograde and near 0° of sign (entering previous).
        if sign_degree is not None and float(sign_degree) < 1.0:
            return {
                "value": 30.0,
                "basis": "anuvakra",
                "motion": "anuvakra",
                "is_retrograde": True,
                "speed_longitude": round(speed, 6),
                "speed_ratio_vs_mean": round(speed / mean, 6),
            }
        return {
            "value": 60.0,
            "basis": "vakra",
            "motion": "vakra",
            "is_retrograde": True,
            "speed_longitude": round(speed, 6),
            "speed_ratio_vs_mean": round(speed / mean, 6),
        }

    ratio = abs(speed) / mean if mean > 0 else 1.0
    if ratio < 0.10:
        motion, val = "vikala", 15.0
    elif ratio < 0.50:
        motion, val = "mandatara", 15.0
    elif ratio < 1.00:
        motion, val = "manda", 30.0
    elif ratio < 1.50:
        motion, val = "sama", 7.5
    else:
        # Atichara: fast and near end of sign (entering next).
        if sign_degree is not None and float(sign_degree) >= 29.0:
            motion, val = "atichara", 30.0
        else:
            motion, val = "chara", 45.0

    return {
        "value": round(val, 6),
        "basis": motion,
        "motion": motion,
        "is_retrograde": False,
        "speed_longitude": round(speed, 6),
        "speed_ratio_vs_mean": round(ratio, 6),
    }

def _aspect_weight(matched_house: int) -> float:
    # 7th full; special aspects slightly weaker (Candidate).
    if matched_house == 7:
        return 15.0
    return 10.0


def drik_bala(
    *,
    planet: str,
    planet_signs: dict[str, str],
) -> dict[str, Any]:
    """
    Aspectual net from whole-sign graha aspects onto `planet` (Candidate).

    Benefic aspectors add weight; malefic aspectors subtract. Clamped ±60.
    """
    target_sign = planet_signs.get(planet)
    if not target_sign:
        return {"value": 0.0, "benefic_hits": [], "malefic_hits": [], "raw": 0.0}

    benefic_hits: list[dict[str, Any]] = []
    malefic_hits: list[dict[str, Any]] = []
    raw = 0.0
    for other, from_sign in planet_signs.items():
        if other == planet or other not in CLASSICAL_PLANETS:
            continue
        houses = GRAHA_ASPECT_HOUSES.get(_planet_enum(other))
        if not houses:
            continue
        rel = relative_house(from_sign, target_sign)
        if rel not in houses:
            continue
        w = _aspect_weight(rel)
        hit = {"from": other, "matched_house": rel, "weight": w}
        if other in NATURAL_BENEFICS:
            raw += w
            benefic_hits.append(hit)
        elif other in NATURAL_MALEFICS:
            raw -= w
            malefic_hits.append(hit)
    clamped = max(-60.0, min(60.0, raw))
    return {
        "value": round(clamped, 6),
        "raw": round(raw, 6),
        "benefic_hits": benefic_hits,
        "malefic_hits": malefic_hits,
        "basis": "whole_sign_graha_aspect_net_candidate",
    }


def compute_planet_shadbala_partial(
    *,
    planet: str,
    longitude_sidereal_deg: float,
    sign: str,
    rasi_house: int,
    is_day: bool,
    sun_lon: float,
    moon_lon: float,
    vara_lord: str | None,
    hora_lord: str | None,
    is_retrograde: bool,
    planet_signs: dict[str, str],
    varga_signs: dict[str, dict[str, Any]] | None = None,
    abda_lord: str | None = None,
    masa_lord: str | None = None,
    tribhaga_portion: int | None = None,
    tropical_longitude_deg: float | None = None,
    speed_longitude: float | None = None,
    sign_degree: float | None = None,
) -> dict[str, Any]:
    nais = naisargika_bala(planet)
    dig = dig_bala(planet=planet, rasi_house=rasi_house)
    uchcha = uchcha_bala(planet=planet, longitude_sidereal_deg=longitude_sidereal_deg)
    kend = kendradi_bala(rasi_house=rasi_house)
    oja = ojayugma_rasi_bala(planet=planet, sign=sign)

    # Navamsa sign for Ojayugma amsa
    if varga_signs and "D9" in varga_signs and varga_signs["D9"].get("sign"):
        d9_sign = str(varga_signs["D9"]["sign"])
    else:
        d9_sign = varga_sign(longitude_sidereal_deg, VargaId.D9).sign
    oja_n = ojayugma_navamsa_bala(planet=planet, navamsa_sign=d9_sign)

    sapta = compute_saptavargaja_bala(
        planet=planet,
        longitude_sidereal_deg=longitude_sidereal_deg,
        varga_signs=varga_signs,
    )
    drek = drekkana_bala(planet=planet, longitude_sidereal_deg=longitude_sidereal_deg)

    sthana_partial = (
        uchcha + kend + oja + oja_n + float(sapta["value"]) + drek
    )

    trop = tropical_longitude_deg
    if trop is None:
        trop = longitude_sidereal_deg  # fallback; Ayana expects tropical

    kala = compute_kala_bala(
        planet=planet,
        is_day=is_day,
        sun_lon=sun_lon,
        moon_lon=moon_lon,
        vara_lord=vara_lord,
        hora_lord=hora_lord,
        abda_lord=abda_lord,
        masa_lord=masa_lord,
        tribhaga_portion=tribhaga_portion,
        tropical_longitude_deg=trop,
    )
    chesta = chesta_bala(
        planet=planet,
        is_retrograde=is_retrograde,
        speed_longitude=speed_longitude,
        sign_degree=sign_degree,
        ayana_value=float(kala["ayana"]) if planet == "Sun" else None,
        paksha_value=float(kala["paksha"]) if planet == "Moon" else None,
    )
    drik = drik_bala(planet=planet, planet_signs=planet_signs)

    components = {
        "naisargika": round(nais, 6),
        "dig": round(dig, 6),
        "sthana_partial": {
            "uchcha": round(uchcha, 6),
            "kendradi": round(kend, 6),
            "ojayugma_rasi": round(oja, 6),
            "ojayugma_navamsa": round(oja_n, 6),
            "saptavargaja": sapta,
            "drekkana": round(drek, 6),
            "subtotal": round(sthana_partial, 6),
            "deferred_subs": [],
        },
        "kala_partial": kala,
        "chesta": chesta,
        "drik": drik,
    }
    partial_total = (
        nais
        + dig
        + sthana_partial
        + float(kala["subtotal"])
        + float(chesta["value"])
        + float(drik["value"])
    )
    return {
        "planet": planet,
        "rasi_house": rasi_house,
        "sign": sign,
        "longitude_sidereal_deg": normalize_longitude(longitude_sidereal_deg),
        "components_virupa": components,
        "partial_total_virupa": round(partial_total, 6),
        "partial_total_rupa": round(partial_total / 60.0, 6),
        "full_minimum_virupa": FULL_MINIMUM_VIRUPA[planet],
        "full_minimum_comparison": "deferred_until_complete_shadbala",
        "included_components": [
            "naisargika",
            "dig",
            "sthana.uchcha",
            "sthana.kendradi",
            "sthana.ojayugma_rasi",
            "sthana.ojayugma_navamsa",
            "sthana.saptavargaja",
            "sthana.drekkana",
            "kala.natonnata",
            "kala.paksha",
            "kala.tribhaga",
            "kala.abda",
            "kala.masa",
            "kala.vara",
            "kala.hora",
            "kala.ayana",
            "kala.yuddha",
            "chesta.saravali_motion",
            "drik.thin",
        ],
        "deferred_components": [
            "saptavargaja.adhi_mitra_satru",
            "kala.abda_masa_hora_at_sankranti",
            "chesta.seeghra_kendra",
            "drik.classical_drishti_strength_tables",
        ],
    }


def _parse_local(iso_local: str) -> datetime:
    return datetime.fromisoformat(iso_local)


def _chart_context(chart: dict[str, Any]) -> dict[str, Any]:
    planets = {p["planet"]: p for p in chart.get("planets") or []}
    sun = planets.get("Sun") or {}
    moon = planets.get("Moon") or {}
    sun_lon = float(sun.get("longitude_sidereal_deg") or 0.0)
    moon_lon = float(moon.get("longitude_sidereal_deg") or 0.0)

    day_window = chart.get("day_window") or {}
    resolved = chart.get("resolved_time") or {}
    is_day = True
    vara_lord = None
    hora_lord = None
    abda_lord = None
    masa_lord = None
    tribhaga_portion: int | None = None
    sunrise_local = day_window.get("sunrise_local")
    sunset_local = day_window.get("sunset_local")
    local_iso = (chart.get("input") or {}).get("local_datetime") or resolved.get(
        "local_datetime"
    )

    if sunrise_local and sunset_local and local_iso:
        rise = _parse_local(str(sunrise_local))
        sett = _parse_local(str(sunset_local))
        local = _parse_local(str(local_iso).replace("T", " "))
        # Compare naive civil clocks.
        rise_n = rise.replace(tzinfo=None)
        sett_n = sett.replace(tzinfo=None)
        local_n = local.replace(tzinfo=None)
        is_day = rise_n <= local_n < sett_n
        try:
            from datetime import timezone

            from bhava360.timing.muhurta import active_window, compute_horas, sunday_index

            wd = sunday_index(rise_n)
            vara_lord = VARA_LORDS[wd]
            next_rise_approx = rise_n + timedelta(days=1)
            when_utc = resolved.get("utc_datetime")
            if when_utc:
                when = datetime.fromisoformat(str(when_utc))
                if when.tzinfo is None:
                    when = when.replace(tzinfo=timezone.utc)
                horas = compute_horas(
                    sunrise=rise_n,
                    sunset=sett_n,
                    next_sunrise=next_rise_approx,
                    weekday_sunday_index=wd,
                )
                active = active_window(when, horas["horas"])
                if active:
                    hora_lord = active.get("lord")
            # Tribhaga portion within day or night.
            if is_day:
                span = (sett_n - rise_n).total_seconds()
                elapsed = (local_n - rise_n).total_seconds()
            elif local_n >= sett_n:
                span = (next_rise_approx - sett_n).total_seconds()
                elapsed = (local_n - sett_n).total_seconds()
            else:
                prev_sett = sett_n - timedelta(days=1)
                span = (rise_n - prev_sett).total_seconds()
                elapsed = (local_n - prev_sett).total_seconds()
            if span > 0:
                tribhaga_portion = min(int((elapsed / span) * 3.0), 2)

            abda_lord = _sankranti_weekday_lord(
                birth_local=local_n, sun_sidereal_lon=sun_lon, target_lon=0.0
            )
            masa_target = math.floor(normalize_longitude(sun_lon) / 30.0) * 30.0
            masa_lord = _sankranti_weekday_lord(
                birth_local=local_n, sun_sidereal_lon=sun_lon, target_lon=masa_target
            )
        except Exception:  # noqa: BLE001
            hora_lord = None
            if sunrise_local:
                try:
                    from bhava360.timing.muhurta import sunday_index

                    wd = sunday_index(rise_n)
                    vara_lord = VARA_LORDS[wd]
                except Exception:  # noqa: BLE001
                    pass

    planet_signs = {
        name: str(p["sign"])
        for name, p in planets.items()
        if name in CLASSICAL_PLANETS and p.get("sign")
    }
    return {
        "planets": planets,
        "sun_lon": sun_lon,
        "moon_lon": moon_lon,
        "is_day": is_day,
        "vara_lord": vara_lord,
        "hora_lord": hora_lord,
        "abda_lord": abda_lord,
        "masa_lord": masa_lord,
        "tribhaga_portion": tribhaga_portion,
        "planet_signs": planet_signs,
    }


def compute_shadbala_pack(chart: dict[str, Any]) -> dict[str, Any]:
    """Compute partial Shadbala for classical seven planets from a chart dict."""
    ctx = _chart_context(chart)
    planets = ctx["planets"]
    rows: list[dict[str, Any]] = []
    longitudes: dict[str, float] = {}
    for name in CLASSICAL_PLANETS:
        p = planets.get(name)
        if not p:
            continue
        house = int((p.get("houses") or {}).get("rasi_house") or 0)
        if house < 1:
            continue
        lon = float(p["longitude_sidereal_deg"])
        longitudes[name] = lon
        trop = p.get("longitude_tropical_deg")
        rows.append(
            compute_planet_shadbala_partial(
                planet=name,
                longitude_sidereal_deg=lon,
                sign=str(p["sign"]),
                rasi_house=house,
                is_day=bool(ctx["is_day"]),
                sun_lon=float(ctx["sun_lon"]),
                moon_lon=float(ctx["moon_lon"]),
                vara_lord=ctx["vara_lord"],
                hora_lord=ctx["hora_lord"],
                is_retrograde=bool(p.get("is_retrograde")),
                planet_signs=ctx["planet_signs"],
                varga_signs=p.get("vargas") or {},
                abda_lord=ctx.get("abda_lord"),
                masa_lord=ctx.get("masa_lord"),
                tribhaga_portion=ctx.get("tribhaga_portion"),
                tropical_longitude_deg=float(trop) if trop is not None else None,
                speed_longitude=(
                    float(p["speed_longitude"])
                    if p.get("speed_longitude") is not None
                    else None
                ),
                sign_degree=float(p["sign_degree"]) if p.get("sign_degree") is not None else None,
            )
        )

    rows = apply_yuddha_bala(rows, longitudes=longitudes)
    ranked = sorted(rows, key=lambda r: r["partial_total_virupa"], reverse=True)
    return {
        "variant": SHADBALA_VARIANT,
        "unit": "virupa",
        "rupa_definition": "1 rupa = 60 virupa",
        "context": {
            "is_day": ctx["is_day"],
            "vara_lord": ctx["vara_lord"],
            "hora_lord": ctx["hora_lord"],
            "abda_lord": ctx.get("abda_lord"),
            "masa_lord": ctx.get("masa_lord"),
            "tribhaga_portion": ctx.get("tribhaga_portion"),
        },
        "planets": rows,
        "summary": {
            "planet_count": len(rows),
            "strongest_partial": ranked[0]["planet"] if ranked else None,
            "strongest_partial_virupa": ranked[0]["partial_total_virupa"] if ranked else None,
            "weakest_partial": ranked[-1]["planet"] if ranked else None,
            "included_component_families": [
                "naisargika",
                "dig",
                "sthana_partial",
                "kala_partial",
                "chesta",
                "drik",
            ],
            "deferred_component_families": [
                "kala_abda_masa_hora_at_sankranti",
                "chesta_seeghra_kendra",
                "drik_classical_tables",
                "saptavargaja_adhi_mitra",
            ],
        },
        "notes": [
            "Candidate partial scaffold — not a complete BPHS Shadbala pack.",
            "Partial totals must not be compared to full-pack minima for verdicts.",
            "Sthana: Uchcha + Kendradi + Ojayugma(rasi+navamsa) + Saptavargaja + Drekkana.",
            "Kala: Natonnata + Paksha + Tribhaga + Abda/Masa/Vara/Hora + Ayana + Yuddha.",
            "Chesta: Sun=Ayana, Moon=Paksha, others Saravali 8-fold speed bands.",
            "Seeghra-kendra Chesta alternate deferred.",
            "Drik thin: whole-sign graha aspect net (±60 clamp).",
        ],
    }


__all__ = [
    "CLASSICAL_PLANETS",
    "MEAN_DAILY_MOTION_DEG",
    "SAPTAVARGA_IDS",
    "SHADBALA_VARIANT",
    "abda_bala",
    "apply_yuddha_bala",
    "ayana_bala",
    "chesta_bala",
    "compute_kala_bala",
    "compute_planet_shadbala_partial",
    "compute_saptavargaja_bala",
    "compute_shadbala_pack",
    "dig_bala",
    "drekkana_bala",
    "drik_bala",
    "hora_bala",
    "kendradi_bala",
    "masa_bala",
    "naisargika_bala",
    "natonnata_bala",
    "ojayugma_navamsa_bala",
    "ojayugma_rasi_bala",
    "paksha_bala",
    "saptavargaja_points",
    "tribhaga_bala",
    "uchcha_bala",
    "vara_bala",
]
