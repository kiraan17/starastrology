"""Shadbala components — Candidate TEC-023 (P27b + P28a)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from bhava360.chart.aspects import GRAHA_ASPECT_HOUSES, relative_house
from bhava360.chart.dignity import DEBILITATION_SIGN, EXALTATION_DEGREE
from bhava360.kernel.derived import normalize_longitude
from bhava360.kernel.models import PlanetName, SIGNS
from bhava360.timing.panchanga import VARA_LORDS, lunar_elongation_deg

SHADBALA_VARIANT = "shadbala_kala_chesta_drik_candidate_v1"

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
    odd = (SIGNS.index(sign) % 2) == 0
    if planet in NEUTRAL_OJAYUGMA:
        return 15.0
    if planet in MALE_PLANETS:
        return 15.0 if odd else 0.0
    if planet in FEMALE_PLANETS:
        return 15.0 if not odd else 0.0
    return 0.0


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
) -> dict[str, Any]:
    nais = naisargika_bala(planet)
    dig = dig_bala(planet=planet, rasi_house=rasi_house)
    uchcha = uchcha_bala(planet=planet, longitude_sidereal_deg=longitude_sidereal_deg)
    kend = kendradi_bala(rasi_house=rasi_house)
    oja = ojayugma_rasi_bala(planet=planet, sign=sign)
    sthana_partial = uchcha + kend + oja

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
            "subtotal": round(sthana_partial, 6),
            "deferred_subs": ["saptavargaja", "ojayugma_navamsa", "drekkana"],
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
            "kala.natonnata",
            "kala.paksha",
            "kala.vara",
            "kala.hora",
            "chesta.thin",
            "drik.thin",
        ],
        "deferred_components": [
            "sthana.saptavargaja",
            "sthana.drekkana",
            "sthana.ojayugma_navamsa",
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
                "sthana_remainder",
                "kala_remainder",
                "chesta_seeghra_ayana",
                "drik_classical_tables",
            ],
        },
        "notes": [
            "Candidate partial scaffold — not a complete BPHS Shadbala pack.",
            "Partial totals must not be compared to full-pack minima for verdicts.",
            "Kala thin: Natonnata + Paksha + Vara + Hora.",
            "Chesta thin: retrograde flag for Mars–Saturn; luminaries deferred.",
            "Drik thin: whole-sign graha aspect net (±60 clamp).",
        ],
    }


__all__ = [
    "CLASSICAL_PLANETS",
    "SHADBALA_VARIANT",
    "chesta_bala",
    "compute_kala_bala",
    "compute_planet_shadbala_partial",
    "compute_shadbala_pack",
    "dig_bala",
    "drik_bala",
    "hora_bala",
    "kendradi_bala",
    "naisargika_bala",
    "natonnata_bala",
    "ojayugma_rasi_bala",
    "paksha_bala",
    "uchcha_bala",
    "vara_bala",
]
