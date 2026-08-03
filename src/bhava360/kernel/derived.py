from __future__ import annotations

from bhava360.kernel.models import NAKSHATRAS_VEDASTRO, SIGNS


NAKSHATRA_SPAN = 360.0 / 27.0  # 13°20'
PADA_SPAN = NAKSHATRA_SPAN / 4.0  # 3°20'


def normalize_longitude(lon: float) -> float:
    return lon % 360.0


def sign_from_longitude(lon: float) -> tuple[str, float]:
    lon = normalize_longitude(lon)
    idx = int(lon // 30.0)
    return SIGNS[idx], lon - idx * 30.0


def nakshatra_from_longitude(lon: float) -> tuple[str, int, str]:
    lon = normalize_longitude(lon)
    idx = int(lon // NAKSHATRA_SPAN) % 27
    within = lon - idx * NAKSHATRA_SPAN
    pada = int(within // PADA_SPAN) + 1
    name = NAKSHATRAS_VEDASTRO[idx]
    return name, pada, f"{name} - {pada}"


def whole_sign_cusp_longitudes(ascendant_sidereal_deg: float) -> list[float]:
    """Vedic whole-sign house starts: House 1 = 0° of Ascendant sign."""
    asc = normalize_longitude(ascendant_sidereal_deg)
    house1 = float(int(asc // 30.0) * 30)
    return [normalize_longitude(house1 + 30.0 * i) for i in range(12)]


def house_index_for_longitude(longitude_deg: float, cusp_longitudes: list[float]) -> int:
    """Return 1–12 house index for longitude given 12 cusp starts in order."""
    if len(cusp_longitudes) != 12:
        raise ValueError("expected 12 cusp longitudes")
    lon = normalize_longitude(longitude_deg)
    for i in range(12):
        start = cusp_longitudes[i]
        end = cusp_longitudes[(i + 1) % 12]
        if start <= end:
            if start <= lon < end:
                return i + 1
        else:
            # wrap across 0°
            if lon >= start or lon < end:
                return i + 1
    return 12
