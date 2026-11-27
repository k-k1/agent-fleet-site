"""Regression tests for the wording of guide landing cards."""

import unittest

from to_starlight import _predicate


class ShelfDescriptionTests(unittest.TestCase):
    def test_japanese_reference_opening(self):
        title = "**[リファレンス](/docs/ja/ref/)**"
        text = "使える機能を確認できます。"
        for opening in (" は", " では、"):
            with self.subTest(opening=opening):
                self.assertEqual(_predicate(title + opening + text, "ja"), text)
