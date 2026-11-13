#!/usr/bin/env python3
"""Tests for the landing's one-liner block: to_starlight.oneliner.

    python3 -m unittest discover -s docs/scripts -p 'test_*.py'
"""
import shutil
import tempfile
import unittest
from pathlib import Path

import to_starlight as T

INSTALL = "curl -fsSL https://raw.githubusercontent.com/k-k1/agent-fleet-dist/main/install.sh | bash"
BLOCK = f"```bash\n{INSTALL}\naf start            # first run only\n# open http://localhost:8099 in a browser\n```\n"
FACTS = "Single-user Linux or WSL2, without Docker. On an Apple Silicon Mac, use a Linux VM.\n\n"


def page(title, body=""):
    return f"# {title}\n\n{FACTS}{body}"


class OneLiner(unittest.TestCase):
    def tree(self, files):
        d = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d)
        for rel, text in files.items():
            (d / rel).parent.mkdir(parents=True, exist_ok=True)
            (d / rel).write_text(text, encoding="utf-8")
        return d

    def main_tree(self, block=BLOCK, **extra):
        return self.tree({
            "operate/native/install.md": page("Install the native package", block),
            "operate/native/install.ja.md": page("ネイティブパッケージを入れる", block),
            "operate/native/update.md": page("Update"),
            "operate/compose/install.md": page("Deploy with Docker Compose"),
            "operate/compose/install.ja.md": page("Docker Compose で構築する"),
            **extra,
        })

    def test_main_layout(self):
        out = T.oneliner(self.main_tree(), "ja")
        self.assertIn("## 手元で 1 人で試す", out)
        self.assertIn("[Docker Compose で構築する](/docs/ja/operate/compose/install/)", out)
        self.assertIn("[ネイティブパッケージを入れる](/docs/ja/operate/native/install/)", out)
        self.assertIn(f"```bash\n{INSTALL}\naf start", out)

    def test_release_runbook_layout(self):
        d = self.tree({"operate/runbooks/native.md": page("Install the native package", BLOCK),
                       "operate/runbooks/compose.md": page("Compose")})
        out = T.oneliner(d, "ja")  # the runbooks have no Japanese: the English pages are linked
        self.assertIn("(/docs/operate/runbooks/native/)", out)
        self.assertIn("(/docs/operate/runbooks/compose/)", out)

    def test_missing_block_fails(self):
        with self.assertRaisesRegex(T.LandingError, "no code block"):
            T.oneliner(self.main_tree(block=""), "en")

    def test_changed_shape_fails(self):
        for block in (f"```bash\n{INSTALL}\n```\n",                        # af start gone
                      f"```bash\n{INSTALL}\naf start\nsudo af enable\n```\n",  # a command added
                      f"```sh\n{INSTALL}\naf start\n```\n",                  # not bash
                      BLOCK.replace("agent-fleet-dist/main", "agent-fleet-dist/v1")):
            with self.subTest(block=block), self.assertRaisesRegex(T.LandingError, "one-liner"):
                T.oneliner(self.main_tree(block=block), "en")

    def test_two_blocks_fail(self):
        with self.assertRaisesRegex(T.LandingError, "more than one"):
            T.oneliner(self.main_tree(**{"operate/native/service.md": page("Service", BLOCK)}), "en")

    def test_facts_must_stay_on_the_page(self):
        d = self.main_tree()
        p = d / "operate/native/install.md"
        p.write_text(p.read_text(encoding="utf-8").replace("Apple Silicon", "Intel"), encoding="utf-8")
        with self.assertRaisesRegex(T.LandingError, "Apple Silicon"):
            T.oneliner(d, "en")


if __name__ == "__main__":
    unittest.main()
