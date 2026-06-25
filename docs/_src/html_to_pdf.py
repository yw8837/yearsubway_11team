# -*- coding: utf-8 -*-
"""기획서.html → A4 PDF (Playwright/Chromium, 웹폰트·배경 보존)."""
import pathlib
from playwright.sync_api import sync_playwright

BASE = pathlib.Path(r"C:/Users/최용우/claude/yearsubway_11team/docs")
SRC = (BASE / "기획서.html").resolve().as_uri()
OUT = str(BASE / "서울지하철_혼잡도분석_기획서_11team.pdf")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(SRC, wait_until="networkidle")
    page.evaluate("document.fonts.ready")        # 웹폰트 로드 보장
    page.pdf(path=OUT, format="A4", print_background=True,
             margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
    browser.close()

print("PDF OK:", OUT)
