#!/usr/bin/env python3
"""Audit canonical jewTeX XML without rewriting source texts.

Audit findings are observations, not claims that the Russian translation is wrong.
Only XML parser errors, duplicate xml:id and invalid new transmission chains fail CI.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
import re
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
REVIEW = {"pending", "proposed", "verified", "disputed", "not_applicable"}
BLOCK = {"pending", "partial", "verified", "disputed"}
NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*$")

def validate_transmission(node, known_ids: set[str], label: str) -> list[str]:
    errors = []
    children = list(node)
    relays = [x for x in children if x.tag == "relay"]
    attributions = [x for x in children if x.tag == "attributed_to"]
    if not relays or len(attributions) != 1 or children != relays + attributions:
        errors.append(f"{label}: transmission must contain one or more relay, then exactly one attributed_to")
        return errors
    statement = node.get("statement", "")
    if statement.startswith("#") and statement[1:] not in known_ids:
        errors.append(f"{label}: transmission statement {statement!r} has no matching xml:id")
    if node.get("human_review") not in BLOCK:
        errors.append(f"{label}: invalid human_review status")
    for i, relay in enumerate(relays):
        if not relay.get("from") or not relay.get("to"):
            errors.append(f"{label}: relay[{i}] must have from and to")
        if relay.get("review") not in REVIEW:
            errors.append(f"{label}: relay[{i}] missing/invalid review")
        if i and relays[i-1].get("to") != relay.get("from"):
            errors.append(f"{label}: relay[{i}] does not continue preceding chain")
    end = attributions[0]
    if relays[-1].get("to") != end.get("person"):
        errors.append(f"{label}: last relay.to differs from attributed_to.person")
    if end.get("review") not in REVIEW:
        errors.append(f"{label}: attributed_to missing/invalid review")
    if node.get("human_review") == "verified":
        if any(x.get("review") != "verified" for x in relays + [end]):
            errors.append(f"{label}: aggregate verified while one or more chain links are unverified")
        if not node.get("reviewed_by") or not node.get("reviewed_at"):
            errors.append(f"{label}: verified transmission has no reviewed_by/reviewed_at")
    for i, item in enumerate(relays + [end]):
        if item.get("review") == "verified" and not item.get("reviewed_by"):
            errors.append(f"{label}: reviewed link[{i}] missing reviewed_by")
    return errors

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", required=True)
    ap.add_argument("--summary")
    ap.add_argument("--known-tags")
    ap.add_argument("--emit-inventory", action="store_true")
    args = ap.parse_args()
    paths = [Path(p.decode("utf8")) for p in subprocess.check_output(
        ["git", "ls-files", "-z", "--", "*.xml"]).split(b"\0") if p]
    tags = Counter()
    attributes = defaultdict(Counter)
    roots = Counter()
    issues = defaultdict(list)
    counts = Counter()
    hard_errors = []
    examples_limit = 14
    def warn(kind, location):
        counts[kind] += 1
        if len(issues[kind]) < examples_limit:
            issues[kind].append(location)
    for path in paths:
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as err:
            hard_errors.append(f"{path}: {err}")
            continue
        roots[root.tag] += 1
        xml_ids = set()
        for el in root.iter():
            tag = el.tag
            tags[tag] += 1
            for k in el.attrib:
                attributes[tag][k] += 1
            idvalue = el.get(XML_ID)
            if idvalue:
                if idvalue in xml_ids:
                    hard_errors.append(f"{path}: duplicate xml:id {idvalue!r}")
                xml_ids.add(idvalue)
                if not NAME.match(idvalue):
                    warn("xml_id_nonportable", f"{path}: {idvalue}")
            if el.tag == "p-ai":
                counts["unverified_ai_paragraphs"] += 1
            if el.tag in ("makshan", "tarzan"):
                counts["argument_role_tags"] += 1
            if el.tag == "work_needed":
                counts["work_needed_marks"] += 1
            if el.tag == "link_needed":
                warn("unresolved_internal_links", str(path))
            if el.tag == "p" and not "".join(el.itertext()).strip() and len(el) == 0:
                warn("empty_p_placeholders", str(path))
            if el.tag == "header" and not el.get("name"):
                warn("header_without_name", str(path))
            if el.tag == "header":
                for suspicious in ("text_lik", "vebouse_name"):
                    if suspicious in el.attrib:
                        warn("possible_misspelled_header_attribute", f"{path}: {suspicious}")
            if root.tag != "info" and el.tag == "quote" and (not el.get("author") or not el.get("book")):
                warn("quote_missing_target_fields", str(path))
            if el.tag == "p" and "от имени" in "".join(el.itertext()) and "speaker" not in el.attrib:
                warn("candidate_reported_speech_for_annotation", str(path))
        # Repeating a named header under the SAME XML parent can break addressing.
        # A provisional editorial warning, not an automatic structural failure.
        for parent in root.iter():
            siblings = [child for child in parent if child.tag == "header" and child.get("name")]
            keyed = Counter((ch.get("type"), ch.get("name")) for ch in siblings)
            for (heading_type, name), freq in keyed.items():
                if freq > 1:
                    warn("duplicate_sibling_header_address", f"{path}: {heading_type}={name!r} ({freq} siblings)")
        # idx is a Sefaria display aid, NOT globally unique. Count only as diagnostic.
        for daf in root.iter("daf"):
            vals = [e.get("idx") for e in daf.iter() if e.get("idx")]
            duplicate = sorted(x for x, n in Counter(vals).items() if n > 1)
            if duplicate:
                warn("reused_idx_on_a_daf_not_a_unique_id", f"{path} daf={daf.get('name')}: {', '.join(duplicate[:6])}")
        for transmission in root.iter("transmission"):
            counts["transmission_chains"] += 1
            hard_errors.extend(validate_transmission(transmission, xml_ids, str(path)))
    if args.known_tags:
        p = Path(args.known_tags)
        if p.exists():
            baseline = json.loads(p.read_text(encoding="utf8"))
            allowed = set(baseline["elements"])
            for t in sorted(set(tags) - allowed):
                hard_errors.append(f"New XML element {t!r} not registered in {p}; review schema and inventory")
            known_attributes = baseline.get("attributes_by_element", {})
            for t, usage in attributes.items():
                permitted = set(known_attributes.get(t, []))
                for attribute in sorted(set(usage) - permitted):
                    hard_errors.append(f"New XML attribute {t}@{attribute} not registered in {p}; review schema and inventory")
        else:
            warn("inventory_missing", str(p))
    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "files_scanned": len(paths),
        "roots": dict(roots.most_common()),
        "element_counts": dict(tags.most_common()),
        "attributes_by_element": {k: dict(v.most_common()) for k, v in sorted(attributes.items())},
        "finding_counts": dict(counts.most_common()),
        "examples": dict(issues),
        "validation_errors": hard_errors[:100],
    }
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf8")
    if args.emit_inventory:
        print("ELEMENT_INVENTORY_JSON=" + json.dumps({"elements": sorted(tags)}, ensure_ascii=False))
    top = sorted(counts.items(), key=lambda kv: -kv[1])[:12]
    print(f"XML audit: {len(paths)} files; {len(tags)} element names; {len(hard_errors)} strict errors")
    for category, n in top:
        print(f"  {category}: {n}; examples: {issues.get(category, [])[:3]}")
    if args.summary:
        with open(args.summary, "a", encoding="utf8") as f:
            f.write("\n## jewTeX XML audit\n\n")
            f.write(f"- XML files: **{len(paths)}**, distinct element names: **{len(tags)}**, strict errors: **{len(hard_errors)}**.\n")
            f.write("- Findings below are editorial candidates, **not** automatic errors or proof of unverified content.\n\n")
            f.write("| Category | Count |\n|---|---:|\n")
            for category, n in top:
                f.write(f"| {category} | {n} |\n")
    for err in hard_errors[:30]:
        print("ERROR: " + err, file=sys.stderr)
    return 1 if hard_errors else 0

if __name__ == "__main__":
    sys.exit(main())
