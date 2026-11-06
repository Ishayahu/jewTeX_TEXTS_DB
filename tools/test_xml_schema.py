#!/usr/bin/env python3
"""Regression examples for schema and transmission-chain semantics."""
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from xml_audit import validate_transmission

SCHEMA = Path("schema/jewtex.rng")
HEAD = '<content><p xml:id="utt1">текст</p><semantic_data version="1">'
TAIL = "</semantic_data></content>"
valid = HEAD + (
    '<transmission statement="#utt1" human_review="pending">'
    '<relay from="amoraim/a" to="amoraim/b" relation="reports_in_name_of" review="pending" evidence="אמר"/>'
    '<relay from="amoraim/b" to="amoraim/c" relation="reports_in_name_of" review="pending" evidence="בשם"/>'
    '<attributed_to person="amoraim/c" status="reported" review="pending"/>'
    '</transmission>'
) + TAIL
bad_shape = HEAD + (
    '<transmission statement="#utt1" human_review="pending">'
    '<relay from="a" to="b" relation="reports_in_name_of" review="pending"/>'
    '</transmission>'
) + TAIL
bad_continuity = HEAD + (
    '<transmission statement="#utt1" human_review="verified">'
    '<relay from="a" to="b" relation="reports_in_name_of" review="pending"/>'
    '<relay from="different" to="c" relation="reports_in_name_of" review="pending"/>'
    '<attributed_to person="wrong" status="reported" review="pending"/>'
    '</transmission>'
) + TAIL
with tempfile.TemporaryDirectory() as d:
    for title, xml, expected in [
        ("valid", valid, True), ("invalid_shape", bad_shape, False),
        ("invalid_review", bad_continuity.replace('human_review="verified"', 'human_review="BAD"'), False),
    ]:
        p = Path(d) / (title + ".xml")
        p.write_text(xml, encoding="utf8")
        r = subprocess.run(["xmllint", "--noout", "--nonet", "--relaxng", str(SCHEMA), str(p)],
                           capture_output=True)
        if (r.returncode == 0) != expected:
            raise AssertionError(f"{title}: expected schema valid={expected}; got {r.stderr.decode()[:600]}")
root = ET.fromstring(valid)
chain = root.find(".//transmission")
assert not validate_transmission(chain, {"utt1"}, "fixture-valid")
bad = ET.fromstring(bad_continuity)
errors = validate_transmission(bad.find(".//transmission"), {"utt1"}, "fixture-bad")
assert any("does not continue" in x for x in errors), errors
assert any("differs" in x for x in errors), errors
assert any("aggregate verified" in x for x in errors), errors
print("XML schema and transmission chain regression examples passed")
