"""Capture UI screenshots (uses system Chrome). python scripts/shots.py outdir"""
import sys, time
from playwright.sync_api import sync_playwright
out = sys.argv[1] if len(sys.argv) > 1 else "shots"
import os; os.makedirs(out, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1500, "height": 900})
    pg.goto("http://localhost:8000"); pg.click("#reset"); pg.wait_for_timeout(2500)
    pg.click("#ask"); pg.wait_for_timeout(1500); pg.screenshot(path=f"{out}/1-before.png")
    pg.click("#go"); pg.wait_for_timeout(7000); pg.screenshot(path=f"{out}/2-after-correction.png")
    pg.click("#ask"); pg.wait_for_timeout(1500)
    pg.click("#sw"); pg.click("#ask"); pg.wait_for_timeout(1500); pg.screenshot(path=f"{out}/3-graph-off.png")
    b.close()
