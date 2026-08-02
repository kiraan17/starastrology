"""Shadbala components — Candidate TEC-023 (P27b + P28a)."""

from __future__ import annotations

from datetime import datetime
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

SHADBALA_VARIANT = "shadbala_saptavargaja_candidate_v1"

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


def compute_kala_bala(
    *,
    planet: str,
    is_day: bool,
    sun_lon: float,
    moon_lon: float,
    vara_lord: str | None,
    hora_lord: str | None,
) -> dict[str, Any]:
    nat = natonnata_bala(planet=planet, is_day=is_day)
    pak = paksha_bala(planet=planet, sun_lon=sun_lon, moon_lon=moon_lon)
    vara = vara_bala(planet=planet, vara_lord=vara_lord)
    hora = hora_bala(planet=planet, hora_lord=hora_lord)
    subtotal = nat + pak + vara + hora
    return {
        "natonnata": round(nat, 6),
        "paksha": round(pak, 6),
        "vara": round(vara, 6),
        "hora": round(hora, 6),
        "subtotal": round(subtotal, 6),
        "deferred_subs": ["tribhaga", "abda", "masa", "ayana", "yuddha"],
    }


def chesta_bala(*, planet: str, is_retrograde: bool) -> dict[str, Any]:
    """
    Motional strength thin slice (Candidate).

    Mars–Saturn: 60 if retrograde else 15 (seeghra kendra deferred).
    Sun/Moon: Ayana-based Chesta deferred → 0 placeholder.
    """
    if planet in {"Sun", "Moon"}:
        return {
            "value": 0.0,
            "basis": "ayana_chesta_deferred",
            "is_retrograde": False,
        }
    if planet in CHESTA_MOTION_PLANETS:
        val = 60.0 if is_retrograde else 15.0
        return {
            "value": round(val, 6),
            "basis": "retrograde_flag_candidate",
            "is_retrograde": bool(is_retrograde),
        }
    return {"value": 0.0, "basis": "unsupported", "is_retrograde": bool(is_retrograde)}


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

    kala = compute_kala_bala(
        planet=planet,
        is_day=is_day,
        sun_lon=sun_lon,
        moon_lon=moon_lon,
        vara_lord=vara_lord,
        hora_lord=hora_lord,
    )
    chesta = chesta_bala(planet=planet, is_retrograde=is_retrograde)
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
            "kala.vara",
            "kala.hora",
            "chesta.thin",
            "drik.thin",
        ],
        "deferred_components": [
            "saptavargaja.adhi_mitra_satru",
            "kala.tribhaga",
            "kala.abda",
            "kala.masa",
            "kala.ayana",
            "kala.yuddha",
            "chesta.seeghra_kendra",
            "chesta.ayana_for_luminaries",
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
            from datetime import timedelta, timezone

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
        "planet_signs": planet_signs,
    }


def compute_shadbala_pack(chart: dict[str, Any]) -> dict[str, Any]:
    """Compute partial Shadbala for classical seven planets from a chart dict."""
    ctx = _chart_context(chart)
    planets = ctx["planets"]
    rows: list[dict[str, Any]] = []
    for name in CLASSICAL_PLANETS:
        p = planets.get(name)
        if not p:
            continue
        house = int((p.get("houses") or {}).get("rasi_house") or 0)
        if house < 1:
            continue
        rows.append(
            compute_planet_shadbala_partial(
                planet=name,
                longitude_sidereal_deg=float(p["longitude_sidereal_deg"]),
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
            )
        )

    ranked = sorted(rows, key=lambda r: r["partial_total_virupa"], reverse=True)
    return {
        "variant": SHADBALA_VARIANT,
        "unit": "virupa",
        "rupa_definition": "1 rupa = 60 virupa",
        "context": {
            "is_day": ctx["is_day"],
            "vara_lord": ctx["vara_lord"],
            "hora_lord": ctx["hora_lord"],
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
                "kala_remainder",
                "chesta_seeghra_ayana",
                "drik_classical_tables",
                "saptavargaja_adhi_mitra",
            ],
        },
        "notes": [
            "Candidate partial scaffold — not a complete BPHS Shadbala pack.",
            "Partial totals must not be compared to full-pack minima for verdicts.",
            "Sthana: Uchcha + Kendradi + Ojayugma(rasi+navamsa) + Saptavargaja + Drekkana.",
            "Saptavargaja uses permanent friendship only (Adhi-mitra/satru deferred).",
            "Kala thin: Natonnata + Paksha + Vara + Hora.",
            "Chesta thin: retrograde flag for Mars–Saturn; luminaries deferred.",
            "Drik thin: whole-sign graha aspect net (±60 clamp).",
        ],
    }


__all__ = [
    "CLASSICAL_PLANETS",
    "SAPTAVARGA_IDS",
    "SHADBALA_VARIANT",
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
    "naisargika_bala",
    "natonnata_bala",
    "ojayugma_navamsa_bala",
    "ojayugma_rasi_bala",
    "paksha_bala",
    "saptavargaja_points",
    "uchcha_bala",
    "vara_bala",
]
