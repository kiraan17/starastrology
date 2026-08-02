"""Panchanga core (TEC-070): Tithi, Vara, Nakshatra, Yoga, Karana."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from bhava360.kernel.derived import NAKSHATRA_SPAN, nakshatra_from_longitude, normalize_longitude

TITHI_NAMES: tuple[str, ...] = (
    "Pratipada",
    "Dwitiya",
    "Tritiya",
    "Chaturthi",
    "Panchami",
    "Shashthi",
    "Saptami",
    "Ashtami",
    "Navami",
    "Dashami",
    "Ekadashi",
    "Dwadashi",
    "Trayodashi",
    "Chaturdashi",
)

YOGA_NAMES: tuple[str, ...] = (
    "Vishkambha",
    "Priti",
    "Ayushman",
    "Saubhagya",
    "Shobhana",
    "Atiganda",
    "Sukarma",
    "Dhriti",
    "Shula",
    "Ganda",
    "Vriddhi",
    "Dhruva",
    "Vyaghata",
    "Harshana",
    "Vajra",
    "Siddhi",
    "Vyatipata",
    "Variyan",
    "Parigha",
    "Shiva",
    "Siddha",
    "Sadhya",
    "Shubha",
    "Shukla",
    "Brahma",
    "Indra",
    "Vaidhriti",
)

MOVABLE_KARANAS: tuple[str, ...] = (
    "Bava",
    "Balava",
    "Kaulava",
    "Taitila",
    "Garaja",
    "Vanija",
    "Vishti",
)

VARA_NAMES: tuple[str, ...] = (
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
)

VARA_LORDS: tuple[str, ...] = (
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
)

PANCHANGA_VARIANT = "sidereal_lahiri_candidate_v1"


def lunar_elongation_deg(sun_lon: float, moon_lon: float) -> float:
    return normalize_longitude(moon_lon - sun_lon)


def compute_tithi(sun_lon: float, moon_lon: float) -> dict[str, Any]:
    elong = lunar_elongation_deg(sun_lon, moon_lon)
    # Each tithi = 12°
    idx = min(int(elong // 12.0), 29)  # 0..29
    paksha = "Shukla" if idx < 15 else "Krishna"
    tithi_in_paksha = (idx % 15) + 1
    if idx == 14:
        name = "Purnima"
    elif idx == 29:
        name = "Amavasya"
    else:
        name = TITHI_NAMES[idx % 15]
    frac = (elong % 12.0) / 12.0
    return {
        "index": idx + 1,  # 1..30
        "paksha": paksha,
        "tithi_in_paksha": tithi_in_paksha,
        "name": name,
        "label": f"{paksha} {name}",
        "elongation_deg": elong,
        "fraction_elapsed": frac,
    }


def compute_karana(sun_lon: float, moon_lon: float) -> dict[str, Any]:
    elong = lunar_elongation_deg(sun_lon, moon_lon)
    idx = min(int(elong // 6.0), 59)  # 0..59
    if idx == 0:
        name = "Kimstughna"
    elif idx >= 57:
        name = ("Shakuni", "Chatushpada", "Naga")[idx - 57]
    else:
        name = MOVABLE_KARANAS[(idx - 1) % 7]
    frac = (elong % 6.0) / 6.0
    return {
        "index": idx + 1,  # 1..60
        "name": name,
        "elongation_deg": elong,
        "fraction_elapsed": frac,
    }


def compute_yoga(sun_lon: float, moon_lon: float) -> dict[str, Any]:
    total = normalize_longitude(sun_lon + moon_lon)
    idx = min(int(total // NAKSHATRA_SPAN), 26)
    frac = (total % NAKSHATRA_SPAN) / NAKSHATRA_SPAN
    return {
        "index": idx + 1,
        "name": YOGA_NAMES[idx],
        "sum_longitude_deg": total,
        "fraction_elapsed": frac,
    }


def compute_nakshatra_panchanga(moon_lon: float) -> dict[str, Any]:
    name, pada, label = nakshatra_from_longitude(moon_lon)
    lon = normalize_longitude(moon_lon)
    idx = int(lon // NAKSHATRA_SPAN) % 27
    within = lon - idx * NAKSHATRA_SPAN
    frac = within / NAKSHATRA_SPAN
    return {
        "index": idx + 1,
        "name": name,
        "pada": pada,
        "label": label,
        "nameset": "vedastro_spellings",
        "fraction_elapsed": frac,
        "longitude_sidereal_deg": lon,
    }


def compute_vara_from_local(local_dt: datetime) -> dict[str, Any]:
    """Weekday with Sunday=0 indexing (Hindu vara order)."""
    # datetime.weekday(): Monday=0 .. Sunday=6 → convert to Sunday=0
    sunday_index = (local_dt.weekday() + 1) % 7
    return {
        "index": sunday_index + 1,
        "name": VARA_NAMES[sunday_index],
        "lord": VARA_LORDS[sunday_index],
        "boundary": "sunrise_local_date",
        "reference_local": local_dt.isoformat(sep=" "),
    }


def compute_panchanga_core(
    *,
    sun_lon_sidereal: float,
    moon_lon_sidereal: float,
    sunrise_local: datetime,
) -> dict[str, Any]:
    """Five limbs at a moment; Vara taken from sunrise local civil datetime."""
    tithi = compute_tithi(sun_lon_sidereal, moon_lon_sidereal)
    karana = compute_karana(sun_lon_sidereal, moon_lon_sidereal)
    yoga = compute_yoga(sun_lon_sidereal, moon_lon_sidereal)
    nak = compute_nakshatra_panchanga(moon_lon_sidereal)
    vara = compute_vara_from_local(sunrise_local)
    return {
        "tithi": tithi,
        "vara": vara,
        "nakshatra": nak,
        "yoga": yoga,
        "karana": karana,
        "sun_longitude_sidereal_deg": normalize_longitude(sun_lon_sidereal),
        "moon_longitude_sidereal_deg": normalize_longitude(moon_lon_sidereal),
        "variant": PANCHANGA_VARIANT,
        "notes": [
            "Longitudes are sidereal (chart ayanamsa); elongation-based limbs match tropical elongation.",
            "Yoga uses sidereal sun+moon sum (Candidate; some almanacs use tropical).",
            "Vara uses weekday of the local sunrise instant (sunrise boundary).",
            "Rahu Kala / Hora / Chaughadiya deferred.",
        ],
    }
