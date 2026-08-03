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

SHADBALA_VARIANT = "shadbala_adhi_mitra_candidate_v1"

# Mean sidereal solar motion (°/day) for sankranti instant estimate (Candidate).
MEAN_SOLAR_SIDEREAL_DEG_PER_DAY = 0.98564733

# Superior planets: Seeghrochcha = mean Sun (BPHS / Raman Candidate).
SEEGHRA_SUPERIOR = frozenset({"Mars", "Jupiter", "Saturn"})
# Inferior: mean = mean Sun; Seeghrochcha ≈ heliocentric mean (table proxy).
SEEGHRA_INFERIOR = frozenset({"Mercury", "Venus"})
SEEGHRA_PLANETS = SEEGHRA_SUPERIOR | SEEGHRA_INFERIOR

# Temporary friends: 2nd/3rd/4th/10th/11th/12th from the planet (BPHS).
_TEMP_FRIEND_HOUSES = frozenset({2, 3, 4, 10, 11, 12})

_PLANET_TO_SWE_CHESTA: dict[str, int] | None = None


def _swe_planet_id(planet: str) -> int:
    global _PLANET_TO_SWE_CHESTA
    if _PLANET_TO_SWE_CHESTA is None:
        import swisseph as swe

        _PLANET_TO_SWE_CHESTA = {
            "Mars": swe.MARS,
            "Mercury": swe.MERCURY,
            "Jupiter": swe.JUPITER,
            "Venus": swe.VENUS,
            "Saturn": swe.SATURN,
        }
    return _PLANET_TO_SWE_CHESTA[planet]

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

# Permanent natural friendship (combined with temporary → Panchadha).
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

# BPHS Saptavargaja points (Santhanam / five-fold compound).
_SAPTA_POINTS = {
    "moolatrikona": 45.0,
    "own": 30.0,
    "adhi_mitra": 20.0,
    "friend": 15.0,
    "neutral": 10.0,
    "enemy": 4.0,
    "adhi_satru": 2.0,
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


def _temp_relation(*, from_sign: str, to_sign: str) -> str:
    """Tatkalika: friend if other is in 2/3/4/10/11/12 from planet."""
    rel = relative_house(from_sign, to_sign)
    return "friend" if rel in _TEMP_FRIEND_HOUSES else "enemy"


def compound_relation(
    planet: str,
    other: str,
    *,
    planet_signs: dict[str, str] | None = None,
) -> dict[str, str]:
    """
    Panchadha (five-fold) compound friendship (BPHS Candidate).

    Combines permanent natural relation with D1 temporary house relation.
    Without ``planet_signs``, returns permanent relation only.
    """
    if planet == other:
        return {
            "compound": "own",
            "permanent": "own",
            "temporary": "own",
        }
    perm = _perm_relation(planet, other)
    if not planet_signs or planet not in planet_signs or other not in planet_signs:
        return {
            "compound": perm,
            "permanent": perm,
            "temporary": "unknown",
        }
    temp = _temp_relation(
        from_sign=planet_signs[planet],
        to_sign=planet_signs[other],
    )
    if perm == "friend" and temp == "friend":
        compound = "adhi_mitra"
    elif perm == "enemy" and temp == "enemy":
        compound = "adhi_satru"
    elif perm == "friend" and temp == "enemy":
        compound = "neutral"
    elif perm == "enemy" and temp == "friend":
        compound = "neutral"
    elif perm == "neutral" and temp == "friend":
        compound = "friend"
    elif perm == "neutral" and temp == "enemy":
        compound = "enemy"
    else:
        compound = perm
    return {
        "compound": compound,
        "permanent": perm,
        "temporary": temp,
    }


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
    planet_signs: dict[str, str] | None = None,
) -> dict[str, Any]:
    """
    One-varga Saptavargaja contribution (Candidate).

    Moolatrikona 45 only in D1 with degree window; other vargas use own=30
    for own/moolatrikona signs. Friendship uses Panchadha compound when
    D1 ``planet_signs`` are supplied (Adhi-mitra 20 / Adhi-satru 2).
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
            "permanent": "own",
            "temporary": "own",
        }
    if sign in OWN_SIGNS.get(pe, set()) or lord_name == planet:
        return {
            "points": _SAPTA_POINTS["own"],
            "basis": "own",
            "sign_lord": lord_name,
            "permanent": "own",
            "temporary": "own",
        }
    if lord_name is None:
        return {
            "points": 0.0,
            "basis": "unknown_sign",
            "sign_lord": None,
            "permanent": None,
            "temporary": None,
        }

    rel = compound_relation(planet, lord_name, planet_signs=planet_signs)
    basis = rel["compound"]
    return {
        "points": _SAPTA_POINTS[basis],
        "basis": basis,
        "sign_lord": lord_name,
        "permanent": rel["permanent"],
        "temporary": rel["temporary"],
    }


def compute_saptavargaja_bala(
    *,
    planet: str,
    longitude_sidereal_deg: float,
    varga_signs: dict[str, dict[str, Any]] | None = None,
    planet_signs: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Sum Saptavargaja across D1/D2/D3/D7/D9/D12/D30 (Panchadha)."""
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
            planet=planet,
            varga=vid,
            sign=sign,
            sign_degree=sign_deg,
            planet_signs=planet_signs,
        )
        total += float(part["points"])
        rows.append(
            {
                "varga": vid,
                "sign": sign,
                "points": part["points"],
                "basis": part["basis"],
                "sign_lord": part["sign_lord"],
                "permanent": part.get("permanent"),
                "temporary": part.get("temporary"),
            }
        )
    used_compound = bool(planet_signs)
    return {
        "value": round(total, 6),
        "parts": rows,
        "basis": (
            "saptavargaja_panchadha_candidate"
            if used_compound
            else "saptavargaja_permanent_friendship_fallback"
        ),
        "deferred": [] if used_compound else ["adhi_mitra", "adhi_satru", "temporal_friendship"],
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
    """Year-lord strength: 15 virupa (Hora lord at Mesha sankranti)."""
    if abda_lord and planet == abda_lord:
        return 15.0
    return 0.0


def masa_bala(*, planet: str, masa_lord: str | None) -> float:
    """Month-lord strength: 30 virupa (Hora lord at current-rasi sankranti)."""
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


def _estimate_sankranti_local(
    *,
    birth_local: datetime,
    sun_sidereal_lon: float,
    target_lon: float,
) -> datetime:
    """Estimate sankranti civil instant via mean sidereal solar motion."""
    delta = (
        normalize_longitude(sun_sidereal_lon) - normalize_longitude(target_lon)
    ) % 360.0
    days = delta / MEAN_SOLAR_SIDEREAL_DEG_PER_DAY
    return birth_local.replace(tzinfo=None) - timedelta(days=float(days))


def _shift_clock(*, template: datetime, onto: datetime) -> datetime:
    """Copy template time-of-day onto ``onto``'s civil date (naive)."""
    t = template.replace(tzinfo=None)
    o = onto.replace(tzinfo=None)
    return o.replace(
        hour=t.hour,
        minute=t.minute,
        second=t.second,
        microsecond=t.microsecond,
    )


def _sankranti_weekday_lord(
    *,
    birth_local: datetime,
    sun_sidereal_lon: float,
    target_lon: float,
) -> str:
    """Weekday (Vara) lord fallback for a sankranti estimate."""
    from bhava360.timing.muhurta import sunday_index

    sank = _estimate_sankranti_local(
        birth_local=birth_local,
        sun_sidereal_lon=sun_sidereal_lon,
        target_lon=target_lon,
    )
    return VARA_LORDS[sunday_index(sank)]


def sankranti_hora_lord(
    *,
    birth_local: datetime,
    sun_sidereal_lon: float,
    target_lon: float,
    sunrise_local: datetime | None = None,
    sunset_local: datetime | None = None,
) -> dict[str, Any]:
    """
    Planetary Hora lord at estimated sidereal Sun sankranti (Candidate).

    Instant ≈ birth − Δλ / mean solar motion. Birth-day sunrise/sunset clocks
    are shifted onto the sankranti civil date (exact ephemeris sunrise deferred).
    Falls back to Vara lord when the day window is missing.
    """
    from datetime import timezone

    from bhava360.timing.muhurta import active_window, compute_horas, sunday_index

    sank = _estimate_sankranti_local(
        birth_local=birth_local,
        sun_sidereal_lon=sun_sidereal_lon,
        target_lon=target_lon,
    )
    if sunrise_local is None or sunset_local is None:
        lord = VARA_LORDS[sunday_index(sank)]
        return {
            "lord": lord,
            "basis": "sankranti_weekday_fallback",
            "sankranti_local": sank.isoformat(sep=" "),
        }

    rise = _shift_clock(template=sunrise_local, onto=sank)
    sett = _shift_clock(template=sunset_local, onto=sank)
    if sett <= rise:
        sett = sett + timedelta(days=1)
    next_rise = rise + timedelta(days=1)
    if sank < rise:
        rise = rise - timedelta(days=1)
        sett = sett - timedelta(days=1)
        next_rise = next_rise - timedelta(days=1)

    wd = sunday_index(rise)
    horas = compute_horas(
        sunrise=rise,
        sunset=sett,
        next_sunrise=next_rise,
        weekday_sunday_index=wd,
    )
    # Match existing birth-hora Candidate pattern: naive local clocks as UTC.
    when = sank.replace(tzinfo=timezone.utc)
    active = active_window(when, horas["horas"])
    if active and active.get("lord"):
        return {
            "lord": str(active["lord"]),
            "basis": "sankranti_hora_mean_sun_candidate",
            "sankranti_local": sank.isoformat(sep=" "),
            "hora_index": active.get("index"),
            "hora_period": active.get("period"),
            "vara_lord_of_day": VARA_LORDS[wd],
        }
    return {
        "lord": VARA_LORDS[wd],
        "basis": "sankranti_weekday_fallback",
        "sankranti_local": sank.isoformat(sep=" "),
        "vara_lord_of_day": VARA_LORDS[wd],
    }


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
        "deferred_subs": [],
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


def _fold_chesta_kendra(angle_deg: float) -> float:
    """Reduce Chesta/Seeghra kendra to 0–180°."""
    a = normalize_longitude(angle_deg)
    return a if a <= 180.0 else 360.0 - a


def seeghra_kendra_chesta(
    *,
    seeghrochcha_deg: float,
    mean_longitude_deg: float,
    true_longitude_deg: float,
) -> dict[str, Any]:
    """
    BPHS Chesta from Seeghra kendra (Candidate).

    CK = Seeghrochcha − (Mean + True)/2 ; if >180 use 360−CK; Bala = CK/3.
    """
    mean = normalize_longitude(mean_longitude_deg)
    true = normalize_longitude(true_longitude_deg)
    seeg = normalize_longitude(seeghrochcha_deg)
    avg = ((mean + true) / 2.0) % 360.0
    ck_raw = (seeg - avg) % 360.0
    ck = _fold_chesta_kendra(ck_raw)
    val = ck / 3.0
    return {
        "value": round(val, 6),
        "seeghra_kendra_deg": round(ck, 6),
        "seeghra_kendra_raw_deg": round(ck_raw, 6),
        "average_longitude_deg": round(avg, 6),
        "mean_longitude_deg": round(mean, 6),
        "true_longitude_deg": round(true, 6),
        "seeghrochcha_deg": round(seeg, 6),
        "basis": "seeghra_kendra_bphs_candidate",
    }


def resolve_seeghra_inputs(
    *,
    planet: str,
    true_longitude_sidereal_deg: float,
    julian_day_ut: float,
    ayanamsa_deg: float,
    ephemeris_mode: str = "moshier",
) -> dict[str, Any] | None:
    """
    Resolve mean longitude + Seeghrochcha for Seeghra Chesta (Candidate).

    - Mars/Jupiter/Saturn: mean = SE osculating LM (sidereal);
      Seeghrochcha = mean Sun (Earth LM + 180°).
    - Mercury/Venus: mean = mean Sun; Seeghrochcha = heliocentric mean LM
      (Candidate proxy; classical product tables deferred).
    """
    if planet not in SEEGHRA_PLANETS:
        return None
    try:
        import swisseph as swe

        if ephemeris_mode == "swisseph_files":
            flag = swe.FLG_SWIEPH
        else:
            flag = swe.FLG_MOSEPH
        jd_et = float(julian_day_ut) + float(swe.deltat(julian_day_ut)) / 86400.0
        aya = float(ayanamsa_deg)

        def trop_lm_to_sid(lm: float) -> float:
            return normalize_longitude(float(lm) - aya)

        earth = swe.get_orbital_elements(jd_et, swe.EARTH, flag)
        mean_sun = trop_lm_to_sid((float(earth[9]) + 180.0) % 360.0)
        true = normalize_longitude(true_longitude_sidereal_deg)

        if planet in SEEGHRA_INFERIOR:
            # Classical: mean of Mercury/Venus = mean Sun.
            # Seeghrochcha: heliocentric mean LM as table proxy (Candidate).
            body = swe.get_orbital_elements(jd_et, _swe_planet_id(planet), flag)
            seeg = trop_lm_to_sid(float(body[9]) % 360.0)
            return {
                "mean_longitude_deg": mean_sun,
                "seeghrochcha_deg": seeg,
                "true_longitude_deg": true,
                "mean_sun_deg": mean_sun,
                "notes": ["inferior_seeghrochcha_heliocentric_mean_proxy"],
            }

        body = swe.get_orbital_elements(jd_et, _swe_planet_id(planet), flag)
        mean = trop_lm_to_sid(float(body[9]) % 360.0)
        return {
            "mean_longitude_deg": mean,
            "seeghrochcha_deg": mean_sun,
            "true_longitude_deg": true,
            "mean_sun_deg": mean_sun,
            "notes": ["superior_seeghrochcha_mean_sun"],
        }
    except Exception:  # noqa: BLE001
        return None


def chesta_saravali_motion(
    *,
    planet: str,
    is_retrograde: bool,
    speed_longitude: float | None = None,
    sign_degree: float | None = None,
) -> dict[str, Any]:
    """Saravali 8-fold speed-band Chesta (fallback / prior P30b)."""
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


def chesta_bala(
    *,
    planet: str,
    is_retrograde: bool,
    speed_longitude: float | None = None,
    sign_degree: float | None = None,
    ayana_value: float | None = None,
    paksha_value: float | None = None,
    true_longitude_sidereal_deg: float | None = None,
    julian_day_ut: float | None = None,
    ayanamsa_deg: float | None = None,
    ephemeris_mode: str = "moshier",
    seeghra_inputs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Motional strength (BPHS Seeghra + Saravali fallback).

    - Sun: identical to Ayana Bala
    - Moon: identical to Paksha Bala
    - Mars–Saturn: Seeghra-kendra Chesta when JD/means available;
      else Saravali 8-fold speed bands
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

    inputs = seeghra_inputs
    if inputs is None and (
        true_longitude_sidereal_deg is not None
        and julian_day_ut is not None
        and ayanamsa_deg is not None
        and planet in SEEGHRA_PLANETS
    ):
        inputs = resolve_seeghra_inputs(
            planet=planet,
            true_longitude_sidereal_deg=float(true_longitude_sidereal_deg),
            julian_day_ut=float(julian_day_ut),
            ayanamsa_deg=float(ayanamsa_deg),
            ephemeris_mode=ephemeris_mode,
        )

    if inputs is not None:
        out = seeghra_kendra_chesta(
            seeghrochcha_deg=float(inputs["seeghrochcha_deg"]),
            mean_longitude_deg=float(inputs["mean_longitude_deg"]),
            true_longitude_deg=float(inputs["true_longitude_deg"]),
        )
        out["motion"] = "seeghra_kendra"
        out["is_retrograde"] = bool(is_retrograde)
        out["speed_longitude"] = (
            round(float(speed_longitude), 6) if speed_longitude is not None else None
        )
        out["speed_ratio_vs_mean"] = None
        out["seeghra_notes"] = list(inputs.get("notes") or [])
        return out

    return chesta_saravali_motion(
        planet=planet,
        is_retrograde=is_retrograde,
        speed_longitude=speed_longitude,
        sign_degree=sign_degree,
    )


def _clamp_sphuta(value: float) -> float:
    return max(0.0, min(60.0, value))


def _base_aspect_virupa(*, aspector: str, matched_house: int) -> float:
    """Whole-sign classical table (fallback when longitudes missing)."""
    if matched_house == 7:
        return 60.0
    if matched_house in {4, 8}:
        return 60.0 if aspector == "Mars" else 45.0
    if matched_house in {5, 9}:
        return 60.0 if aspector == "Jupiter" else 30.0
    if matched_house in {3, 10}:
        return 60.0 if aspector == "Saturn" else 15.0
    return 0.0


def sphuta_drishti(*, aspector: str, from_longitude: float, to_longitude: float) -> float:
    """
    Sphuta (degree) Drishti virupa 0–60 (Saravali Candidate).

    Angle ``a`` = forward zodiacal distance from aspector to aspected.
    General 150–180 uses ``2*(a-150)`` so opposition = 60 (table typo fix;
    stamped Candidate). Planet-specific columns override when present.
    """
    a = (normalize_longitude(to_longitude) - normalize_longitude(from_longitude)) % 360.0

    def general() -> float:
        if a < 30.0 or a >= 330.0:
            return 0.0
        if a < 60.0:
            return (a - 30.0) / 2.0
        if a < 90.0:
            return a - 45.0
        if a < 120.0:
            return 30.0 + (120.0 - a) / 2.0
        if a < 150.0:
            return 150.0 - a
        if a < 180.0:
            # Saravali table prints 2*(150-a); that yields 0 at 180 — corrected.
            return 2.0 * (a - 150.0)
        if a < 300.0:
            return (300.0 - a) / 2.0
        return 0.0

    special: float | None = None
    if aspector == "Mars":
        if 90.0 <= a < 120.0:
            special = 45.0 + (a - 90.0) / 2.0
        elif 120.0 <= a < 150.0:
            special = 2.0 * (150.0 - a)
        elif 180.0 <= a < 210.0:
            special = 60.0
        elif 210.0 <= a < 240.0:
            special = 270.0 - a
    elif aspector == "Jupiter":
        if 90.0 <= a < 120.0:
            special = 45.0 + (a - 90.0) / 2.0
        elif 120.0 <= a < 150.0:
            special = 2.0 * (150.0 - a)
        elif 210.0 <= a < 240.0:
            special = 45.0 + (a - 210.0) / 2.0
        elif 240.0 <= a < 270.0:
            special = 15.0 + 2.0 * (270.0 - a) / 3.0
    elif aspector == "Saturn":
        if 30.0 <= a < 60.0:
            special = (a - 30.0) * 2.0
        elif 60.0 <= a < 90.0:
            special = 45.0 + (90.0 - a) / 2.0
        elif 240.0 <= a < 270.0:
            special = a - 210.0
        elif 270.0 <= a < 330.0:
            special = 2.0 * (300.0 - a)

    raw = general() if special is None else special
    return _clamp_sphuta(raw)


def _drik_is_benefic(
    aspector: str,
    *,
    sun_lon: float,
    moon_lon: float,
    planet_signs: dict[str, str],
) -> bool:
    """Benefic/malefic for Drig Bala (Saravali Candidate)."""
    if aspector in {"Jupiter", "Venus"}:
        return True
    if aspector in {"Sun", "Mars", "Saturn"}:
        return False
    if aspector == "Moon":
        elong = lunar_elongation_deg(sun_lon, moon_lon)
        return elong <= 180.0
    if aspector == "Mercury":
        m_sign = planet_signs.get("Mercury")
        if not m_sign:
            return True
        for mal in ("Sun", "Mars", "Saturn"):
            if planet_signs.get(mal) == m_sign:
                return False
        return True
    return False


def drik_bala(
    *,
    planet: str,
    planet_signs: dict[str, str],
    sun_lon: float = 0.0,
    moon_lon: float = 0.0,
    planet_longitudes: dict[str, float] | None = None,
) -> dict[str, Any]:
    """
    Drig Bala via Sphuta Drishti (Candidate).

    Degree-based Sphuta virupa for each aspector, then benefic ×1.25 (add) /
    malefic ×0.75 (subtract). Falls back to whole-sign classical table if
    longitudes are missing.
    """
    target_sign = planet_signs.get(planet)
    if not target_sign:
        return {
            "value": 0.0,
            "benefic_hits": [],
            "malefic_hits": [],
            "raw": 0.0,
            "basis": "sphuta_drishti_candidate",
        }

    use_sphuta = bool(planet_longitudes) and planet in (planet_longitudes or {})
    benefic_hits: list[dict[str, Any]] = []
    malefic_hits: list[dict[str, Any]] = []
    raw = 0.0

    for other, from_sign in planet_signs.items():
        if other == planet or other not in CLASSICAL_PLANETS:
            continue

        if use_sphuta and other in planet_longitudes:  # type: ignore[operator]
            base = sphuta_drishti(
                aspector=other,
                from_longitude=float(planet_longitudes[other]),  # type: ignore[index]
                to_longitude=float(planet_longitudes[planet]),  # type: ignore[index]
            )
            angle = (
                normalize_longitude(float(planet_longitudes[planet]))  # type: ignore[index]
                - normalize_longitude(float(planet_longitudes[other]))  # type: ignore[index]
            ) % 360.0
            matched_house = None
        else:
            houses = GRAHA_ASPECT_HOUSES.get(_planet_enum(other))
            if not houses:
                continue
            rel = relative_house(from_sign, target_sign)
            if rel not in houses:
                continue
            base = _base_aspect_virupa(aspector=other, matched_house=rel)
            angle = None
            matched_house = rel

        if base <= 0:
            continue
        benefic = _drik_is_benefic(
            other, sun_lon=sun_lon, moon_lon=moon_lon, planet_signs=planet_signs
        )
        hit: dict[str, Any] = {
            "from": other,
            "base_virupa": round(base, 6),
            "factor": 1.25 if benefic else 0.75,
        }
        if matched_house is not None:
            hit["matched_house"] = matched_house
        if angle is not None:
            hit["aspect_angle_deg"] = round(angle, 6)
        if benefic:
            weight = base * 1.25
            raw += weight
            hit["weight"] = round(weight, 6)
            benefic_hits.append(hit)
        else:
            weight = base * 0.75
            raw -= weight
            hit["weight"] = round(weight, 6)
            malefic_hits.append(hit)

    return {
        "value": round(raw, 6),
        "raw": round(raw, 6),
        "benefic_hits": benefic_hits,
        "malefic_hits": malefic_hits,
        "basis": "sphuta_drishti_candidate" if use_sphuta else "classical_graha_drishti_table_fallback",
        "notes": [
            "Sphuta general 150–180 uses 2*(a-150) so opposition=60 (Candidate fix).",
        ],
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
    planet_longitudes: dict[str, float] | None = None,
    julian_day_ut: float | None = None,
    ayanamsa_deg: float | None = None,
    ephemeris_mode: str = "moshier",
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
        planet_signs=planet_signs,
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
        true_longitude_sidereal_deg=longitude_sidereal_deg,
        julian_day_ut=julian_day_ut,
        ayanamsa_deg=ayanamsa_deg,
        ephemeris_mode=ephemeris_mode,
    )
    drik = drik_bala(
        planet=planet,
        planet_signs=planet_signs,
        sun_lon=sun_lon,
        moon_lon=moon_lon,
        planet_longitudes=planet_longitudes,
    )

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
            "chesta.seeghra_kendra",
            "chesta.saravali_motion_fallback",
            "drik.sphuta",
        ],
        "deferred_components": [
            "kala.sankranti_ephemeris_sunrise",
            "chesta.inferior_seeghrochcha_product_tables",
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
    abda_meta: dict[str, Any] | None = None
    masa_meta: dict[str, Any] | None = None
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

            abda_meta = sankranti_hora_lord(
                birth_local=local_n,
                sun_sidereal_lon=sun_lon,
                target_lon=0.0,
                sunrise_local=rise_n,
                sunset_local=sett_n,
            )
            abda_lord = abda_meta.get("lord")
            masa_target = math.floor(normalize_longitude(sun_lon) / 30.0) * 30.0
            masa_meta = sankranti_hora_lord(
                birth_local=local_n,
                sun_sidereal_lon=sun_lon,
                target_lon=masa_target,
                sunrise_local=rise_n,
                sunset_local=sett_n,
            )
            masa_lord = masa_meta.get("lord")
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
    jd = resolved.get("julian_day_ut")
    aya = chart.get("ayanamsa_degrees")
    lib = chart.get("library") or chart.get("config") or {}
    ephe_mode = str(lib.get("ephemeris_mode") or "moshier")
    return {
        "planets": planets,
        "sun_lon": sun_lon,
        "moon_lon": moon_lon,
        "is_day": is_day,
        "vara_lord": vara_lord,
        "hora_lord": hora_lord,
        "abda_lord": abda_lord,
        "masa_lord": masa_lord,
        "abda_meta": abda_meta,
        "masa_meta": masa_meta,
        "tribhaga_portion": tribhaga_portion,
        "planet_signs": planet_signs,
        "julian_day_ut": float(jd) if jd is not None else None,
        "ayanamsa_deg": float(aya) if aya is not None else None,
        "ephemeris_mode": ephe_mode,
    }


def compute_shadbala_pack(chart: dict[str, Any]) -> dict[str, Any]:
    """Compute partial Shadbala for classical seven planets from a chart dict."""
    ctx = _chart_context(chart)
    planets = ctx["planets"]
    longitudes: dict[str, float] = {}
    for name in CLASSICAL_PLANETS:
        p = planets.get(name)
        if not p or p.get("longitude_sidereal_deg") is None:
            continue
        longitudes[name] = float(p["longitude_sidereal_deg"])

    rows: list[dict[str, Any]] = []
    for name in CLASSICAL_PLANETS:
        p = planets.get(name)
        if not p:
            continue
        house = int((p.get("houses") or {}).get("rasi_house") or 0)
        if house < 1:
            continue
        lon = float(p["longitude_sidereal_deg"])
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
                planet_longitudes=longitudes,
                julian_day_ut=ctx.get("julian_day_ut"),
                ayanamsa_deg=ctx.get("ayanamsa_deg"),
                ephemeris_mode=str(ctx.get("ephemeris_mode") or "moshier"),
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
            "abda_meta": ctx.get("abda_meta"),
            "masa_meta": ctx.get("masa_meta"),
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
                "kala_sankranti_ephemeris_sunrise",
                "chesta_inferior_seeghrochcha_product_tables",
            ],
        },
        "notes": [
            "Candidate partial scaffold — not a complete BPHS Shadbala pack.",
            "Partial totals must not be compared to full-pack minima for verdicts.",
            "Sthana: Uchcha + Kendradi + Ojayugma(rasi+navamsa) + Saptavargaja "
            "(Panchadha Adhi-mitra/Adhi-satru) + Drekkana.",
            "Kala: Natonnata + Paksha + Tribhaga + Abda/Masa (Hora-at-sankranti) "
            "+ Vara/Hora + Ayana + Yuddha.",
            "Chesta: Sun=Ayana, Moon=Paksha; Mars–Saturn Seeghra-kendra (BPHS); "
            "Saravali 8-fold fallback if means unavailable.",
            "Drik: Sphuta continuous degree-Drishti + 1.25/0.75; "
            "whole-sign graha-table fallback if longitudes absent.",
        ],
    }


__all__ = [
    "CLASSICAL_PLANETS",
    "MEAN_DAILY_MOTION_DEG",
    "MEAN_SOLAR_SIDEREAL_DEG_PER_DAY",
    "SAPTAVARGA_IDS",
    "SHADBALA_VARIANT",
    "abda_bala",
    "apply_yuddha_bala",
    "ayana_bala",
    "chesta_bala",
    "chesta_saravali_motion",
    "compound_relation",
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
    "resolve_seeghra_inputs",
    "sankranti_hora_lord",
    "saptavargaja_points",
    "seeghra_kendra_chesta",
    "sphuta_drishti",
    "tribhaga_bala",
    "uchcha_bala",
    "vara_bala",
]
