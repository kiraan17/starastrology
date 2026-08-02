from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from bhava360.kernel.derived import normalize_longitude, sign_from_longitude
from bhava360.kernel.errors import KernelError, KernelErrorCode
from bhava360.kernel.models import SIGNS


class VargaId(str, Enum):
    D1 = "D1"
    D2 = "D2"
    D3 = "D3"
    D7 = "D7"
    D9 = "D9"
    D10 = "D10"
    D12 = "D12"
    D16 = "D16"
    D20 = "D20"
    D24 = "D24"
    D27 = "D27"
    D30 = "D30"
    D40 = "D40"
    D45 = "D45"
    D60 = "D60"
    D150 = "D150"


# Common Parashara set used by default (D150 opt-in / gated).
DEFAULT_VARGAS: tuple[VargaId, ...] = (
    VargaId.D1,
    VargaId.D2,
    VargaId.D3,
    VargaId.D7,
    VargaId.D9,
    VargaId.D10,
    VargaId.D12,
    VargaId.D16,
    VargaId.D20,
    VargaId.D24,
    VargaId.D27,
    VargaId.D30,
    VargaId.D40,
    VargaId.D45,
    VargaId.D60,
)


@dataclass(slots=True)
class VargaPlacement:
    varga: VargaId
    longitude_deg: float
    sign: str
    sign_degree: float
    sign_index: int

    def to_dict(self) -> dict:
        return {
            "varga": self.varga.value,
            "longitude_deg": self.longitude_deg,
            "sign": self.sign,
            "sign_degree": self.sign_degree,
            "sign_index": self.sign_index,
        }


def _sign_index(lon: float) -> int:
    return int(normalize_longitude(lon) // 30.0)


def _deg_in_sign(lon: float) -> float:
    return normalize_longitude(lon) % 30.0


def _placement_from_sign_index(varga: VargaId, sign_index: int, frac: float = 0.0) -> VargaPlacement:
    sign_index %= 12
    lon = sign_index * 30.0 + max(0.0, min(frac, 29.999999))
    sign, sign_deg = sign_from_longitude(lon)
    return VargaPlacement(
        varga=varga,
        longitude_deg=lon,
        sign=sign,
        sign_degree=sign_deg,
        sign_index=sign_index,
    )


def _odd_sign(sign_index: int) -> bool:
    # Aries=0 odd in 1-based astrology numbering.
    return (sign_index % 2) == 0


def varga_sign(longitude_sidereal_deg: float, varga: VargaId) -> VargaPlacement:
    """Compute divisional-chart sign placement from D1 sidereal longitude."""
    lon = normalize_longitude(longitude_sidereal_deg)
    s = _sign_index(lon)
    d = _deg_in_sign(lon)

    if varga == VargaId.D1:
        return _placement_from_sign_index(varga, s, d)

    if varga == VargaId.D2:
        # Hora: first/second 15° → Leo (Sun) or Cancer (Moon), parity by sign.
        first_half = d < 15.0
        if _odd_sign(s):
            sign_index = 4 if first_half else 3  # Leo / Cancer
        else:
            sign_index = 3 if first_half else 4
        frac = (d % 15.0) * 2.0
        return _placement_from_sign_index(varga, sign_index, frac)

    if varga == VargaId.D3:
        part = int(d // 10.0)  # 0,1,2
        # 1st=same, 2nd=5th, 3rd=9th
        offset = (0, 4, 8)[part]
        frac = (d % 10.0) * 3.0
        return _placement_from_sign_index(varga, s + offset, frac)

    if varga == VargaId.D7:
        part_size = 30.0 / 7.0
        part = min(int(d // part_size), 6)
        start = s if _odd_sign(s) else (s + 6) % 12
        frac = (d - part * part_size) / part_size * 30.0
        return _placement_from_sign_index(varga, start + part, frac)

    if varga == VargaId.D9:
        part_size = 30.0 / 9.0
        part = min(int(d // part_size), 8)
        modality = s % 3  # 0 movable, 1 fixed, 2 dual
        start = s if modality == 0 else (s + 8) % 12 if modality == 1 else (s + 4) % 12
        frac = (d - part * part_size) / part_size * 30.0
        return _placement_from_sign_index(varga, start + part, frac)

    if varga == VargaId.D10:
        part_size = 3.0
        part = min(int(d // part_size), 9)
        start = s if _odd_sign(s) else (s + 8) % 12
        frac = (d - part * part_size) / part_size * 30.0
        return _placement_from_sign_index(varga, start + part, frac)

    if varga == VargaId.D12:
        part_size = 2.5
        part = min(int(d // part_size), 11)
        frac = (d - part * part_size) / part_size * 30.0
        return _placement_from_sign_index(varga, s + part, frac)

    if varga in {VargaId.D16, VargaId.D20, VargaId.D24, VargaId.D27, VargaId.D30, VargaId.D40, VargaId.D45, VargaId.D60}:
        n = int(varga.value[1:])
        part_size = 30.0 / n
        part = min(int(d // part_size), n - 1)
        # Standard counting starts:
        # D16: movable from Aries, fixed from Leo, dual from Sagittarius (common modern)
        # Use widely used Parasara-style starts where documented; otherwise count from sign.
        if varga == VargaId.D16:
            modality = s % 3
            start = 0 if modality == 0 else 4 if modality == 1 else 8
        elif varga == VargaId.D20:
            modality = s % 3
            start = 0 if modality == 0 else 8 if modality == 1 else 4
        elif varga == VargaId.D24:
            start = 4 if _odd_sign(s) else 3  # Leo / Cancer common
        elif varga == VargaId.D27:
            start = s  # count from same (nakshatramsa style simplification)
        elif varga == VargaId.D30:
            # Trimsamsa uses irregular lords; approximate by 5 unequal parts mapped to signs.
            # Use equal 6° parts for scaffold; refine when source Approved.
            part_size = 6.0
            part = min(int(d // part_size), 4)
            # Odd: Mars,Saturn,Jupiter,Mercury,Venus signs cascade from Aries etc.
            odd_map = [0, 10, 8, 5, 1]  # placeholder sign indices for scaffold
            even_map = [1, 5, 8, 10, 0]
            sign_index = (odd_map if _odd_sign(s) else even_map)[part]
            frac = (d - part * part_size) / part_size * 30.0
            return _placement_from_sign_index(varga, sign_index, frac)
        elif varga == VargaId.D40:
            start = 0 if _odd_sign(s) else 6
        elif varga == VargaId.D45:
            modality = s % 3
            start = 0 if modality == 0 else 4 if modality == 1 else 8
        else:  # D60
            start = s
        frac = (d - part * part_size) / part_size * 30.0
        return _placement_from_sign_index(varga, start + part, frac)

    if varga == VargaId.D150:
        n = 150
        part_size = 30.0 / n
        part = min(int(d // part_size), n - 1)
        frac = (d - part * part_size) / part_size * 30.0
        return _placement_from_sign_index(varga, s + part, frac)

    raise KernelError(
        KernelErrorCode.UNSUPPORTED_CONFIG,
        f"unsupported varga {varga}",
    )


def assert_d150_accuracy_gate(
    birth_time_uncertainty_minutes: float | None,
    *,
    max_uncertainty_minutes: float = 1.0,
    force: bool = False,
) -> None:
    """Nadiamsa D150 is extremely time-sensitive — gate unless forced for research."""
    if force:
        return
    if birth_time_uncertainty_minutes is None:
        raise KernelError(
            KernelErrorCode.UNSUPPORTED_CONFIG,
            "D150 requires birth_time_uncertainty_minutes (accuracy gate)",
        )
    if birth_time_uncertainty_minutes > max_uncertainty_minutes:
        raise KernelError(
            KernelErrorCode.UNSUPPORTED_CONFIG,
            "D150 blocked: birth-time uncertainty exceeds gate",
            {
                "birth_time_uncertainty_minutes": birth_time_uncertainty_minutes,
                "max_uncertainty_minutes": max_uncertainty_minutes,
            },
        )


def compute_vargas(
    longitude_sidereal_deg: float,
    vargas: tuple[VargaId, ...] | list[VargaId] | None = None,
    *,
    birth_time_uncertainty_minutes: float | None = None,
    include_d150: bool = False,
    force_d150: bool = False,
) -> dict[str, dict]:
    selected = list(vargas) if vargas is not None else list(DEFAULT_VARGAS)
    if include_d150 or VargaId.D150 in selected:
        assert_d150_accuracy_gate(
            birth_time_uncertainty_minutes,
            force=force_d150,
        )
        if VargaId.D150 not in selected:
            selected.append(VargaId.D150)
    return {
        v.value: varga_sign(longitude_sidereal_deg, v).to_dict()
        for v in selected
        if v != VargaId.D150 or include_d150 or vargas is not None
    }
