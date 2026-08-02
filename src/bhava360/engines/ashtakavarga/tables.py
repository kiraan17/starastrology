from __future__ import annotations

from dataclasses import dataclass

from bhava360.kernel.models import PlanetName, SIGNS

# Contributors in classical Ashtakavarga (no Rahu/Ketu).
BAV_PLANETS: tuple[PlanetName, ...] = (
    PlanetName.SUN,
    PlanetName.MOON,
    PlanetName.MARS,
    PlanetName.MERCURY,
    PlanetName.JUPITER,
    PlanetName.VENUS,
    PlanetName.SATURN,
)

Contributor = str  # planet name or "Lagna"

# Standard house-number tables (1–12 from contributor) used by many Vedic engines.
# Source status: Candidate classical tables — expert edition citation still required.
BAV_TABLES: dict[PlanetName, dict[Contributor, tuple[int, ...]]] = {
    PlanetName.SUN: {
        "Sun": (1, 2, 4, 7, 8, 9, 10, 11),
        "Moon": (3, 6, 10, 11),
        "Mars": (1, 2, 4, 7, 8, 9, 10, 11),
        "Mercury": (3, 5, 6, 9, 10, 11, 12),
        "Jupiter": (5, 6, 9, 11),
        "Venus": (6, 7, 12),
        "Saturn": (1, 2, 4, 7, 8, 9, 10, 11),
        "Lagna": (3, 4, 6, 10, 11, 12),
    },
    PlanetName.MOON: {
        "Sun": (3, 6, 7, 8, 10, 11),
        "Moon": (1, 3, 6, 7, 10, 11),
        "Mars": (2, 3, 5, 6, 9, 10, 11),
        "Mercury": (1, 3, 4, 5, 7, 8, 10, 11),
        "Jupiter": (1, 4, 7, 8, 10, 11, 12),
        "Venus": (3, 4, 5, 7, 9, 10, 11),
        "Saturn": (3, 5, 6, 11),
        "Lagna": (3, 6, 10, 11),
    },
    PlanetName.MARS: {
        "Sun": (3, 5, 6, 10, 11),
        "Moon": (3, 6, 8, 10, 11),
        "Mars": (1, 2, 4, 7, 8, 10, 11),
        "Mercury": (3, 5, 6, 11),
        "Jupiter": (6, 10, 11, 12),
        "Venus": (6, 8, 11, 12),
        "Saturn": (1, 4, 7, 8, 10, 11),
        "Lagna": (1, 3, 6, 11),
    },
    PlanetName.MERCURY: {
        "Sun": (5, 6, 9, 11, 12),
        "Moon": (2, 4, 6, 8, 10, 11),
        "Mars": (1, 2, 4, 7, 8, 9, 10, 11),
        "Mercury": (1, 3, 5, 6, 9, 10, 11, 12),
        "Jupiter": (6, 8, 11, 12),
        "Venus": (1, 2, 3, 4, 5, 8, 9, 11),
        "Saturn": (1, 2, 4, 7, 8, 9, 10, 11),
        "Lagna": (1, 2, 4, 6, 8, 10, 11),
    },
    PlanetName.JUPITER: {
        "Sun": (1, 2, 3, 4, 7, 8, 9, 10, 11),
        "Moon": (2, 5, 7, 9, 11),
        "Mars": (1, 2, 4, 7, 8, 10, 11),
        "Mercury": (1, 2, 4, 5, 6, 9, 10, 11),
        "Jupiter": (1, 2, 3, 4, 7, 8, 10, 11),
        "Venus": (2, 5, 6, 9, 10, 11),
        "Saturn": (3, 5, 6, 12),
        "Lagna": (1, 2, 4, 5, 6, 7, 9, 10, 11),
    },
    PlanetName.VENUS: {
        "Sun": (8, 11, 12),
        "Moon": (1, 2, 3, 4, 5, 8, 9, 11, 12),
        "Mars": (3, 5, 6, 9, 11, 12),
        "Mercury": (3, 5, 6, 9, 11),
        "Jupiter": (5, 8, 9, 10, 11),
        "Venus": (1, 2, 3, 4, 5, 8, 9, 10, 11),
        "Saturn": (3, 4, 5, 8, 9, 10, 11),
        "Lagna": (1, 2, 3, 4, 5, 8, 9, 11),
    },
    PlanetName.SATURN: {
        "Sun": (1, 2, 4, 7, 8, 10, 11),
        "Moon": (3, 6, 11),
        "Mars": (3, 5, 6, 10, 11, 12),
        "Mercury": (6, 8, 9, 10, 11, 12),
        "Jupiter": (5, 6, 11, 12),
        "Venus": (6, 11, 12),
        "Saturn": (3, 5, 6, 11),
        "Lagna": (1, 3, 4, 6, 10, 11),
    },
}


@dataclass(slots=True)
class BinduContribution:
    target_planet: PlanetName
    contributor: Contributor
    from_sign: str
    house_from_contributor: int
    to_sign: str

    def to_dict(self) -> dict:
        return {
            "target_planet": self.target_planet.value,
            "contributor": self.contributor,
            "from_sign": self.from_sign,
            "house_from_contributor": self.house_from_contributor,
            "to_sign": self.to_sign,
        }


def _sign_index(sign: str) -> int:
    return SIGNS.index(sign)


def _sign_from_house(base_sign: str, house_num: int) -> str:
    """House 1 = base_sign itself."""
    idx = (_sign_index(base_sign) + (house_num - 1)) % 12
    return SIGNS[idx]


def compute_bhinna_ashtakavarga(
    *,
    planet_signs: dict[str, str],
    lagna_sign: str,
    target: PlanetName,
) -> dict:
    """Compute one planet's BAV with reconstructable bindu contributors."""
    if target not in BAV_TABLES:
        raise ValueError(f"No BAV table for {target}")

    table = BAV_TABLES[target]
    contributor_signs: dict[Contributor, str] = {
        p.value: planet_signs[p.value] for p in BAV_PLANETS
    }
    contributor_signs["Lagna"] = lagna_sign

    contributions: list[BinduContribution] = []
    counts = {sign: 0 for sign in SIGNS}
    by_contributor = {c: {sign: 0 for sign in SIGNS} for c in table}

    for contributor, houses in table.items():
        from_sign = contributor_signs[contributor]
        for house in houses:
            to_sign = _sign_from_house(from_sign, house)
            counts[to_sign] += 1
            by_contributor[contributor][to_sign] += 1
            contributions.append(
                BinduContribution(
                    target_planet=target,
                    contributor=contributor,
                    from_sign=from_sign,
                    house_from_contributor=house,
                    to_sign=to_sign,
                )
            )

    total = sum(counts.values())
    reconstructed = len(contributions)
    return {
        "target_planet": target.value,
        "sign_bindus": counts,
        "bindus_by_contributor": by_contributor,
        "contributions": [c.to_dict() for c in contributions],
        "total_bindus": total,
        "reconstructed_from_contributions": reconstructed,
        "reconstruction_ok": total == reconstructed,
        "table_variant": "standard_candidate_v1",
    }


def compute_sarva_ashtakavarga(
    *,
    planet_signs: dict[str, str],
    lagna_sign: str,
) -> dict:
    """SAV = per-sign sum of the seven Bhinnashtakavargas."""
    bavs = [
        compute_bhinna_ashtakavarga(
            planet_signs=planet_signs,
            lagna_sign=lagna_sign,
            target=p,
        )
        for p in BAV_PLANETS
    ]
    sav = {sign: 0 for sign in SIGNS}
    for bav in bavs:
        for sign, n in bav["sign_bindus"].items():
            sav[sign] += n
    return {
        "sign_bindus": sav,
        "total_bindus": sum(sav.values()),
        "bhinnas": {b["target_planet"]: b for b in bavs},
        "notes": [
            "SAV is sum of seven BAVs (Sun–Saturn).",
            "Bindu contributors are retained per BAV for audit/reconstruction.",
            "Shodhana / Sodhya Pinda / Prastara not in this thin slice.",
        ],
        "table_variant": "standard_candidate_v1",
    }


# Kakshya lords in each sign (8 equal 3°45' parts).
KAKSHYA_LORD_NAMES: tuple[str, ...] = (
    "Saturn",
    "Jupiter",
    "Mars",
    "Sun",
    "Venus",
    "Mercury",
    "Moon",
    "Lagna",
)
KAKSHYA_SPAN = 30.0 / 8.0  # 3°45'


def kakshya_for_longitude(sign_degree: float) -> dict:
    """Return kakshya index/lord for degree-within-sign (0–30)."""
    d = max(0.0, min(sign_degree, 29.999999))
    idx = min(int(d // KAKSHYA_SPAN), 7)
    return {
        "kakshya_index": idx + 1,
        "kakshya_lord": KAKSHYA_LORD_NAMES[idx],
        "kakshya_span_deg": KAKSHYA_SPAN,
        "degree_in_sign": sign_degree,
    }
