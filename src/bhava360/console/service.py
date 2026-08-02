from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from bhava360.chart.builder import ChartConstructor
from bhava360.engines.ashtakavarga import run_ashtakavarga_engine
from bhava360.engines.chakra import run_nakshatra_chakra_engine, run_sudarshana_engine
from bhava360.engines.classification import run_classification_engine
from bhava360.engines.compatibility import run_compatibility_engine
from bhava360.engines.jaimini import run_jaimini_engine
from bhava360.engines.kp import run_kp_engine
from bhava360.engines.nadi import run_nakshatra_nadi_engine
from bhava360.engines.parashara import run_parashara_engine
from bhava360.engines.prashna import run_prashna_engine
from bhava360.engines.progression import run_bhrigu_bindu_engine
from bhava360.engines.tajika import run_tajika_annual_engine
from bhava360.kernel.models import AyanamsaMode, ChartConfig, HouseSystem, SubjectInput
from bhava360.timing.muhurta_event_engine import run_muhurta_event_engine
from bhava360.timing.panchanga_engine import run_panchanga_engine


def parse_subject(
    *,
    date_str: str,
    time_str: str,
    offset_str: str,
    latitude: float,
    longitude: float,
    location_label: str,
    uncertainty_minutes: float | None,
    timezone_id: str | None = None,
    dst_ambiguity_policy: str = "earlier",
) -> SubjectInput:
    local = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    tz_id = (timezone_id or "").strip() or None
    offset_minutes: int | None = None
    if tz_id is None:
        sign = 1
        off = offset_str.strip()
        if off.startswith("-"):
            sign = -1
            off = off[1:]
        elif off.startswith("+"):
            off = off[1:]
        hh, mm = off.split(":")
        offset_minutes = sign * (int(hh) * 60 + int(mm))
    return SubjectInput(
        local_datetime=local,
        timezone_offset_minutes=offset_minutes,
        timezone_id=tz_id,
        dst_ambiguity_policy=dst_ambiguity_policy,
        latitude=latitude,
        longitude=longitude,
        location_label=location_label or None,
        birth_time_uncertainty_minutes=uncertainty_minutes,
    )


def build_config(ayanamsa: str, house_system: str) -> ChartConfig:
    return ChartConfig(
        ayanamsa=AyanamsaMode(ayanamsa),
        house_system=HouseSystem(house_system),
    )


def run_verification(
    subject: SubjectInput,
    *,
    ayanamsa: str = "lahiri",
    house_system: str = "whole_sign",
    engines: list[str] | None = None,
    jaimini_chara_scheme: str = "seven",
    target_year: int | None = None,
    annual_location_rule: str = "birth_place",
    ashtamangala_counts: str | list | dict | None = None,
    question_text: str | None = None,
    partner_subject: SubjectInput | None = None,
) -> dict[str, Any]:
    """Run selected verification engines and return a structured report."""
    selected = engines or ["chart", "parashara", "ashtakavarga"]
    config = build_config(ayanamsa, house_system)
    report: dict[str, Any] = {
        "report_type": "bhava360_internal_verification",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input": {
            "local_datetime": subject.local_datetime.isoformat(sep=" "),
            "timezone_offset_minutes": subject.timezone_offset_minutes,
            "timezone_id": subject.timezone_id,
            "dst_ambiguity_policy": subject.dst_ambiguity_policy,
            "latitude": subject.latitude,
            "longitude": subject.longitude,
            "location_label": subject.location_label,
            "birth_time_uncertainty_minutes": subject.birth_time_uncertainty_minutes,
            "ayanamsa": ayanamsa,
            "house_system": house_system,
            "engines": selected,
            "jaimini_chara_scheme": jaimini_chara_scheme,
            "target_year": target_year,
            "annual_location_rule": annual_location_rule,
            "ashtamangala_counts_provided": bool(ashtamangala_counts),
            "question_text": question_text,
            "partner_provided": partner_subject is not None,
        },
        "sections": {},
        "errors": [],
    }

    chart = None
    needs_chart = any(
        e in selected
        for e in (
            "chart",
            "parashara",
            "ashtakavarga",
            "jaimini",
            "nadi",
            "panchanga",
            "muhurta_events",
            "tajika",
            "sudarshana",
            "bhrigu_bindu",
            "nakshatra_chakra",
            "classification",
            "prashna",
        )
    )
    if needs_chart:
        try:
            chart = ChartConstructor(config).build(subject).to_dict()
            report["sections"]["chart"] = chart
        except Exception as exc:  # noqa: BLE001
            report["errors"].append({"section": "chart", "error": str(exc)})

    if "parashara" in selected:
        try:
            if chart is None:
                raise RuntimeError("chart required for Parashara")
            report["sections"]["parashara"] = run_parashara_engine(chart)
        except Exception as exc:  # noqa: BLE001
            report["errors"].append({"section": "parashara", "error": str(exc)})

    if "ashtakavarga" in selected:
        try:
            report["sections"]["ashtakavarga"] = run_ashtakavarga_engine(
                subject, config=config, chart=chart
            )
        except Exception as exc:  # noqa: BLE001
            report["errors"].append({"section": "ashtakavarga", "error": str(exc)})

    if "jaimini" in selected:
        try:
            if chart is None:
                raise RuntimeError("chart required for Jaimini")
            report["sections"]["jaimini"] = run_jaimini_engine(
                chart=chart,
                chara_karaka_scheme=jaimini_chara_scheme,
            )
        except Exception as exc:  # noqa: BLE001
            report["errors"].append({"section": "jaimini", "error": str(exc)})

    if "nadi" in selected:
        try:
            if chart is None:
                raise RuntimeError("chart required for Nakshatra Nadi")
            report["sections"]["nadi"] = run_nakshatra_nadi_engine(
                chart=chart,
                attempt_chains=True,
            )
        except Exception as exc:  # noqa: BLE001
            report["errors"].append({"section": "nadi", "error": str(exc)})

    if "panchanga" in selected:
        try:
            report["sections"]["panchanga"] = run_panchanga_engine(
                subject, config=config, chart=chart
            )
        except Exception as exc:  # noqa: BLE001
            report["errors"].append({"section": "panchanga", "error": str(exc)})

    if "muhurta_events" in selected:
        try:
            pan = report["sections"].get("panchanga")
            report["sections"]["muhurta_events"] = run_muhurta_event_engine(
                subject,
                config=config,
                chart=chart,
                panchanga=pan,
            )
        except Exception as exc:  # noqa: BLE001
            report["errors"].append({"section": "muhurta_events", "error": str(exc)})

    if "kp" in selected:
        try:
            # KP path enforces its own ayanamsa/house system.
            report["sections"]["kp"] = run_kp_engine(subject)
        except Exception as exc:  # noqa: BLE001
            report["errors"].append({"section": "kp", "error": str(exc)})

    if "tajika" in selected:
        try:
            report["sections"]["tajika"] = run_tajika_annual_engine(
                subject,
                config=config,
                chart=chart,
                target_year=target_year,
                location_rule=annual_location_rule,
            )
        except Exception as exc:  # noqa: BLE001
            report["errors"].append({"section": "tajika", "error": str(exc)})

    if "sudarshana" in selected:
        try:
            if chart is None:
                raise RuntimeError("chart required for Sudarshana")
            report["sections"]["sudarshana"] = run_sudarshana_engine(chart=chart)
        except Exception as exc:  # noqa: BLE001
            report["errors"].append({"section": "sudarshana", "error": str(exc)})

    if "bhrigu_bindu" in selected:
        try:
            if chart is None:
                raise RuntimeError("chart required for Bhrigu Bindu")
            report["sections"]["bhrigu_bindu"] = run_bhrigu_bindu_engine(chart=chart)
        except Exception as exc:  # noqa: BLE001
            report["errors"].append({"section": "bhrigu_bindu", "error": str(exc)})

    if "nakshatra_chakra" in selected:
        try:
            if chart is None:
                raise RuntimeError("chart required for nakshatra chakras")
            report["sections"]["nakshatra_chakra"] = run_nakshatra_chakra_engine(chart=chart)
        except Exception as exc:  # noqa: BLE001
            report["errors"].append({"section": "nakshatra_chakra", "error": str(exc)})

    if "classification" in selected:
        try:
            if chart is None:
                raise RuntimeError("chart required for classification")
            report["sections"]["classification"] = run_classification_engine(chart=chart)
        except Exception as exc:  # noqa: BLE001
            report["errors"].append({"section": "classification", "error": str(exc)})

    if "prashna" in selected:
        try:
            report["sections"]["prashna"] = run_prashna_engine(
                subject,
                config=config,
                chart=chart,
                ashtamangala_counts=ashtamangala_counts,
                question_text=question_text,
            )
        except Exception as exc:  # noqa: BLE001
            report["errors"].append({"section": "prashna", "error": str(exc)})

    if "compatibility" in selected:
        try:
            if partner_subject is None:
                raise RuntimeError("partner subject required for compatibility/Ashtakoota")
            report["sections"]["compatibility"] = run_compatibility_engine(
                boy_subject=subject,
                girl_subject=partner_subject,
                config=config,
            )
        except Exception as exc:  # noqa: BLE001
            report["errors"].append({"section": "compatibility", "error": str(exc)})

    report["summary"] = _summarize(report)
    return report


def _summarize(report: dict[str, Any]) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "sections_present": list(report["sections"].keys()),
        "error_count": len(report["errors"]),
    }
    chart = report["sections"].get("chart")
    if chart:
        summary["calc_library_version"] = chart.get("config", {}).get("calc_library_version")
        summary["ayanamsa_degrees"] = chart.get("ayanamsa_degrees")
        if chart.get("dashas"):
            summary["vimshottari_balance_lord"] = chart["dashas"]["balance"]["lord"]
            summary["vimshottari_balance_years"] = chart["dashas"]["balance"]["balance_years"]
        if chart.get("relationships"):
            summary["relationship_edge_count"] = len(chart["relationships"].get("edges", []))
            summary["graha_aspect_count"] = len(chart["relationships"].get("graha_aspects", []))
            summary["conjunction_count"] = len(chart["relationships"].get("conjunctions", []))
        planets = []
        for p in chart.get("planets", []):
            planets.append(
                {
                    "planet": p["planet"],
                    "longitude": p["longitude_sidereal_deg"],
                    "sign": p["sign"],
                    "nakshatra": p["nakshatra_label"],
                    "rasi_house": p.get("houses", {}).get("rasi_house"),
                    "dignity": p.get("dignity", {}).get("primary"),
                }
            )
        summary["planets"] = planets
        asc = chart.get("angles", {}).get("whole_sign", {}).get("ascendant", {})
        summary["ascendant"] = {
            "longitude": asc.get("longitude_sidereal_deg"),
            "sign": asc.get("sign"),
            "nakshatra": asc.get("nakshatra_label"),
        }
        rt = chart.get("resolved_time") or {}
        summary["timezone_source"] = rt.get("timezone_source")
        summary["timezone_id"] = rt.get("timezone_id")
        summary["resolved_offset_minutes"] = rt.get("timezone_offset_minutes")
        summary["is_dst"] = rt.get("is_dst")
        summary["ambiguous_local_time"] = rt.get("ambiguous_local_time")

    para = report["sections"].get("parashara")
    if para:
        summary["parashara_rules"] = [
            {
                "rule_id": r["rule_id"],
                "name": r["name"],
                "outcome": r["outcome"],
                "version": r["version"],
                "activation_active": r.get("activation", {}).get("active"),
                "source_ids": r.get("source_ids"),
            }
            for r in para.get("results", [])
        ]

    av = report["sections"].get("ashtakavarga")
    if av:
        summary["sav_total_bindus"] = av.get("sarvashtakavarga", {}).get("total_bindus")
        sh = av.get("sarvashtakavarga", {}).get("shodhana") or {}
        if sh:
            summary["sav_reduced_total"] = sh.get("reduced_total")
            summary["sav_sodhya_pinda"] = (sh.get("sodhya_pinda") or {}).get("sodhya_pinda")
            summary["ashtakavarga_shodhana_variant"] = sh.get("variant")
        sun_sh = (av.get("bhinnashtakavarga_shodhana") or {}).get("Sun") or {}
        if sun_sh.get("sodhya_pinda"):
            summary["sun_sodhya_pinda"] = sun_sh["sodhya_pinda"].get("sodhya_pinda")
        pr = av.get("prastara") or {}
        if pr:
            sun_p = (pr.get("by_planet") or {}).get("Sun") or {}
            summary["prastara_sun_ok"] = sun_p.get("reconstruction_ok")
            sun_score = (av.get("natal_sign_scores") or {}).get("Sun") or {}
            if "kakshya_lord_bindu" in sun_score:
                summary["sun_kakshya_lord_bindu"] = sun_score["kakshya_lord_bindu"]

    kp = report["sections"].get("kp")
    if kp:
        summary["kp_config_isolation"] = kp.get("config_isolation", {}).get("outcome")
        sun = kp.get("planet_lord_chains", {}).get("Sun", {})
        summary["kp_sun_lords"] = {
            "star": sun.get("star_lord"),
            "sub": sun.get("sub_lord"),
            "sub_sub": sun.get("sub_sub_lord"),
        }

    jaimini = report["sections"].get("jaimini")
    if jaimini:
        ak = jaimini.get("chara_karakas", {}).get("atmakaraka", {})
        a1 = jaimini.get("arudha", {}).get("arudha_lagna", {})
        summary["jaimini_engine"] = jaimini.get("engine")
        summary["jaimini_chara_scheme"] = jaimini.get("config", {}).get(
            "jaimini.chara_karaka.scheme"
        )
        summary["jaimini_atmakaraka"] = ak.get("planet")
        summary["jaimini_arudha_lagna"] = a1.get("arudha_sign")
        summary["jaimini_karakamsa"] = (
            jaimini.get("karakamsa_swamsa", {}).get("karakamsa", {}).get("sign")
        )

    nadi = report["sections"].get("nadi")
    if nadi:
        summary["nadi_engine"] = nadi.get("engine")
        summary["nadi_corpus_status"] = (nadi.get("corpus_gate") or {}).get("corpus_status")
        summary["nadi_planet_in_star_count"] = len(nadi.get("planet_in_star") or [])
        summary["nadi_chains_blocked"] = nadi.get("chain_error") is not None

    pan = report["sections"].get("panchanga")
    if pan:
        p = pan.get("panchanga") or {}
        summary["panchanga_engine"] = pan.get("engine")
        summary["panchanga_tithi"] = (p.get("tithi") or {}).get("label")
        summary["panchanga_vara"] = (p.get("vara") or {}).get("name")
        summary["panchanga_nakshatra"] = (p.get("nakshatra") or {}).get("label")
        summary["panchanga_yoga"] = (p.get("yoga") or {}).get("name")
        summary["panchanga_karana"] = (p.get("karana") or {}).get("name")
        muh = pan.get("muhurta") or {}
        active = muh.get("active") or {}
        summary["muhurta_rahu_kala_active"] = active.get("rahu_kala")
        summary["muhurta_hora_lord"] = (active.get("hora") or {}).get("lord")
        summary["muhurta_chaughadiya"] = (active.get("chaughadiya") or {}).get("label")
        bala = pan.get("bala") or {}
        moon_tara = (bala.get("tara_from_moon") or {}).get("Moon") or {}
        summary["bala_moon_tara"] = moon_tara.get("tara")
        summary["bala_moon_from_lagna"] = (
            (bala.get("chandra_bala") or {}).get("moon_from_lagna") or {}
        ).get("bala")

    mev = report["sections"].get("muhurta_events")
    if mev:
        summary["muhurta_events_engine"] = mev.get("engine")
        pack = mev.get("event_pack") or {}
        summary["muhurta_events_good"] = (pack.get("summary") or {}).get("good")
        summary["muhurta_events_mixed"] = (pack.get("summary") or {}).get("mixed")
        summary["muhurta_events_avoid"] = (pack.get("summary") or {}).get("avoid")
        summary["muhurta_events_count"] = len(pack.get("results") or [])

    tajika = report["sections"].get("tajika")
    if tajika:
        summary["tajika_engine"] = tajika.get("engine")
        summary["tajika_target_year"] = tajika.get("target_year")
        summary["tajika_muntha_sign"] = (tajika.get("muntha") or {}).get("sign")
        summary["tajika_year_lord_candidate"] = (tajika.get("muntha") or {}).get(
            "year_lord_candidate"
        )
        summary["tajika_location_rule"] = (tajika.get("annual_location") or {}).get(
            "location_rule"
        )
        summary["tajika_sun_error_deg"] = (tajika.get("solar_return") or {}).get(
            "sun_longitude_error_deg"
        )
        tp = tajika.get("tithi_pravesh") or {}
        summary["tajika_tithi_pravesh_label"] = (tp.get("tithi") or {}).get("label")
        summary["tajika_tithi_pravesh_error_deg"] = tp.get("elongation_error_deg")
        summary["tajika_saham_count"] = len((tajika.get("sahams") or {}).get("sahams") or [])
        summary["tajika_aspect_count"] = len(
            (tajika.get("tajika_aspects") or {}).get("aspects") or []
        )
        summary["tajika_ithasala_count"] = len(
            (tajika.get("tajika_aspects") or {}).get("ithasala_candidates") or []
        )

    sud = report["sections"].get("sudarshana")
    if sud:
        summary["sudarshana_engine"] = sud.get("engine")
        refs = (sud.get("sudarshana") or {}).get("references") or {}
        summary["sudarshana_lagna"] = (refs.get("lagna") or {}).get("sign")
        summary["sudarshana_chandra"] = (refs.get("chandra") or {}).get("sign")
        summary["sudarshana_surya"] = (refs.get("surya") or {}).get("sign")
        summary["sudarshana_planet_count"] = len((sud.get("sudarshana") or {}).get("planets") or [])

    bb = report["sections"].get("bhrigu_bindu")
    if bb:
        summary["bhrigu_bindu_engine"] = bb.get("engine")
        bindu = bb.get("bhrigu_bindu") or {}
        summary["bhrigu_bindu_sign"] = bindu.get("sign")
        summary["bhrigu_bindu_longitude"] = bindu.get("longitude_sidereal_deg")
        summary["bhrigu_bindu_nakshatra"] = bindu.get("nakshatra_label")
        summary["bhrigu_bindu_house"] = bindu.get("house_from_lagna")
        summary["bhrigu_bindu_natal_hit_count"] = len(bindu.get("natal_conjunctions") or [])

    nc = report["sections"].get("nakshatra_chakra")
    if nc:
        summary["nakshatra_chakra_engine"] = nc.get("engine")
        tara = nc.get("tara_chakra") or {}
        kota = nc.get("kota_chakra") or {}
        sbc = nc.get("sarvatobhadra") or {}
        summary["tara_chakra_spoke_count"] = len(tara.get("spokes") or [])
        summary["kota_chakra_slot_count"] = len(kota.get("slots") or [])
        summary["sarvatobhadra_rim_count"] = len(sbc.get("rim") or [])
        summary["sarvatobhadra_vedha_status"] = (sbc.get("vedha") or {}).get("status")
        moon_tara = next(
            (p for p in (tara.get("planets") or []) if p.get("planet") == "Moon"),
            None,
        )
        summary["tara_chakra_moon_tara"] = (moon_tara or {}).get("tara")

    clas = report["sections"].get("classification")
    if clas:
        summary["classification_engine"] = clas.get("engine")
        summary["gandanta_hit_count"] = len(clas.get("gandanta_hits") or [])
        moon = clas.get("moon") or {}
        summary["chandra_kriya"] = (moon.get("chandra_kriya") or {}).get("name")
        summary["chandra_kriya_index"] = (moon.get("chandra_kriya") or {}).get("index")
        summary["chandra_vela_index"] = (moon.get("chandra_vela") or {}).get("index")
        summary["moon_baladi_avastha"] = (moon.get("baladi_avastha") or {}).get("avastha")
        summary["lagna_gandanta"] = ((clas.get("lagna") or {}).get("gandanta") or {}).get(
            "active"
        )

    prashna = report["sections"].get("prashna")
    if prashna:
        summary["prashna_engine"] = prashna.get("engine")
        summary["prashna_lagna_sign"] = (prashna.get("prashna_lagna") or {}).get("sign")
        tri = (prashna.get("sphutas") or {}).get("trisphuta") or {}
        summary["prashna_trisphuta_sign"] = tri.get("sign")
        chat = (prashna.get("sphutas") or {}).get("chatusphuta") or {}
        summary["prashna_chatusphuta_sign"] = chat.get("sign")
        ash = (prashna.get("manual_inputs") or {}).get("ashtamangala") or {}
        summary["ashtamangala_status"] = ash.get("status")
        summary["ashtamangala_provided"] = ash.get("provided")
        arudha = prashna.get("arudha_lagna") or {}
        summary["prashna_arudha_sign"] = arudha.get("arudha_sign")

    compat = report["sections"].get("compatibility")
    if compat:
        summary["compatibility_engine"] = compat.get("engine")
        ak = compat.get("ashtakoota") or {}
        summary["ashtakoota_total"] = ak.get("total")
        summary["ashtakoota_max"] = ak.get("max_total")
        summary["ashtakoota_percentage"] = ak.get("percentage")
        summary["ashtakoota_boy_nakshatra"] = (ak.get("boy") or {}).get("nakshatra_label")
        summary["ashtakoota_girl_nakshatra"] = (ak.get("girl") or {}).get("nakshatra_label")
    return summary
