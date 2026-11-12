#!/usr/bin/env python3
"""Re-render every sketch and compare it with its painting, pixel by pixel.

    pip install playwright && playwright install chromium
    python verify/verify.py                 # all 75
    python verify/verify.py 12 34           # just these

Each sketch runs in headless Chromium with p5.js 2.3.2, the version the paintings were made
with, on an 800 x 800 canvas. The render is drawn next to the committed PNG and the two are
compared in the page. A painting passes when no pixel differs by more than 8 (of 255) in any
channel, which allows for antialiasing differences between Chromium builds on bar edges.

Output matches verify/RESULTS.txt; diff your run against it.
"""

import asyncio
import base64
import json
import sys
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
P5 = "https://cdn.jsdelivr.net/npm/p5@2.3.2/lib/p5.min.js"
TOLERANCE = 8

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<script src="P5_URL"></script></head><body><script>
window.__errors = [];
window.onerror = (m) => { window.__errors.push(String(m)); return true };
SKETCH
</script></body></html>"""

COMPARE = """async ([ref, tol]) => {
  const canvas = document.querySelector('canvas');
  const w = canvas.width, h = canvas.height;
  const a = canvas.getContext('2d').getImageData(0, 0, w, h).data;
  const img = new Image();
  img.src = ref;
  await img.decode();
  const c = document.createElement('canvas');
  c.width = img.width; c.height = img.height;
  const ctx = c.getContext('2d');
  ctx.drawImage(img, 0, 0);
  if (img.width !== w || img.height !== h) return {size: [w, h, img.width, img.height]};
  const b = ctx.getImageData(0, 0, w, h).data;
  let differ = 0, worst = 0;
  for (let i = 0; i < a.length; i += 4) {
    const d = Math.max(Math.abs(a[i] - b[i]), Math.abs(a[i + 1] - b[i + 1]), Math.abs(a[i + 2] - b[i + 2]));
    if (d > 0) differ++;
    if (d > worst) worst = d;
  }
  return {differ, worst, total: w * h};
}"""


async def check(browser, n):
    nn = f"{n:02d}"
    sketch = (ROOT / "sketches" / f"{nn}.js").read_text()
    ref = "data:image/png;base64," + base64.b64encode((ROOT / "paintings" / f"{nn}.png").read_bytes()).decode()
    page = await browser.new_page(viewport={"width": 1000, "height": 1000}, device_scale_factor=1)
    try:
        await page.set_content(PAGE.replace("P5_URL", P5).replace("SKETCH", sketch))
        await page.wait_for_function("typeof frameCount !== 'undefined' && frameCount >= 1", timeout=30000)
        errors = await page.evaluate("window.__errors")
        if errors:
            return f"{nn}  ERROR  {errors[0]}"
        r = await page.evaluate(COMPARE, [ref, TOLERANCE])
        if "size" in r:
            return f"{nn}  FAIL   size {r['size']}"
        verdict = "PASS" if r["worst"] <= TOLERANCE else "FAIL"
        return f"{nn}  {verdict}   pixels differing {r['differ']:>6} of {r['total']}, largest difference {r['worst']}"
    finally:
        await page.close()


async def main(ns):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        sem = asyncio.Semaphore(4)

        async def one(n):
            async with sem:
                return await check(browser, n)

        lines = await asyncio.gather(*(one(n) for n in ns))
        await browser.close()
    for line in lines:
        print(line)
    passed = sum(" PASS " in l for l in lines)
    print(f"\n{passed} of {len(lines)} paintings reproduced from their sketches (tolerance {TOLERANCE}/255).")
    return passed == len(lines)


if __name__ == "__main__":
    catalog = json.loads((ROOT / "catalog.json").read_text())
    ns = [int(a) for a in sys.argv[1:]] or [c["n"] for c in catalog]
    sys.exit(0 if asyncio.run(main(ns)) else 1)
