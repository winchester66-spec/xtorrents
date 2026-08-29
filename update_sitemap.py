#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera sitemap index + sitemaps parciais para GitHub Pages.
Divide em partes de 1000 URLs para garantir compatibilidade com Google.
Remove slugs inválidos (muito longos ou com texto lixo).
"""
import datetime
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TODAY = datetime.date.today().isoformat()
BASE = "https://winchester66-spec.github.io/xtorrents/"
MAX_PER_FILE = 1000
MAX_SLUG_LEN = 80  # slugs maiores que isso são inválidos

slugs_raw = sorted(p.parent.name for p in (ROOT / "filme").glob("*/index.html"))

# Filtra slugs inválidos
slugs = [s for s in slugs_raw if len(s) <= MAX_SLUG_LEN]
removidos = [s for s in slugs_raw if len(s) > MAX_SLUG_LEN]

if removidos:
    print(f"Slugs inválidos removidos ({len(removidos)}):")
    for s in removidos:
        print(f"  - {s[:80]}...")

# Divide em partes
chunks = [slugs[i:i+MAX_PER_FILE] for i in range(0, len(slugs), MAX_PER_FILE)]

sitemap_files = []

for idx, chunk in enumerate(chunks, 1):
    filename = f"sitemap-{idx}.xml"
    sitemap_files.append(filename)
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    # Inclui home apenas no primeiro arquivo
    if idx == 1:
        lines.append("  <url>")
        lines.append("    <loc>" + html.escape(BASE) + "</loc>")
        lines.append("    <lastmod>" + TODAY + "</lastmod>")
        lines.append("    <changefreq>daily</changefreq>")
        lines.append("    <priority>1.0</priority>")
        lines.append("  </url>")

    for slug in chunk:
        loc = BASE + "filme/" + slug + "/"
        lines.append("  <url>")
        lines.append("    <loc>" + html.escape(loc) + "</loc>")
        lines.append("    <lastmod>" + TODAY + "</lastmod>")
        lines.append("    <changefreq>weekly</changefreq>")
        lines.append("    <priority>0.8</priority>")
        lines.append("  </url>")

    lines.append("</urlset>")
    lines.append("")
    (ROOT / filename).write_text("\n".join(lines), encoding="utf-8", newline="")
    print(f"  {filename}: {len(chunk) + (1 if idx == 1 else 0)} URLs")

# Gera sitemap index
index_lines = []
index_lines.append('<?xml version="1.0" encoding="UTF-8"?>')
index_lines.append('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
for filename in sitemap_files:
    index_lines.append("  <sitemap>")
    index_lines.append("    <loc>" + html.escape(BASE + filename) + "</loc>")
    index_lines.append("    <lastmod>" + TODAY + "</lastmod>")
    index_lines.append("  </sitemap>")
index_lines.append("</sitemapindex>")
index_lines.append("")
(ROOT / "sitemap.xml").write_text("\n".join(index_lines), encoding="utf-8", newline="")

total_urls = len(slugs) + 1  # +1 pela home
print()
print(f"sitemap.xml (index) criado com {len(sitemap_files)} arquivos parciais")
print(f"Total de URLs validas: {total_urls}")
print(f"Data: {TODAY}")
