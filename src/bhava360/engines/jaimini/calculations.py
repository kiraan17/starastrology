from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from bhava360.chart.dignity import sign_lord
from bhava360.chart.vargas import VargaId, varga_sign
from bhava360.kernel.derived import normalize_longitude, sign_from_longitude
from bhava360.kernel.errors import KernelError, KernelErrorCode
from bhava360.kernel.models import PlanetName, SIGNS


class CharaKarakaScheme(str, Enum):
    SEVEN = "seven"
    EIGHT = "eight"


KARAKA_NAMES_SEVEN: tuple[str, ...] = (
    "Atmakaraka",
    "Amatyakaraka",
    "Bhratrikaraka",
    "Matrikaraka",
    "Putrakaraka",
    "Gnatikaraka",
    "Darakaraka",
)

KARAKA_NAMES_EIGHT: tuple[str, ...] = (
    "Atmakaraka",
    "Amatyakaraka",
    "Bhratrikaraka",
    "Matrikaraka",
    "Pitrikaraka",
    "Putrakaraka",
    "Gnatikaraka",
    "Darakaraka",
)

SEVEN_PLANETS: tuple[PlanetName, ...] = (
    PlanetName.SUN,
    PlanetName.MOON,
    PlanetName.MARS,
    PlanetName.MERCURY,
    PlanetName.JUPITER,
    PlanetName.VENUS,
    PlanetName.SATURN,
)


@dataclass(slots=True)
class CharaKaraka:
    rank: int
    name: str
    planet: PlanetName
    longitude_sidereal_deg: float
    sign: str
    degree_in_sign_used: float

    def to_dict(self) -> dict:
        return {
            "rank": self.rank,
            "name": self.name,
            "planet": self.planet.value,
            "longitude_sidereal_deg": self.longitude_sidereal_deg,
            "sign": self.sign,
            "degree_in_sign_used": self.degree_in_sign_used,
        }


def _degree_key(planet: PlanetName, longitude: float) -> float:
    """Degree-in-sign used for ranking. Rahu uses (30 - deg) provisional rule."""
    lon = normalize_longitude(longitude)
    deg = lon % 30.0
    if planet == PlanetName.RAHU:
        return 30.0 - deg
    return deg


def compute_chara_karakas(
    planet_longitudes: dict[str, float],
    *,
    scheme: CharaKarakaScheme,
) -> dict:
    """Rank planets by degree-in-sign into Chara Karakas.

    Scheme must be explicit (VARIANT-001). No silent default for production verdicts —
    callers pass seven or eight intentionally.
    """
    if scheme == CharaKarakaScheme.SEVEN:
        planets = list(SEVEN_PLANETS)
        names = KARAKA_NAMES_SEVEN
    elif scheme == CharaKarakaScheme.EIGHT:
        planets = list(SEVEN_PLANETS) + [PlanetName.RAHU]
        names = KARAKA_NAMES_EIGHT
    else:  # pragma: no cover
        raise KernelError(
            KernelErrorCode.UNSUPPORTED_CONFIG,
            f"unsupported chara karaka scheme {scheme}",
        )

    ranked = []
    for p in planets:
        if p.value not in planet_longitudes:
            raise KernelError(
                KernelErrorCode.UNSUPPORTED_PLANET,
                f"missing longitude for {p.value}",
            )
        lon = planet_longitudes[p.value]
        sign, _ = sign_from_longitude(lon)
        ranked.append((p, lon, sign, _degree_key(p, lon)))

    ranked.sort(key=lambda row: row[3], reverse=True)
    karakas = [
        CharaKaraka(
            rank=i + 1,
            name=names[i],
            planet=p,
            longitude_sidereal_deg=lon,
            sign=sign,
            degree_in_sign_used=deg,
        )
        for i, (p, lon, sign, deg) in enumerate(ranked)
    ]
    return {
        "scheme": scheme.value,
        "variant_id": "VARIANT-001",
        "karakas": [k.to_dict() for k in karakas],
        "atmakaraka": karakas[0].to_dict(),
        "notes": [
            "Chara Karaka scheme is explicit (seven|eight).",
            "Rahu degree key uses provisional (30 - deg_in_sign) in eight-karaka mode.",
            "Engine name is Jaimini — never Gemini.",
        ],
    }


def _sign_index(sign: str) -> int:
    return SIGNS.index(sign)


def compute_arudha_pada(reference_sign: str, lord_sign: str) -> dict:
    """Compute Arudha pada for a house/reference sign from its lord's sign."""
    ref_i = _sign_index(reference_sign)
    lord_i = _sign_index(lord_sign)
    count = (lord_i - ref_i) % 12
    pada_i = (lord_i + count) % 12
    exception_applied = False
    # If pada lands in reference sign or 7th from it, take 10th from calculated pada.
    if pada_i == ref_i or pada_i == (ref_i + 6) % 12:
        pada_i = (pada_i + 9) % 12
        exception_applied = True
    return {
        "reference_sign": reference_sign,
        "lord_sign": lord_sign,
        "count_signs": count,
        "arudha_sign": SIGNS[pada_i],
        "exception_applied": exception_applied,
    }


def compute_arudha_padas(
    *,
    lagna_sign: str,
    planet_signs: dict[str, str],
) -> dict:
    """A1–A12 using whole-sign houses from Lagna."""
    padas = {}
    for house in range(1, 13):
        ref_sign = SIGNS[(_sign_index(lagna_sign) + house - 1) % 12]
        lord = sign_lord(ref_sign)
        if lord is None or lord.value not in planet_signs:
            # Nodes as lords shouldn't happen for sign lords.
            continue
        lord_sign = planet_signs[lord.value]
        # For Rahu/Ketu owned signs — not applicable in standard sign lords.
        detail = compute_arudha_pada(ref_sign, lord_sign)
        detail["house"] = house
        detail["label"] = f"A{house}"
        detail["house_lord"] = lord.value
        padas[f"A{house}"] = detail
    return {
        "system": "jaimini_arudha",
        "lagna_sign": lagna_sign,
        "padas": padas,
        "arudha_lagna": padas.get("A1"),
        "notes": [
            "Whole-sign Arudha padas A1–A12.",
            "Exception: if pada falls in house sign or 7th from it, use 10th from calculated pada.",
        ],
    }


def compute_karakamsa_swamsa(
    *,
    atmakaraka_longitude: float,
    ascendant_longitude: float,
) -> dict:
    """Karakamsa = AK in D9; Swamsa = Lagna in D9."""
    karakamsa = varga_sign(atmakaraka_longitude, VargaId.D9)
    swamsa = varga_sign(ascendant_longitude, VargaId.D9)
    return {
        "karakamsa": karakamsa.to_dict(),
        "swamsa": swamsa.to_dict(),
        "notes": [
            "Karakamsa is Navamsa sign of Atmakaraka.",
            "Swamsa here is Navamsa Lagna (D9 of Ascendant).",
        ],
    }


def compute_argala(sign: str) -> dict:
    """Thin Argala/Virodha houses from a reference sign (sign-based)."""
    idx = _sign_index(sign)

    def houses(offsets: tuple[int, ...]) -> list[str]:
        # offsets are house numbers from sign (2 => +1 sign index)
        return [SIGNS[(idx + h - 1) % 12] for h in offsets]

    return {
        "reference_sign": sign,
        "argala_signs": houses((2, 4, 11)),
        "virodha_argala_signs": houses((12, 10, 3)),
        "notes": [
            "Primary argala from 2nd/4th/11th; virodha from 12th/10th/3rd.",
            "Secondary argala (3/10/12 etc.) not expanded in this thin slice.",
        ],
    }
