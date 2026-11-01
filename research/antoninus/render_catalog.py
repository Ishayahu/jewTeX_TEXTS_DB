#!/usr/bin/env python3
"""Render the Antoninus bibliography, grouped by book in approximate chronology.

Only research/antoninus/registry.json is authoritative input. No source text is
duplicated and no historic identification of Antoninus is inferred.
"""

import argparse
import json
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

SOURCE = Path("research/antoninus/registry.json")
DEST = Path("lastov_ishayahu/chronos/9001.xml")
BASE = "https://github.com/Ishayahu/jewTeX_TEXTS_DB"
CLASS_NAMES = {
    "primary_source": "ранний текст",
    "parallel_recension": "параллель или компиляция",
    "commentary": "комментарий",
    "later_citation": "позднее цитирование",
}


def year_value(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)) and -10000 <= value <= 2500:
        return round(value)
    if isinstance(value, str) and re.fullmatch(r"-?\d{1,4}", value):
        n = int(value)
        return n if -10000 <= n <= 2500 else None
    return None


def period(year):
    if year is None:
        return (9, "Не датированные в реестре произведения")
    if year < 1:
        return (0, "Произведения, датированные до нашей эры")
    if year < 200:
        return (1, "I–II века")
    if year < 400:
        return (2, "III–IV века")
    if year < 600:
        return (3, "V–VI века")
    if year < 1000:
        return (4, "VII–X века")
    if year < 1300:
        return (5, "XI–XIII века")
    if year < 1600:
        return (6, "XIV–XVI века")
    if year < 1800:
        return (7, "XVII–XVIII века")
    return (8, "XIX–XXI века")


def numeric_ref(value):
    return tuple((0, int(t)) if t.isdecimal() else (1, t.casefold())
                 for t in re.split(r"(\d+)", value))


def work_year(rows):
    years = [n for r in rows if (n := year_value(r.get("composition_date"))) is not None]
    return int(statistics.median(years)) if years else None


def render(data):
    records = data["records"]
    groups = defaultdict(list)
    seen_refs, seen_ids = set(), set()
    for r in records:
        if not all(r.get(k) for k in ("id", "ref", "book", "url")):
            raise ValueError("Record missing stable identity or source URL")
        if r["id"] in seen_ids or r["ref"] in seen_refs:
            raise ValueError("Duplicate ID/ref: " + r["ref"])
        if not r["url"].startswith("https://www.sefaria.org/"):
            raise ValueError("Unexpected external host: " + r["url"])
        seen_ids.add(r["id"])
        seen_refs.add(r["ref"])
        groups[r["book"]].append(r)

    stats = data["summary"]
    if len(records) != stats["verified_unique_fragments"] or len(groups) != stats["unique_works"]:
        raise ValueError("Registry totals do not match source records")

    works = [(work_year(rows), book, sorted(rows, key=lambda r: numeric_ref(r["ref"])))
             for book, rows in groups.items()]
    works.sort(key=lambda item: (period(item[0])[0],
                                 item[0] if item[0] is not None else 99999,
                                 item[1].casefold()))
    by_period = Counter(period(y)[0] for y, _, _ in works)
    refs_by_period = Counter()
    for y, _, rows in works:
        refs_by_period[period(y)[0]] += len(rows)
    class_counts = Counter(r.get("classification") for r in records)

    rows = [
        '<?xml version="1.0" standalone="yes"?>',
        '<content>',
        '  <header level="0" type="chapter" name="9001" verbouse_name="Приложение. Антонинус — каталог по книгам">',
        '    <header level="2" type="seif" name="Антонинус — каталог по книгам">',
        '      <p><strong>Антонинус: полный каталог ссылок по книгам.</strong> '
        'Записи сгруппированы по произведениям, книги упорядочены приблизительно по времени составления, '
        'внутри книги ссылки — в порядке адресов. Открываются оригинальные места Sefaria, в новой вкладке.</p>',
        '      <p>Даты относятся к <strong>созданию произведений</strong>, а не к историческим событиям. '
        'Основа сортировки — поле composition_date в реестре Sefaria; дата книги — медиана значений '
        'этого поля. Датировки условны, а при отсутствии метаданных книги помещены в конец. '
        'Имя Антонинус не означает, что все тексты говорят об одном императоре. '
        'Поздние комментарии и параллельные редакции могут повторять более древний источник.</p>',
        f'      <p><strong>Всего {len(records)} ссылок из {len(groups)} книг.</strong> '
        f'Ранних текстов: {class_counts["primary_source"]}; параллелей и компиляций: '
        f'{class_counts["parallel_recension"]}; комментариев: {class_counts["commentary"]}; '
        f'поздних упоминаний: {class_counts["later_citation"]}. '
        f'<a href="{BASE}/blob/master/research/antoninus/registry.json" target="_blank">Полный реестр JSON</a>. '
        f'<a href="{BASE}/issues/12" target="_blank">Рабочая задача №12</a>. '
        '<a href="https://jewtex.ru/open/lastov_ishayahu/chronos/chapter=9000/" '
        'target="_blank">Подборка с переведёнными текстами</a>.</p>',
    ]
    previous_group = None
    for year, book, passages in works:
        grp, label = period(year)
        if previous_group != grp:
            rows.append(f'      <p><strong>{escape(label)}: книг {by_period[grp]}, '
                        f'ссылок {refs_by_period[grp]}</strong></p>')
            previous_group = grp
        when = ("год не установлен" if year is None else
                f"около {abs(year)} г. до н. э." if year < 0 else f"около {year} г. н. э.")
        rows.append(f'      <p><strong>{escape(book)}</strong> — '
                    f'ссылок: {len(passages)}; {escape(when)}</p>')
        for item in passages:
            klass = CLASS_NAMES.get(item.get("classification"), "классификация не установлена")
            status = ("переведён" if item.get("database_status") == "translated"
                      else "перевод не отмечен")
            hint = klass + "; " + status + "; " + str(item.get("episode_summary_ru") or "")
            rows.append(f'      <p><a href={quoteattr(item["url"])} '
                        f'target="_blank" rel="noopener noreferrer" title={quoteattr(hint)}>'
                        f'{escape(item["ref"])}</a> '
                        f'({escape(klass)}; {escape(status)})</p>')
    rows.extend(["    </header>", "  </header>", "</content>"])
    return "\n".join(rows) + "\n"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--registry", type=Path, default=SOURCE)
    p.add_argument("--output", type=Path, default=DEST)
    args = p.parse_args()
    data = json.loads(args.registry.read_text(encoding="utf-8"))
    result = render(data)
    from lxml import etree
    etree.fromstring(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result, encoding="utf-8")
    print(f"Rendered {len(data['records'])} refs from {data['summary']['unique_works']} books")


if __name__ == "__main__":
    main()
