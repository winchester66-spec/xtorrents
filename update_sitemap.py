#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TODAY = datetime.date.today().isoformat()
BASE = "https://winchester66-spec.github.io/xtorrents/"

slugs = sorted(p.parent.name for p in (ROOT / "filme").glob("*/index.html"))

lines = []
lines.append('<?xml version="1.0" encoding="UTF-8"?>')
lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

# Home
lines.append("  <url>")
lines.append("    <loc>" + html.escape(BASE) + "</loc>")
lines.append("    <lastmod>" + TODAY + "</lastmod>")
lines.append("    <changefreq>daily</changefreq>")
lines.append("    <priority>1.0</priority>")
lines.append("  </url>")

# Filmes/Séries
for slug in slugs:
    loc = BASE + "filme/" + slug + "/"
    lines.append("  <url>")
    lines.append("    <loc>" + html.escape(loc) + "</loc>")
    lines.append("    <lastmod>" + TODAY + "</lastmod>")
    lines.append("    <changefreq>weekly</changefreq>")
    lines.append("    <priority>0.8</priority>")
    lines.append("  </url>")

lines.append("</urlset>")
lines.append("")

(ROOT / "sitemap.xml").write_text("\n".join(lines), encoding="utf-8", newline="")
print("sitemap.xml atualizado!")
print("Total de URLs: " + str(len(slugs) + 1))
print("Data: " + TODAY)
