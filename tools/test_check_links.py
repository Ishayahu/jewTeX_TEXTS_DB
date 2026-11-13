#!/usr/bin/env python3
"""Regressions for the corpus-aware internal XML link verifier."""
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from check_links import Corpus, Finding, new_regressions, scan


class InternalLinksTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.put("info.xml", "<info/>")

    def put(self, name: str, xml: str):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(xml, encoding="utf-8")

    def book(self, name: str, xml: str):
        self.put(name + "/info.xml", "<info/>")
        self.put(name + "/01.xml", xml)

    def reason(self, xml: str):
        return Corpus(self.root).resolve(ET.fromstring(xml))

    def test_valid_book_and_nested_siman_seif(self):
        self.book("joseph_karo/shulchan_aruch_yoreh_deah",
                  '<content><header type="siman" name="246">'
                  '<header type="seif" name="21"><p>Текст</p></header>'
                  '</header></content>')
        attrs = 'author="joseph_karo" book="shulchan_aruch_yoreh_deah"'
        self.assertIsNone(self.reason(f'<link {attrs}/>'))
        self.assertIsNone(self.reason(f'<link {attrs} siman="246" seif="21"/>'))
        self.assertIn("seif 22", self.reason(f'<link {attrs} siman="246" seif="22"/>'))

    def test_misspelled_hullin_book_is_rejected(self):
        self.book("talmud/hullin", '<content><daf name="8a"><p>Текст</p></daf></content>')
        self.assertIn("book not found", self.reason('<link author="talmud" book="chullin" daf="8a"/>'))
        self.assertIsNone(self.reason('<link author="talmud" book="hullin" daf="8a"/>'))
        self.assertIn("daf 44b", self.reason('<link author="talmud" book="hullin" daf="44b"/>'))

    def test_chapter_ancestor_with_daf_is_supported(self):
        self.book("talmud/nedarim",
                  '<content><header type="chapter" name="3">'
                  '<daf name="32a"><p>Текст</p></daf></header></content>')
        self.assertIsNone(self.reason('<link author="talmud" book="nedarim" chapter="3" daf="32a"/>'))
        self.assertIn("chapter 4", self.reason('<link author="talmud" book="nedarim" chapter="4" daf="32a"/>'))

    def test_posuk_must_be_in_matching_chapter(self):
        self.book("tanakh/proverbs",
                  '<content><header type="chapter" name="13">'
                  '<header type="posuk" name="27"><p>Текст</p></header>'
                  '</header></content>')
        self.assertIn("chapter 15", self.reason(
            '<link author="tanakh" book="proverbs" chapter="15" posuk="27"/>'))

    def test_empty_target_is_invalid(self):
        self.book("talmud/taanit", '<content><daf name="21b"><p/></daf></content>')
        self.assertIn("no readable text", self.reason(
            '<link author="talmud" book="taanit" daf="21b"/>'))

    def test_quote_and_page(self):
        self.book("tora/bereshit",
                  '<content><page name="1"><p>Первый текст</p></page></content>')
        self.assertIsNone(self.reason('<quote author="tora" book="bereshit" page="1"/>'))
        self.assertIn("page 2", self.reason('<quote author="tora" book="bereshit" page="2"/>'))

    def test_empty_book_and_missing_target_fields(self):
        self.put("talmud/taanit/info.xml", "<info/>")
        self.assertIn("no text XML", self.reason('<link author="talmud" book="taanit"/>'))
        self.assertIn("missing author", self.reason('<link book="taanit"/>'))

    def test_scan_and_new_regressions_preserve_old_problems(self):
        self.book("talmud/hullin", '<content><daf name="8a"><p>Текст</p></daf></content>')
        self.book("lastov_ishayahu/parasha_lessons",
                  '<content>'
                  '<link author="talmud" book="chullin" daf="44b">Старый</link>'
                  '<quote author="talmud" book="hullin" daf="99b"/>'
                  '</content>')
        issues = scan(self.root)
        self.assertEqual(len(issues), 2)
        self.assertEqual(new_regressions(issues, issues), [])
        self.assertEqual(len(new_regressions(issues, issues[:1])), 1)

    def test_deleted_target_becomes_new_regression(self):
        self.book("talmud/hullin", '<content><daf name="8a"><p>Текст</p></daf></content>')
        reference = ET.fromstring('<link author="talmud" book="hullin" daf="8a"/>')
        self.assertIsNone(Corpus(self.root).resolve(reference))
        self.put("talmud/hullin/01.xml", '<content><daf name="9a"><p>Текст</p></daf></content>')
        self.assertIn("daf 8a", Corpus(self.root).resolve(reference))

    def test_duplicate_new_invalid_link_not_silenced(self):
        invalid = Finding("book/01.xml", "link", (("book", "bad"),), "missing book")
        self.assertEqual(len(new_regressions([invalid, invalid], [invalid])), 1)


if __name__ == "__main__":
    unittest.main()
