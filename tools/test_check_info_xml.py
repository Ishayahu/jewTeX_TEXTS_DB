#!/usr/bin/env python3
"""Regression tests for required info.xml detection."""
import unittest

from check_info_xml import is_exempt, missing_info_files


class InfoXmlCheckTests(unittest.TestCase):
    def test_complete_talmud_book(self):
        self.assertEqual(
            missing_info_files([
                "info.xml",
                "talmud/info.xml",
                "talmud/hullin/info.xml",
                "talmud/hullin/ch09.xml",
            ]),
            [],
        )

    def test_missing_tractate_info_detected(self):
        self.assertEqual(
            missing_info_files([
                "info.xml", "talmud/info.xml", "talmud/hullin/008.xml",
            ]),
            ["talmud/hullin/info.xml"],
        )

    def test_missing_author_and_book_info_detected(self):
        self.assertEqual(
            missing_info_files(["info.xml", "author/book/01.xml"]),
            ["author/info.xml", "author/book/info.xml"],
        )

    def test_missing_root_info_detected(self):
        self.assertEqual(
            missing_info_files(["talmud/info.xml"]),
            ["info.xml"],
        )

    def test_exempt_infrastructure_and_illustrations(self):
        self.assertEqual(
            missing_info_files([
                "info.xml", "tools/info.xml", "tools/check_info_xml.py",
                ".github/workflows/main.yml",
                "lastov_ishayahu/info.xml",
                "lastov_ishayahu/chronos/info.xml",
                "lastov_ishayahu/chronos/illustrations/figure.svg",
            ]),
            [],
        )

    def test_new_unlisted_subdirectory_is_checked(self):
        self.assertEqual(
            missing_info_files([
                "info.xml", "talmud/info.xml", "talmud/hullin/info.xml",
                "talmud/hullin/new_subdir/01.xml",
            ]),
            ["talmud/hullin/new_subdir/info.xml"],
        )

    def test_exceptions_are_exact_subtrees(self):
        self.assertTrue(is_exempt(".github/workflows"))
        self.assertFalse(is_exempt(".github-not-exempt"))
        self.assertFalse(is_exempt("author/book/meta"))


if __name__ == "__main__":
    unittest.main()
