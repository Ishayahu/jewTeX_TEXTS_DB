#!/usr/bin/env python3
"""Normalize a Sefaria harvest into the committed Antoninus registry."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import quote


HEBREW_VARIANTS = {
    "אנטונינוס",
    "אנטונוס",
    "אנטולינוס",
    "אנטלימוס",
    "אנטוניוס",
    "אנטונין",
    "אנטולימוס",
    "אנטינוס",
    "אנטינינוס",
    "אנטונינס",
    "אנטנינוס",
    "אנטוניניס",
    "אנטינינס",
    "אנטולינס",
}
LATIN_VARIANTS = {"antoninus", "antoninos", "antonios", "antolinus"}
TAG_RE = re.compile(r"<[^>]+>")
TECHNICAL_FALSE_POSITIVE_REFS = {
    "Mekhilta DeRabbi Shimon Ben Yochai 14:7",
    "Mekhilta DeRabbi Shimon Ben Yochai 15:1",
    "Introductions to Tanaitic Literature, Introduction to Halakhic Midrashim, Mekhilta of Rashbi 20",
}

EPISODE_RULES = [
    (("Avodah Zarah 10a:", "Bereshit Rabbah 67:6"), "royal_succession_and_tiberias", "Совет о наследовании престола и освобождении Тверии; сокровищницы и смена чиновников."),
    (("Avodah Zarah 10b:",), "secret_visits_and_service", "Цикл о тайных посещениях Раби, дарах, слугах, дочери Гире и смерти Антонинуса."),
    (("Avodah Zarah 11a:", "Berakhot 57b:"), "two_great_persons_and_table", "Антонинус и Раби как две знатные личности; богатый стол и редька."),
    (("Sanhedrin 91a:17", "Mekhilta DeRabbi Yishmael, Tractate Shirah 2:25"), "body_soul_judgment", "Тело и душа на суде; притча о хромом и слепом сторожах."),
    (("Sanhedrin 91b:4",), "sun_sets_in_west", "Почему солнце восходит на востоке и заходит на западе."),
    (("Sanhedrin 91b:5", "Bereshit Rabbah 34:10"), "soul_enters_embryo", "Когда душа входит в человека: при зачатии или при формировании."),
    (("Sanhedrin 91b:6", "Bereshit Rabbah 34:10"), "evil_inclination", "Когда дурное начало начинает властвовать над человеком."),
    (("Sanhedrin 91b:7", "Mekhilta DeRabbi Yishmael, Tractate Shirah 6:15"), "egyptian_ruler", "Вопрос о походе в Александрию и возможности появления правителя Египта."),
    (("Jerusalem Talmud Megillah 1:11:4",), "conversion_altar_and_leviathan", "Жертвенник, воскурение, гиюр, Левиафан и обрезание Антонинуса."),
    (("Jerusalem Talmud Megillah 3:2:4",), "synagogue_lamp", "Светильник Антонинуса для синагоги и вопрос, прошёл ли он гиюр."),
    (("Jerusalem Talmud Megillah 3:2:5", "Jerusalem Talmud Sanhedrin 10:5:3"), "conversion_and_circumcision", "Спор о гиюре, Йом-Кипур, Левиафан, обрезание и прозвище Раби."),
    (("Bereshit Rabbah 11:4", "Esther Rabbah 1:16"), "sabbath_meal_spice", "Трапезы Раби и Антонинуса и особая «приправа» Шаббата."),
    (("Bereshit Rabbah 75:5", "Midrash Tanchuma Buber, Vayishlach 5:1", "Mishnat Rabbi Eliezer 10:6"), "rabbi_letter_as_servant", "Письмо Раби Антонинусу с формулой «твой слуга Йеуда»."),
    (("Bereshit Rabbah 84:3",), "job_reward_and_punishment", "Беседа о словах Иова, наказании и вознаграждении."),
    (("Vayikra Rabbah 10:4",), "disciple_revives_servant", "Ученик Раби оживляет слугу Антонинуса."),
    (("Vayikra Rabbah 16:8",), "prayer_heat_and_cold", "Просьба Антонинуса молиться против холода и жары."),
    (("Vayikra Rabbah 3:2",), "righteous_proselytes", "Антонинус во главе праведных прозелитов в будущем."),
    (("Midrash Tanchuma, Miketz 9:2", "Midrash Tanchuma Buber, Miketz 11:1"), "frequency_of_prayer", "Сколько раз в день следует молиться; пример обращений ко двору Антонинуса."),
    (("Midrash Tanchuma, Vayeshev 3:2",), "caesarea_legionaries", "Приглашение Раби в Кесарию и столкновение с римскими легионерами."),
    (("Mekhilta DeRabbi Yishmael, Tractate Vayehi Beshalach 1:26",), "lamp_for_sons", "Антонинус сам освещает дорогу сыновьям как знак любви к ним."),
    (("Mekhilta DeRabbi Yishmael, Tractate Vayehi Beshalach 2:30",), "third_charioteer", "Антонинус добавил третьего воина на колесницу."),
    (("Pesachim 119a:11", "Sanhedrin 110a:12"), "joseph_treasure", "Одна из сокровищниц Йосефа открылась Антонинусу, сыну Асвейруса."),
    (("Niddah 45a:9",), "justina_marriage_age", "Юстина, дочь Асвейруса, сына Антонинуса, спрашивает о брачном возрасте."),
    (("Kohelet Rabbah 10:5:1", "Kohelet Rabbah 9:10:2"), "antoninus_younger_and_death", "Антонинус-младший, смерть Раби и вопрос об обрезании."),
    (("Jerusalem Talmud Niddah 1:3:8", "Jerusalem Talmud Yevamot 4:11:5"), "cattle_of_antoninus", "Стадо Антонинуса и определение срока беременности животных."),
    (("Jerusalem Talmud Sanhedrin 1:4:8",), "antoninus_and_levite_count", "Вопрос правителя Антонинуса о расхождении числа левитов и итоговой суммы."),
]

TRANSLATED_RULES = [
    (("Jerusalem Talmud Megillah 3:2:4", "Jerusalem Talmud Megillah 3:2:5"), ["jerusalem_talmud/megillah/ch03.xml"]),
    (("Tosafot on Avodah Zarah 10b:5:1", "Tosafot on Avodah Zarah 10b:14:1"), ["tosafot/tosafot_al_avodah_zarah/10.xml"]),
    (("Seder HaDorot, Almanac 3900:1",), ["heilprin_yechiel/seder_hadorot/01.xml"]),
    (("Seder HaDorot, Tanaim and Amoraim 1652:7",), ["heilprin_yechiel/seder_hadorot/02.xml"]),
]


def plain(value: str) -> str:
    value = html.unescape(TAG_RE.sub("", value or ""))
    return " ".join(value.split())


def unpoint(value: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFD", value) if unicodedata.category(ch) != "Mn")


def variants_in(text: str) -> list[str]:
    normalized = unpoint(plain(text)).lower()
    variants = {variant for variant in HEBREW_VARIANTS if variant in normalized}
    variants.update(variant for variant in LATIN_VARIANTS if re.search(rf"\b{re.escape(variant)}\b", normalized))
    return sorted(variants)


PRIMARY_PREFIXES = (
    "Mishnah ",
    "Tosefta ",
    "Jerusalem Talmud ",
    "Berakhot ",
    "Pesachim ",
    "Avodah Zarah ",
    "Niddah ",
    "Sanhedrin ",
    "Bereshit Rabbah ",
    "Vayikra Rabbah ",
    "Esther Rabbah ",
    "Kohelet Rabbah ",
    "Midrash Tanchuma, ",
    "Midrash Tanchuma Buber, ",
    "Mekhilta DeRabbi ",
    "Mishnat Rabbi Eliezer ",
    "Pesikta Rabbati ",
    "Midrash Tehillim ",
    "Zohar ",
)
PARALLEL_PREFIXES = (
    "Yalkut Shimoni ",
    "Ein Yaakov",
    "Midrash Aggadah, ",
    "Midrash Lekach Tov, ",
    "Midrash Yelamdenu, ",
    "Otzar Midrashim, ",
    "Bereshit Rabbati, ",
)


def source_class(ref: str, categories: list[str], path: str) -> str:
    if "Commentary" in categories or "/Commentary/" in path:
        return "commentary"
    if ref.startswith(PRIMARY_PREFIXES):
        return "primary_source"
    if ref.startswith(PARALLEL_PREFIXES):
        return "parallel_recension"
    return "later_citation"


GENERIC_SUMMARIES = {
    "commentary": "Комментарий, в котором обсуждается или цитируется материал об Антонинусе; конкретное содержание сохранено в проверенном фрагменте.",
    "parallel_recension": "Параллельная, компилятивная или переизданная передача материала об Антонинусе; точная зависимость от более раннего текста требует отдельной текстологической сверки.",
    "later_citation": "Позднее цитирование, историческое, галахическое или справочное упоминание Антонинуса; конкретное содержание сохранено в проверенном фрагменте.",
    "primary_source": "Прямое упоминание Антонинуса в источнике; конкретное содержание сохранено в проверенном фрагменте.",
}


def stable_id(ref: str) -> str:
    digest = hashlib.sha1(ref.encode("utf-8")).hexdigest()[:12]
    return f"ant-sf-{digest}"


def sefaria_url(ref: str) -> str:
    return "https://www.sefaria.org/" + quote(ref.replace(" ", "_"), safe="/:,._-")


def editorial_metadata(ref: str) -> tuple[str | None, str | None]:
    for prefixes, group, summary in EPISODE_RULES:
        if any(ref.startswith(prefix) for prefix in prefixes):
            return group, summary
    return None, None


def database_metadata(ref: str) -> tuple[str, list[str]]:
    for prefixes, targets in TRANSLATED_RULES:
        if any(ref.startswith(prefix) for prefix in prefixes):
            return "translated", targets
    return "not_translated_or_not_present", []


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("raw", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    raw = json.loads(args.raw.read_text(encoding="utf-8"))

    grouped: dict[str, list[dict]] = defaultdict(list)
    for hit in raw["hits"]:
        ref = hit.get("source", {}).get("ref")
        if ref:
            grouped[ref].append(hit)

    records = []
    false_positives = []
    for ref, hits in grouped.items():
        source = hits[0]["source"]
        candidate_texts = []
        for hit in hits:
            hit_source = hit["source"]
            candidate_texts.extend(
                str(hit_source.get(field, "")) for field in ("exact", "naive_lemmatizer")
            )
            for snippets in hit.get("highlight", {}).values():
                candidate_texts.extend(snippets)
        matched_variants = sorted({variant for text in candidate_texts for variant in variants_in(text)})
        if not matched_variants or ref in TECHNICAL_FALSE_POSITIVE_REFS:
            false_positives.append(
                {
                    "ref": ref,
                    "matches": sorted(
                        {(m["query"], m["field"]) for hit in hits for m in hit.get("matches", [])}
                    ),
                    "reason": (
                        "Technical manuscript/shelfmark occurrence, not a person."
                        if ref in TECHNICAL_FALSE_POSITIVE_REFS
                        else "No accepted Antoninus spelling occurs in the indexed segment."
                    ),
                }
            )
            continue

        categories = source.get("categories") or []
        path = source.get("path") or ""
        book = (source.get("titleVariants") or [path.rsplit("/", 1)[-1] or ref])[0]
        versions = sorted(
            {
                (hit["source"].get("lang") or "", hit["source"].get("version") or "")
                for hit in hits
            }
        )
        full_texts = [plain(hit["source"].get("exact", "")) for hit in hits]
        full_texts = [text for text in full_texts if text]
        excerpt = max(full_texts, key=len, default="")[:700]
        parallel_group, episode_summary = editorial_metadata(ref)
        database_status, database_targets = database_metadata(ref)
        attribution_status = "uncertain" if ref.startswith(("Mishnah Challah 4:11", "Jerusalem Talmud Sanhedrin 1:2:47", "Jerusalem Talmud Sanhedrin 1:4:8")) else "not_assessed"
        classification = source_class(ref, categories, path)
        records.append(
            {
                "id": stable_id(ref),
                "book": book,
                "ref": ref,
                "he_ref": source.get("heRef"),
                "url": sefaria_url(ref),
                "path": path,
                "categories": categories,
                "composition_date": source.get("comp_date"),
                "classification": classification,
                "parallel_group": parallel_group,
                "episode_summary_ru": episode_summary or GENERIC_SUMMARIES[classification],
                "attribution_status": attribution_status,
                "matched_variants": matched_variants,
                "verified": True,
                "verification_basis": "Full indexed segment returned by Sefaria Search API v2",
                "verified_text_excerpt": excerpt,
                "sefaria_versions": [
                    {"language": language, "version_title": title} for language, title in versions
                ],
                "database_status": database_status,
                "database_targets": database_targets,
            }
        )

    records.sort(key=lambda item: (item["composition_date"] is None, item["composition_date"] or 0, item["book"], item["ref"]))
    class_counts = Counter(record["classification"] for record in records)
    work_counts = Counter(record["book"] for record in records)
    output = {
        "schema_version": 1,
        "scope": "Sefaria text-index mentions of accepted Antoninus name variants; user sheets excluded",
        "generated_from": {
            "endpoint": raw["search_url"],
            "query_count": len(raw["queries"]),
            "field_count": len(raw["fields"]),
            "request_count": len(raw["request_log"]),
            "queries": raw["queries"],
            "fields": raw["fields"],
            "request_log": raw["request_log"],
            "raw_versioned_hit_count": raw["raw_hit_count_after_id_deduplication"],
        },
        "summary": {
            "verified_unique_fragments": len(records),
            "unique_works": len(work_counts),
            "classifications": dict(sorted(class_counts.items())),
            "excluded_false_positive_refs": len(false_positives),
        },
        "records": records,
        "excluded_false_positives": false_positives,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
