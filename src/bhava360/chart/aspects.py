from __future__ import annotations

from dataclasses import dataclass

from bhava360.chart.dignity import sign_lord
from bhava360.kernel.derived import normalize_longitude
from bhava360.kernel.models import PlanetName, SIGNS

# Whole-sign graha aspect houses counted from the planet (1 = own sign).
# Special aspects are provisional classical defaults.
GRAHA_ASPECT_HOUSES: dict[PlanetName, tuple[int, ...]] = {
    PlanetName.SUN: (7,),
    PlanetName.MOON: (7,),
    PlanetName.MERCURY: (7,),
    PlanetName.VENUS: (7,),
    PlanetName.MARS: (4, 7, 8),
    PlanetName.JUPITER: (5, 7, 9),
    PlanetName.SATURN: (3, 7, 10),
    # Common modern treatment for nodes; mark provisional in notes.
    PlanetName.RAHU: (5, 7, 9),
    PlanetName.KETU: (5, 7, 9),
}


@dataclass(slots=True)
class GrahaAspect:
    from_planet: PlanetName
    to_planet: PlanetName
    aspect_houses: tuple[int, ...]
    matched_house: int
    from_sign: str
    to_sign: str

    def to_dict(self) -> dict:
        return {
            "from_planet": self.from_planet.value,
            "to_planet": self.to_planet.value,
            "aspect_houses": list(self.aspect_houses),
            "matched_house": self.matched_house,
            "from_sign": self.from_sign,
            "to_sign": self.to_sign,
            "system": "graha_whole_sign",
        }


def _sign_index(sign: str) -> int:
    return SIGNS.index(sign)


def _sign_after(sign: str, houses: int) -> str:
    """houses=1 => same sign; houses=7 => opposite."""
    return SIGNS[(_sign_index(sign) + houses - 1) % 12]


def relative_house(from_sign: str, to_sign: str) -> int:
    return ((_sign_index(to_sign) - _sign_index(from_sign)) % 12) + 1


def graha_aspects_between(
    from_planet: PlanetName,
    from_sign: str,
    to_planet: PlanetName,
    to_sign: str,
) -> GrahaAspect | None:
    if from_planet == to_planet:
        return None
    houses = GRAHA_ASPECT_HOUSES[from_planet]
    rel = relative_house(from_sign, to_sign)
    if rel in houses:
        return GrahaAspect(
            from_planet=from_planet,
            to_planet=to_planet,
            aspect_houses=houses,
            matched_house=rel,
            from_sign=from_sign,
            to_sign=to_sign,
        )
    return None


def compute_graha_aspects(planet_signs: dict[str, str]) -> list[dict]:
    """Directed whole-sign graha aspects for all planet pairs."""
    names = [PlanetName(n) for n in planet_signs]
    out: list[dict] = []
    for a in names:
        for b in names:
            asp = graha_aspects_between(a, planet_signs[a.value], b, planet_signs[b.value])
            if asp:
                out.append(asp.to_dict())
    return out


def _sign_modality(sign: str) -> str:
    idx = _sign_index(sign)
    return ("movable", "fixed", "dual")[idx % 3]


def jaimini_rashi_aspect_targets(sign: str) -> list[str]:
    """Jaimini rashi drishti targets from a sign."""
    modality = _sign_modality(sign)
    idx = _sign_index(sign)
    if modality == "movable":
        # Aspects all fixed signs except the adjacent next fixed (idx+1).
        fixed = [SIGNS[i] for i in range(12) if i % 3 == 1]
        excluded = SIGNS[(idx + 1) % 12]
        return [s for s in fixed if s != excluded]
    if modality == "fixed":
        # Aspects all movable except adjacent previous movable (idx-1).
        movable = [SIGNS[i] for i in range(12) if i % 3 == 0]
        excluded = SIGNS[(idx - 1) % 12]
        return [s for s in movable if s != excluded]
    # dual aspects other duals
    dual = [SIGNS[i] for i in range(12) if i % 3 == 2]
    return [s for s in dual if s != sign]


def compute_rashi_aspects(planet_signs: dict[str, str] | None = None) -> dict:
    """Sign-to-sign Jaimini aspects; optional planet overlays."""
    sign_map = {sign: jaimini_rashi_aspect_targets(sign) for sign in SIGNS}
    planet_links: list[dict] = []
    if planet_signs:
        for a, sa in planet_signs.items():
            targets = set(sign_map[sa])
            for b, sb in planet_signs.items():
                if a == b:
                    continue
                if sb in targets:
                    planet_links.append(
                        {
                            "from_planet": a,
                            "to_planet": b,
                            "from_sign": sa,
                            "to_sign": sb,
                            "system": "jaimini_rashi",
                        }
                    )
    return {
        "system": "jaimini_rashi",
        "sign_aspects": sign_map,
        "planet_aspects": planet_links,
        "notes": [
            "Jaimini rashi drishti (movable/fixed/dual rules).",
            "Do not label this engine Gemini.",
        ],
    }


def compute_conjunctions(planet_signs: dict[str, str]) -> list[dict]:
    by_sign: dict[str, list[str]] = {}
    for planet, sign in planet_signs.items():
        by_sign.setdefault(sign, []).append(planet)
    out = []
    for sign, planets in by_sign.items():
        if len(planets) > 1:
            out.append({"sign": sign, "planets": sorted(planets), "system": "sign_conjunction"})
    return out


def build_relationship_graph(planet_signs: dict[str, str]) -> dict:
    """Reusable relationship graph: dignity lords, dispositor chain, aspects, conjunctions."""
    graha = compute_graha_aspects(planet_signs)
    rashi = compute_rashi_aspects(planet_signs)
    conjunctions = compute_conjunctions(planet_signs)

    nodes = []
    edges = []
    for planet, sign in planet_signs.items():
        lord = sign_lord(sign)
        nodes.append(
            {
                "id": planet,
                "type": "planet",
                "sign": sign,
                "sign_lord": lord.value if lord else None,
            }
        )
        if lord:
            edges.append(
                {
                    "from": planet,
                    "to": lord.value,
                    "type": "dispositor",
                }
            )

    for sign in SIGNS:
        nodes.append({"id": f"sign:{sign}", "type": "sign", "sign": sign})

    for asp in graha:
        edges.append(
            {
                "from": asp["from_planet"],
                "to": asp["to_planet"],
                "type": "graha_aspect",
                "matched_house": asp["matched_house"],
            }
        )
    for asp in rashi["planet_aspects"]:
        edges.append(
            {
                "from": asp["from_planet"],
                "to": asp["to_planet"],
                "type": "rashi_aspect",
            }
        )
    for conj in conjunctions:
        planets = conj["planets"]
        for i, a in enumerate(planets):
            for b in planets[i + 1 :]:
                edges.append({"from": a, "to": b, "type": "conjunction", "sign": conj["sign"]})
                edges.append({"from": b, "to": a, "type": "conjunction", "sign": conj["sign"]})

    # Dispositor chain until repeat/loop.
    chains = {}
    for planet in planet_signs:
        chain = [planet]
        seen = {planet}
        current = planet
        for _ in range(12):
            sign = planet_signs[current]
            lord = sign_lord(sign)
            if lord is None:
                break
            nxt = lord.value
            chain.append(nxt)
            if nxt in seen:
                break
            seen.add(nxt)
            if nxt not in planet_signs:
                break
            current = nxt
        chains[planet] = chain

    return {
        "nodes": nodes,
        "edges": edges,
        "graha_aspects": graha,
        "rashi_aspects": rashi,
        "conjunctions": conjunctions,
        "dispositor_chains": chains,
        "notes": [
            "Graha aspects are whole-sign Parashara-style with special aspects.",
            "Rahu/Ketu 5/7/9 aspects are provisional.",
            "Rashi aspects are Jaimini (not 'Gemini').",
        ],
    }
