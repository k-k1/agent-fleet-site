#!/usr/bin/env python3
"""Render the social preview images site/og-en.png and site/og-ja.png.

Run after scripts/sync-shots.sh, since the card shows the Console screenshot:

    scripts/render-og.py

Needs headless Chromium and, for the Japanese card, a CJK font (Noto Sans CJK JP).
Without one Chromium falls back to tofu boxes and still exits 0, so look at the result.

The copy is HTML with hand-placed line breaks: Japanese has no spaces to wrap at, and
an automatic break lands mid-word.
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
W, H = 1200, 630

COPY = {
    "en": {
        "font": 'system-ui, "Helvetica Neue", Arial, sans-serif',
        "line1": "Don't replace your coding agents.",
        "line2": "Operate them.",
        "sub": "A self-hosted operations layer<br>for AI coding agents",
    },
    "ja": {
        "font": '"Noto Sans CJK JP", "Hiragino Sans", "Yu Gothic UI", sans-serif',
        "line1": "エージェントは<br>置き換えない。",
        "line2": "運用する。",
        "sub": "AI コーディングエージェントを運用する、<br>自社ホストの基盤",
    },
}

TEMPLATE = """<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><style>
html, body {{ margin: 0; width: {w}px; height: {h}px; overflow: hidden; }}
body {{
  position: relative; color: #e6eef0; font-family: {font};
  background: radial-gradient(900px 520px at 0% 0%, rgb(20 155 167 / 0.35), transparent 70%), #0b1417;
}}
.brand {{ position: absolute; left: 64px; top: 56px; display: flex; align-items: center; gap: 16px;
  font-size: 34px; font-weight: 700; }}
.brand img {{ width: 60px; height: 60px; border-radius: 14px; }}
h1 {{ position: absolute; left: 64px; top: 170px; width: 560px; margin: 0;
  font-size: {size}px; line-height: 1.15; font-weight: 800; letter-spacing: -0.01em; }}
h1 span {{ display: block; color: #3cc4cf; margin-top: 10px; }}
p {{ position: absolute; left: 64px; bottom: 56px; width: 540px; margin: 0; font-size: 24px; color: #a3b4b9; line-height: 1.4; }}
.url {{ display: block; margin-top: 10px; color: #3cc4cf; font-weight: 600; }}
.shot {{ position: absolute; left: 660px; top: 70px; width: 820px; border-radius: 16px; overflow: hidden;
  border: 1px solid #22363d; box-shadow: 0 0 0 1px rgb(20 155 167 / 0.3), 0 30px 90px -20px rgb(20 155 167 / 0.55); }}
.shot img {{ display: block; width: 100%; }}
</style></head><body>
<div class="brand"><img src="{icon}" alt="">Agent Fleet</div>
<h1>{line1}<span>{line2}</span></h1>
<p>{sub}<span class="url">agent-fleet.org</span></p>
<div class="shot"><img src="{shot}" alt=""></div>
</body></html>
"""


def main() -> int:
    chromium = shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")
    if not chromium:
        print("render-og: no chromium on PATH", file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        for lang, c in COPY.items():
            html = pathlib.Path(tmp) / f"og-{lang}.html"
            html.write_text(TEMPLATE.format(
                lang=lang, w=W, h=H, font=c["font"],
                size=56,
                line1=c["line1"], line2=c["line2"], sub=c["sub"],
                icon=(SITE / "assets/brand/icon-192.png").as_uri(),
                shot=(SITE / f"assets/img/console-{lang}.webp").as_uri(),
            ), encoding="utf-8")
            raw = pathlib.Path(tmp) / f"og-{lang}.png"
            subprocess.run([
                chromium, "--headless", "--disable-gpu", "--hide-scrollbars",
                "--force-device-scale-factor=1", f"--window-size={W},{H}",
                "--allow-file-access-from-files", f"--screenshot={raw}", html.as_uri(),
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
            img = Image.open(raw).convert("RGB")
            if img.size != (W, H):
                img = img.crop((0, 0, W, H))
            out = SITE / f"og-{lang}.png"
            img.save(out, optimize=True)
            print(f"wrote {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KiB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
