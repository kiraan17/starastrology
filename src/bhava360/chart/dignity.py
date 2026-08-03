from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from bhava360.kernel.derived import normalize_longitude, sign_from_longitude
from bhava360.kernel.models import PlanetName, SIGNS


class DignityState(str, Enum):
    EXALTED = "exalted"
    DEBILITATED = "debilitated"
    OWN = "own"
    MOOLATRIKONA = "moolatrikona"
    NEUTRAL = "neutral"


# Classical exaltation signs (exact degrees stored for later precise scoring).
EXALTATION_SIGN = {
    PlanetName.SUN: "Aries",
    PlanetName.MOON: "Taurus",
    PlanetName.MARS: "Capricorn",
    PlanetName.MERCURY: "Virgo",
    PlanetName.JUPITER: "Cancer",
    PlanetName.VENUS: "Pisces",
    PlanetName.SATURN: "Libra",
}

EXALTATION_DEGREE = {
    PlanetName.SUN: 10.0,
    PlanetName.MOON: 3.0,
    PlanetName.MARS: 28.0,
    PlanetName.MERCURY: 15.0,
    PlanetName.JUPITER: 5.0,
    PlanetName.VENUS: 27.0,
    PlanetName.SATURN: 20.0,
}

DEBILITATION_SIGN = {
    PlanetName.SUN: "Libra",
    PlanetName.MOON: "Scorpio",
    PlanetName.MARS: "Cancer",
    PlanetName.MERCURY: "Pisces",
    PlanetName.JUPITER: "Capricorn",
    PlanetName.VENUS: "Virgo",
    PlanetName.SATURN: "Aries",
}

OWN_SIGNS = {
    PlanetName.SUN: {"Leo"},
    PlanetName.MOON: {"Cancer"},
    PlanetName.MARS: {"Aries", "Scorpio"},
    PlanetName.MERCURY: {"Gemini", "Virgo"},
    PlanetName.JUPITER: {"Sagittarius", "Pisces"},
    PlanetName.VENUS: {"Taurus", "Libra"},
    PlanetName.SATURN: {"Capricorn", "Aquarius"},
    PlanetName.RAHU: set(),
    PlanetName.KETU: set(),
}

# Moolatrikona ranges as (sign, start_deg_inclusive, end_deg_exclusive)
MOOLATRIKONA_RANGE = {
    PlanetName.SUN: ("Leo", 0.0, 20.0),
    PlanetName.MOON: ("Taurus", 4.0, 30.0),
    PlanetName.MARS: ("Aries", 0.0, 12.0),
    PlanetName.MERCURY: ("Virgo", 16.0, 20.0),
    PlanetName.JUPITER: ("Sagittarius", 0.0, 10.0),
    PlanetName.VENUS: ("Libra", 0.0, 15.0),
    PlanetName.SATURN: ("Aquarius", 0.0, 20.0),
}


@dataclass(slots=True)
class DignityResult:
    planet: PlanetName
    sign: str
    sign_degree: float
    states: list[DignityState]
    primary: DignityState
    exaltation_sign: str | None
    debilitation_sign: str | None
    is_combust_candidate: bool

    def to_dict(self) -> dict:
        return {
            "planet": self.planet.value,
            "sign": self.sign,
            "sign_degree": self.sign_degree,
            "states": [s.value for s in self.states],
            "primary": self.primary.value,
            "exaltation_sign": self.exaltation_sign,
            "debilitation_sign": self.debilitation_sign,
            "is_combust_candidate": self.is_combust_candidate,
        }


def _in_moolatrikona(planet: PlanetName, sign: str, sign_degree: float) -> bool:
    spec = MOOLATRIKONA_RANGE.get(planet)
    if not spec:
        return False
    m_sign, start, end = spec
    return sign == m_sign and start <= sign_degree < end


def classify_dignity(
    planet: PlanetName,
    longitude_sidereal_deg: float,
    *,
    sun_longitude_sidereal_deg: float | None = None,
    combustion_orb_deg: float = 8.4,
) -> DignityResult:
    """Classify basic dignity. Nodes have limited classical dignity here."""
    lon = normalize_longitude(longitude_sidereal_deg)
    sign, sign_deg = sign_from_longitude(lon)
    states: list[DignityState] = []

    exalt = EXALTATION_SIGN.get(planet)
    debil = DEBILITATION_SIGN.get(planet)
    if exalt and sign == exalt:
        states.append(DignityState.EXALTED)
    if debil and sign == debil:
        states.append(DignityState.DEBILITATED)
    if _in_moolatrikona(planet, sign, sign_deg):
        states.append(DignityState.MOOLATRIKONA)
    if sign in OWN_SIGNS.get(planet, set()):
        states.append(DignityState.OWN)

    if not states:
        states = [DignityState.NEUTRAL]

    # Priority for primary label
    priority = [
        DignityState.EXALTED,
        DignityState.DEBILITATED,
        DignityState.MOOLATRIKONA,
        DignityState.OWN,
        DignityState.NEUTRAL,
    ]
    primary = next(s for s in priority if s in states)

    combust = False
    if (
        sun_longitude_sidereal_deg is not None
        and planet not in {PlanetName.SUN, PlanetName.RAHU, PlanetName.KETU}
    ):
        delta = abs(
            (normalize_longitude(longitude_sidereal_deg) - normalize_longitude(sun_longitude_sidereal_deg) + 180)
            % 360
            - 180
        )
        combust = delta <= combustion_orb_deg

    return DignityResult(
        planet=planet,
        sign=sign,
        sign_degree=sign_deg,
        states=states,
        primary=primary,
        exaltation_sign=exalt,
        debilitation_sign=debil,
        is_combust_candidate=combust,
    )


def sign_lord(sign: str) -> PlanetName | None:
    lords = {
        "Aries": PlanetName.MARS,
        "Taurus": PlanetName.VENUS,
        "Gemini": PlanetName.MERCURY,
        "Cancer": PlanetName.MOON,
        "Leo": PlanetName.SUN,
        "Virgo": PlanetName.MERCURY,
        "Libra": PlanetName.VENUS,
        "Scorpio": PlanetName.MARS,
        "Sagittarius": PlanetName.JUPITER,
        "Capricorn": PlanetName.SATURN,
        "Aquarius": PlanetName.SATURN,
        "Pisces": PlanetName.JUPITER,
    }
    if sign not in SIGNS:
        return None
    return lords[sign]
