#!/usr/bin/env python3
"""Regression examples for schema and transmission-chain semantics."""
from pathlib import Path
import subprocess
import json
import sys
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
# Exercise the same inventory guard used by CI, in an isolated tracked XML fixture.
with tempfile.TemporaryDirectory() as d:
    test_repo = Path(d)
    fixture = test_repo / "fixture.xml"
    inventory = test_repo / "inventory.json"
    audit_script = Path(__file__).resolve().with_name("xml_audit.py")
    inventory.write_text(json.dumps({
        "elements": ["content", "header"],
        "attributes_by_element": {"header": ["name"]},
    }), encoding="utf8")
    subprocess.run(["git", "init", "-q"], cwd=test_repo, check=True, capture_output=True)
    fixture.write_text('<content><header name="ok"/></content>', encoding="utf8")
    subprocess.run(["git", "add", "fixture.xml"], cwd=test_repo, check=True, capture_output=True)
    audit_cmd = [
        sys.executable, str(audit_script), "--report", "audit.json",
        "--known-tags", "inventory.json",
    ]

    def check_fixture(xml: str):
        fixture.write_text(xml, encoding="utf8")
        return subprocess.run(audit_cmd, cwd=test_repo, capture_output=True, text=True)

    approved = check_fixture('<content><header name="ok"/></content>')
    assert approved.returncode == 0, approved.stderr
    new_attribute = check_fixture('<content><header name="ok" undocumented="x"/></content>')
    assert new_attribute.returncode != 0 and "New XML attribute header@undocumented" in new_attribute.stderr, new_attribute.stderr
    new_element = check_fixture('<content><new_element/></content>')
    assert new_element.returncode != 0 and "New XML element" in new_element.stderr, new_element.stderr
    inventory.unlink()
    missing = check_fixture('<content><header name="ok"/></content>')
    assert missing.returncode != 0 and "XML inventory missing" in missing.stderr, missing.stderr

# A deliberately forward-looking XSLT fixture includes an unknown future semantic
# child: metadata must remain hidden even before that child is in the RNG.
with tempfile.TemporaryDirectory() as d:
    fixture = Path(d) / "semantic-output.xml"
    fixture.write_text(
        '<content><p>VISIBLE_SEMANTIC_XSLT</p>'
        '<semantic_data version="1"><future>HIDDEN_SEMANTIC_XSLT</future></semantic_data>'
        '</content>', encoding="utf8",
    )
    for stylesheet in (Path(".meta/html.xslt"), Path(".meta/quote_html.xslt")):
        result = subprocess.run(
            ["xsltproc", "--nonet", str(stylesheet), str(fixture)],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, f"{stylesheet}: {result.stderr[:800]}"
        assert "VISIBLE_SEMANTIC_XSLT" in result.stdout, stylesheet
        assert "HIDDEN_SEMANTIC_XSLT" not in result.stdout, stylesheet

print("XML schema, inventory and XSLT regression examples passed")
