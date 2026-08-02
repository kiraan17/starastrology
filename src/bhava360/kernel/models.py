from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class PlanetName(str, Enum):
    SUN = "Sun"
    MOON = "Moon"
    MARS = "Mars"
    MERCURY = "Mercury"
    JUPITER = "Jupiter"
    VENUS = "Venus"
    SATURN = "Saturn"
    RAHU = "Rahu"
    KETU = "Ketu"


class AyanamsaMode(str, Enum):
    LAHIRI = "lahiri"
    KP = "kp"


class HouseSystem(str, Enum):
    WHOLE_SIGN = "whole_sign"
    PLACIDUS = "placidus"


class NodeType(str, Enum):
    MEAN = "mean"
    TRUE = "true"


class EphemerisMode(str, Enum):
    """Swiss Ephemeris computation backend."""

    MOSHIER = "moshier"
    SWISSEPH_FILES = "swisseph_files"


SIGNS = (
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
)

# VedAstro-facing spellings used in SPIKE-01 fixtures (comparator names).
NAKSHATRAS_VEDASTRO = (
    "Aswini",
    "Bharani",
    "Krithika",
    "Rohini",
    "Mrigasira",
    "Aridra",
    "Punarvasu",
    "Pushyami",
    "Aslesha",
    "Makha",
    "Pubba",
    "Uttara",
    "Hasta",
    "Chitta",
    "Swathi",
    "Vishaka",
    "Anuradha",
    "Jyesta",
    "Moola",
    "Poorvashada",
    "Uttarashada",
    "Sravana",
    "Dhanishta",
    "Satabhisha",
    "Poorvabhadra",
    "Uttarabhadra",
    "Revathi",
)


@dataclass(slots=True)
class SubjectInput:
    local_datetime: datetime
    timezone_offset_minutes: int
    latitude: float | None = None
    longitude: float | None = None
    location_label: str | None = None
    birth_time_uncertainty_minutes: float | None = None
    input_kind: str = "birth"

    def validate(self) -> None:
        from bhava360.kernel.errors import KernelError, KernelErrorCode

        if self.local_datetime.tzinfo is not None:
            raise KernelError(
                KernelErrorCode.INVALID_DATETIME,
                "local_datetime must be naive civil time; pass timezone_offset_minutes separately",
            )
        if not -14 * 60 <= self.timezone_offset_minutes <= 14 * 60:
            raise KernelError(
                KernelErrorCode.INVALID_TIMEZONE,
                "timezone_offset_minutes out of range",
                {"timezone_offset_minutes": self.timezone_offset_minutes},
            )
        if self.latitude is not None and not -90 <= self.latitude <= 90:
            raise KernelError(
                KernelErrorCode.INVALID_LOCATION,
                "latitude out of range",
                {"latitude": self.latitude},
            )
        if self.longitude is not None and not -180 <= self.longitude <= 180:
            raise KernelError(
                KernelErrorCode.INVALID_LOCATION,
                "longitude out of range",
                {"longitude": self.longitude},
            )


@dataclass(slots=True)
class ChartConfig:
    ayanamsa: AyanamsaMode = AyanamsaMode.LAHIRI
    house_system: HouseSystem = HouseSystem.WHOLE_SIGN
    node_type: NodeType = NodeType.MEAN
    ephemeris_mode: EphemerisMode = EphemerisMode.MOSHIER
    ephemeris_path: str | None = None
    calc_library_version: str = "bhava360-kernel-0.1.0"
    variant_config: dict[str, Any] = field(default_factory=dict)

    def stamp(self) -> dict[str, Any]:
        return {
            "ayanamsa": self.ayanamsa.value,
            "house_system": self.house_system.value,
            "node_type": self.node_type.value,
            "ephemeris_mode": self.ephemeris_mode.value,
            "ephemeris_path": self.ephemeris_path,
            "calc_library_version": self.calc_library_version,
            "variant_config": dict(self.variant_config),
        }


@dataclass(slots=True)
class PlanetPosition:
    planet: PlanetName
    longitude_sidereal_deg: float
    longitude_tropical_deg: float | None
    latitude_deg: float
    speed_longitude: float
    is_retrograde: bool
    sign: str
    sign_degree: float
    nakshatra: str
    pada: int
    nakshatra_label: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["planet"] = self.planet.value
        return data


@dataclass(slots=True)
class ResolvedTime:
    local_datetime: datetime
    utc_datetime: datetime
    timezone_offset_minutes: int
    julian_day_ut: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "local_datetime": self.local_datetime.isoformat(sep=" "),
            "utc_datetime": self.utc_datetime.isoformat(),
            "timezone_offset_minutes": self.timezone_offset_minutes,
            "julian_day_ut": self.julian_day_ut,
        }
