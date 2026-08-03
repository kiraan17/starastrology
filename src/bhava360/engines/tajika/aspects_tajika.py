"""Tajika degree aspects + simple Ithasala flag — Candidate (TEC-078)."""

from __future__ import annotations

from typing import Any

from bhava360.kernel.derived import normalize_longitude

ASPECT_VARIANT = "tajika_aspects_candidate_v1"

# Angle → (name, default orb degrees). Candidate orb table.
TAJIKA_ASPECTS: tuple[tuple[float, str, float], ...] = (
    (0.0, "conjunction", 8.0),
    (60.0, "sextile", 6.0),
    (90.0, "square", 8.0),
    (120.0, "trine", 8.0),
    (180.0, "opposition", 8.0),
)

ASPECT_PLANETS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")


def circular_separation(a: float, b: float) -> float:
    """Unsigned shortest separation in [0, 180]."""
    return abs((normalize_longitude(a) - normalize_longitude(b) + 180.0) % 360.0 - 180.0)


def signed_separation(from_lon: float, to_lon: float) -> float:
    """Signed shortest delta to_lon − from_lon in (−180, 180]."""
    return (normalize_longitude(to_lon) - normalize_longitude(from_lon) + 180.0) % 360.0 - 180.0


def match_tajika_aspect(separation_deg: float) -> dict[str, Any] | None:
    sep = abs(float(separation_deg))
    best = None
    for angle, name, orb in TAJIKA_ASPECTS:
        orb_err = abs(sep - angle)
        if orb_err <= orb and (best is None or orb_err < best["orb_error_deg"]):
            best = {
                "aspect": name,
                "exact_angle_deg": angle,
                "orb_allow_deg": orb,
                "orb_error_deg": round(orb_err, 6),
            }
    return best


def _is_applying(
    *,
    sep_signed: float,
    exact_angle: float,
    speed_a: float,
    speed_b: float,
) -> bool | None:
    """
    Applying if relative motion reduces distance to the exact aspect angle.

    Uses signed separation of B from A and relative speed (B−A longitude speed).
    """
    # Work in absolute separation space toward exact_angle on the short arc.
    sep = abs(sep_signed)
    # Relative speed of B vs A
    rel = float(speed_b) - float(speed_a)
    if abs(rel) < 1e-9:
        return None
    # If sep_signed > 0, B is ahead of A on short arc; closing toward 0 needs rel < 0 for conjunction.
    # Generalize: distance to exact aspect along current short-arc side.
    # For simplicity: for conjunction (0), applying when |sep| is decreasing.
    # d/dt |sep_signed| ≈ sign(sep_signed) * rel  when considering B−A.
    # |sep| decreases when sep_signed * rel < 0.
    if exact_angle == 0.0:
        return (sep_signed * rel) < 0

    # For non-zero aspects, consider distance to +exact and −exact on the circle.
    # Choose the nearer target angle with sign matching sep_signed direction.
    target = exact_angle if abs(sep_signed - exact_angle) <= abs(sep_signed + exact_angle) else -exact_angle
    # Distance to target with sign
    dist = sep_signed - target
    # Applying when dist and rel have opposite signs (closing)
    return (dist * rel) < 0


def compute_tajika_aspects(
    planets: list[dict[str, Any]],
    *,
    planet_filter: tuple[str, ...] = ASPECT_PLANETS,
) -> dict[str, Any]:
    """
    Pairwise Tajika degree aspects among classical planets.

    Expects each planet dict to include longitude_sidereal_deg and optionally speed_longitude.
    """
    by_name = {
        p["planet"]: p
        for p in planets
        if p.get("planet") in planet_filter and "longitude_sidereal_deg" in p
    }
    names = [n for n in planet_filter if n in by_name]
    aspects: list[dict[str, Any]] = []
    ithasala: list[dict[str, Any]] = []

    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            pa, pb = by_name[a], by_name[b]
            lon_a = float(pa["longitude_sidereal_deg"])
            lon_b = float(pb["longitude_sidereal_deg"])
            sep = circular_separation(lon_a, lon_b)
            matched = match_tajika_aspect(sep)
            if not matched:
                continue
            sep_signed = signed_separation(lon_a, lon_b)
            speed_a = float(pa.get("speed_longitude") or 0.0)
            speed_b = float(pb.get("speed_longitude") or 0.0)
            applying = _is_applying(
                sep_signed=sep_signed,
                exact_angle=float(matched["exact_angle_deg"]),
                speed_a=speed_a,
                speed_b=speed_b,
            )
            # Faster planet is the one with higher absolute longitude speed
            if abs(speed_a) >= abs(speed_b):
                faster, slower = a, b
            else:
                faster, slower = b, a
            row = {
                "from_planet": a,
                "to_planet": b,
                "separation_deg": round(sep, 6),
                "applying": applying,
                "faster_planet": faster,
                "slower_planet": slower,
                **matched,
            }
            aspects.append(row)
            # Ithasala Candidate: applying aspect, faster applying to slower, within orb
            if applying is True:
                ithasala.append(
                    {
                        **row,
                        "yoga": "ithasala_candidate",
                        "notes": "Applying Tajika aspect; full Ithasala/Isarpha rules deferred.",
                    }
                )

    return {
        "variant": ASPECT_VARIANT,
        "status": "Candidate",
        "orb_table": [
            {"aspect": name, "angle_deg": angle, "orb_deg": orb}
            for angle, name, orb in TAJIKA_ASPECTS
        ],
        "aspects": aspects,
        "ithasala_candidates": ithasala,
        "source_note": "SRC-012 edition citation pending; orbs/Ithasala are Candidate defaults.",
    }


__all__ = [
    "ASPECT_PLANETS",
    "ASPECT_VARIANT",
    "TAJIKA_ASPECTS",
    "circular_separation",
    "compute_tajika_aspects",
    "match_tajika_aspect",
]
