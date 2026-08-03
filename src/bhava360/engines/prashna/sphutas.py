"""Prashna Marga calculable sphutas — Candidate (TEC-086)."""

from __future__ import annotations

from typing import Any

from bhava360.kernel.derived import (
    house_index_for_longitude,
    nakshatra_from_longitude,
    normalize_longitude,
    sign_from_longitude,
    whole_sign_cusp_longitudes,
)

SPHUTA_VARIANT = "prashna_sphuta_candidate_v1"


def _point(lon: float, *, lagna_longitude: float | None = None) -> dict[str, Any]:
    lon = normalize_longitude(lon)
    sign, sign_deg = sign_from_longitude(lon)
    nak, pada, label = nakshatra_from_longitude(lon)
    house = None
    if lagna_longitude is not None:
        house = house_index_for_longitude(lon, whole_sign_cusp_longitudes(lagna_longitude))
    return {
        "longitude_sidereal_deg": lon,
        "sign": sign,
        "sign_degree": sign_deg,
        "nakshatra": nak,
        "pada": pada,
        "nakshatra_label": label,
        "house_from_lagna": house,
    }


def trisphuta(
    *,
    lagna_longitude: float,
    moon_longitude: float,
    sun_longitude: float,
) -> dict[str, Any]:
    """Trisphuta = Lagna + Moon + Sun (mod 360)."""
    lon = normalize_longitude(lagna_longitude + moon_longitude + sun_longitude)
    return {
        "id": "trisphuta",
        "name": "Trisphuta",
        "formula": "Lagna + Moon + Sun",
        **_point(lon, lagna_longitude=lagna_longitude),
    }


def chatusphuta(
    *,
    trisphuta_longitude: float,
    gulika_longitude: float,
    lagna_longitude: float,
) -> dict[str, Any]:
    """Chatusphuta = Trisphuta + Gulika (mod 360)."""
    lon = normalize_longitude(trisphuta_longitude + gulika_longitude)
    return {
        "id": "chatusphuta",
        "name": "Chatusphuta",
        "formula": "Trisphuta + Gulika",
        **_point(lon, lagna_longitude=lagna_longitude),
    }


def compute_prashna_sphutas(
    *,
    lagna_longitude: float,
    moon_longitude: float,
    sun_longitude: float,
    gulika_longitude: float | None = None,
) -> dict[str, Any]:
    tri = trisphuta(
        lagna_longitude=lagna_longitude,
        moon_longitude=moon_longitude,
        sun_longitude=sun_longitude,
    )
    out: dict[str, Any] = {
        "variant": SPHUTA_VARIANT,
        "trisphuta": tri,
        "gulika": None,
        "chatusphuta": None,
    }
    if gulika_longitude is not None:
        out["gulika"] = {
            "id": "gulika",
            "name": "Gulika",
            "formula": "Lagna at start of daytime Gulika kala (Candidate)",
            **_point(gulika_longitude, lagna_longitude=lagna_longitude),
        }
        out["chatusphuta"] = chatusphuta(
            trisphuta_longitude=float(tri["longitude_sidereal_deg"]),
            gulika_longitude=gulika_longitude,
            lagna_longitude=lagna_longitude,
        )
    return out


__all__ = [
    "SPHUTA_VARIANT",
    "chatusphuta",
    "compute_prashna_sphutas",
    "trisphuta",
]
