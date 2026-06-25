# -*- coding: utf-8 -*-
"""발표 보고서 report.html → 16:9 PDF (Playwright)."""
import pathlib
from playwright.sync_api import sync_playwright

BASE = pathlib.Path(r"C:/Users/최용우/claude/yearsubway_11team/report")
SRC = (BASE / "report.html").resolve().as_uri()
OUT = str(BASE / "서울지하철_혼잡도분석_발표자료_11team.pdf")

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 720}, device_scale_factor=2)
    pg.goto(SRC, wait_until="networkidle")
    pg.evaluate("document.fonts.ready")
    pg.pdf(path=OUT, width="1280px", height="720px", print_background=True,
           margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
    b.close()
print("PDF OK:", OUT)
