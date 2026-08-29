#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_github_pages.py

Corrige um site gerado para Hostinger/Apache/PHP para funcionar como versão estática no GitHub Pages.

Cenário esperado:
- Repositório GitHub Pages publicado em: https://winchester66-spec.github.io/xtorrents/
- Arquivo principal: index.html
- Páginas físicas: filme/*/index.html
- Downloads continuam rodando no domínio principal com PHP:
  https://xtorrents.com.br/start.php?id=SLUG&link=N

Como usar:
1. Coloque este script na raiz do projeto, na mesma pasta do index.html.
2. Execute:
   python fix_github_pages.py
3. Faça commit/push dos arquivos alterados.
"""

from pathlib import Path
import re
import html
import datetime

GITHUB_BASE = "https://winchester66-spec.github.io/xtorrents/"
GITHUB_PATH = "/xtorrents/"
HOSTINGER_BASE = "https://xtorrents.com.br/"
ROOT = Path(__file__).resolve().parent
TODAY = datetime.date.today().isoformat()


def read_text_safe(path: Path) -> str:
    """Lê HTML tentando UTF-8 primeiro e fallback latin-1."""
    data = path.read_bytes()
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1")


def write_text_utf8(path: Path, content: str):
    path.write_text(content, encoding="utf-8", newline="")


def fix_common_head_assets(content: str, prefix: str) -> str:
    """
    Corrige assets absolutos de favicon/logo para caminho relativo.
    prefix para index.html: ""
    prefix para filme/*/index.html: "../../"
    """
    replacements = {
        'href="/favicon.ico': f'href="{prefix}favicon.ico',
        'href="/favicon.svg': f'href="{prefix}favicon.svg',
        'href="/favicon-': f'href="{prefix}favicon-',
        'href="/favicon-x-metalico': f'href="{prefix}favicon-x-metalico',
        'href="/apple-touch-icon': f'href="{prefix}apple-touch-icon',
        'href="/android-chrome': f'href="{prefix}android-chrome',
        'href="/site.webmanifest': f'href="{prefix}site.webmanifest',
        'src="/x-logo-512.png': f'src="{prefix}x-logo-512.png',
        'src="/og-image.svg': f'src="{prefix}og-image.svg',
        'src="/capas/': f'src="{prefix}capas/',
        'href="/capas/': f'href="{prefix}capas/',
    }
    for old, new in replacements.items():
        content = content.replace(old, new)

    # Corrige canonical/og:url/twitter se existirem apontando para o domínio principal.
    # No index será a URL base do GitHub; em páginas de filme será tratado separadamente.
    return content


def fix_root_index(path: Path) -> bool:
    if not path.exists():
        print(f"[AVISO] index.html não encontrado em {path}")
        return False

    content = read_text_safe(path)
    original = content

    # Links de páginas de filmes no index: /filme/SLUG/ -> filme/SLUG/
    content = content.replace('href="/filme/', 'href="filme/')
    content = content.replace("href='/filme/", "href='filme/")

    # Caso tenha URLs absolutas do GitHub sem /xtorrents/.
    content = content.replace('https://winchester66-spec.github.io/filme/', 'filme/')

    # Assets na raiz não devem começar com / no GitHub Pages em subpasta.
    content = fix_common_head_assets(content, prefix="")

    # Home/âncoras na raiz.
    content = content.replace('href="/#sobre"', 'href="#sobre"')
    content = content.replace("href='/#sobre'", "href='#sobre'")

    # Download no index, se existir, deve ir para Hostinger.
    content = content.replace('href="/start.php?id=', f'href="{HOSTINGER_BASE}start.php?id=')
    content = content.replace("href='/start.php?id=", f"href='{HOSTINGER_BASE}start.php?id=")
    content = content.replace('href="/iniciar.php?id=', f'href="{HOSTINGER_BASE}iniciar.php?id=')
    content = content.replace("href='/iniciar.php?id=", f"href='{HOSTINGER_BASE}iniciar.php?id=")

    # SEO/canonical da versão GitHub Pages.
    content = re.sub(
        r'<link rel="canonical" href="[^"]*">',
        f'<link rel="canonical" href="{GITHUB_BASE}">',
        content,
        count=1,
    )
    content = re.sub(
        r'<meta property="og:url" content="[^"]*">',
        f'<meta property="og:url" content="{GITHUB_BASE}">',
        content,
        count=1,
    )

    if content != original:
        write_text_utf8(path, content)
        return True
    return False


def fix_film_page(path: Path) -> bool:
    content = read_text_safe(path)
    original = content

    # Páginas de filme estão em filme/slug/index.html, então a home fica ../../
    content = content.replace('href="/"', 'href="../../"')
    content = content.replace("href='/'", "href='../../'")
    content = content.replace('href="/#sobre"', 'href="../../#sobre"')
    content = content.replace("href='/#sobre'", "href='../../#sobre'")

    # Relacionados: /filme/SLUG/ -> ../../filme/SLUG/
    content = content.replace('href="/filme/', 'href="../../filme/')
    content = content.replace("href='/filme/", "href='../../filme/")

    # Corrige URLs absolutas erradas do GitHub sem /xtorrents/.
    content = content.replace('https://winchester66-spec.github.io/filme/', '../../filme/')

    # Botões de download: GitHub Pages não executa PHP; mandar para Hostinger.
    content = content.replace('href="/start.php?id=', f'href="{HOSTINGER_BASE}start.php?id=')
    content = content.replace("href='/start.php?id=", f"href='{HOSTINGER_BASE}start.php?id=")
    content = content.replace('href="/iniciar.php?id=', f'href="{HOSTINGER_BASE}iniciar.php?id=')
    content = content.replace("href='/iniciar.php?id=", f"href='{HOSTINGER_BASE}iniciar.php?id=")

    # Se algum link relativo start.php apareceu dentro das páginas, força Hostinger.
    content = content.replace('href="../../start.php?id=', f'href="{HOSTINGER_BASE}start.php?id=')
    content = content.replace('href="../start.php?id=', f'href="{HOSTINGER_BASE}start.php?id=')
    content = content.replace('href="start.php?id=', f'href="{HOSTINGER_BASE}start.php?id=')
    content = content.replace('href="../../iniciar.php?id=', f'href="{HOSTINGER_BASE}iniciar.php?id=')
    content = content.replace('href="../iniciar.php?id=', f'href="{HOSTINGER_BASE}iniciar.php?id=')
    content = content.replace('href="iniciar.php?id=', f'href="{HOSTINGER_BASE}iniciar.php?id=')

    # Assets nas páginas de filme precisam subir dois níveis.
    content = fix_common_head_assets(content, prefix="../../")

    # Canonical/OG devem apontar para a URL pública real no GitHub Pages.
    # Descobre slug a partir de filme/slug/index.html
    try:
        slug = path.parent.name
        page_url = f"{GITHUB_BASE}filme/{slug}/"
        content = re.sub(
            r'<link rel="canonical" href="[^"]*">',
            f'<link rel="canonical" href="{page_url}">',
            content,
            count=1,
        )
        content = re.sub(
            r'<meta property="og:url" content="[^"]*">',
            f'<meta property="og:url" content="{page_url}">',
            content,
            count=1,
        )
    except Exception:
        pass

    if content != original:
        write_text_utf8(path, content)
        return True
    return False


def create_404():
    content = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,follow">
<title>Página não encontrada | x-torrents</title>
<style>
body{{margin:0;min-height:100vh;display:grid;place-items:center;background:#090b10;color:#fff;font-family:Arial,sans-serif;text-align:center;padding:24px}}
.box{{max-width:560px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);border-radius:20px;padding:32px}}
h1{{color:#ffc928}}
a{{display:inline-block;margin-top:14px;color:#111;background:linear-gradient(135deg,#ffc928,#ff8a00);padding:12px 18px;border-radius:999px;text-decoration:none;font-weight:900}}
</style>
</head>
<body>
<div class="box">
  <h1>Página não encontrada</h1>
  <p>Você será redirecionado para o catálogo x-torrents.</p>
  <a href="{GITHUB_PATH}">Voltar ao catálogo</a>
</div>
<script>
setTimeout(function(){{ location.href = '{GITHUB_PATH}'; }}, 1800);
</script>
</body>
</html>
"""
    write_text_utf8(ROOT / "404.html", content)


def create_robots():
    content = f"""User-agent: *
Allow: /xtorrents/
Sitemap: {GITHUB_BASE}sitemap.xml
"""
    write_text_utf8(ROOT / "robots.txt", content)


def discover_film_slugs():
    film_dir = ROOT / "filme"
    if not film_dir.exists():
        return []
    slugs = []
    for p in film_dir.glob("*/index.html"):
        slugs.append(p.parent.name)
    return sorted(set(slugs))


def create_sitemap(slugs):
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        '  <url>',
        f'    <loc>{html.escape(GITHUB_BASE)}</loc>',
        f'    <lastmod>{TODAY}</lastmod>',
        '    <changefreq>daily</changefreq>',
        '    <priority>1.0</priority>',
        '  </url>',
    ]
    for slug in slugs:
        loc = f"{GITHUB_BASE}filme/{slug}/"
        lines += [
            '  <url>',
            f'    <loc>{html.escape(loc)}</loc>',
            f'    <lastmod>{TODAY}</lastmod>',
            '    <changefreq>weekly</changefreq>',
            '    <priority>0.8</priority>',
            '  </url>',
        ]
    lines.append('</urlset>')
    lines.append('')
    write_text_utf8(ROOT / "sitemap.xml", "\n".join(lines))


def update_manifest():
    manifest = ROOT / "site.webmanifest"
    if not manifest.exists():
        return False
    content = read_text_safe(manifest)
    original = content
    # Corrige caminhos absolutos para GitHub Pages.
    content = content.replace('"src": "/android-chrome', '"src": "/xtorrents/android-chrome')
    content = content.replace('"src":"/android-chrome', '"src":"/xtorrents/android-chrome')
    content = content.replace('"src": "/favicon', '"src": "/xtorrents/favicon')
    content = content.replace('"src":"/favicon', '"src":"/xtorrents/favicon')
    if content != original:
        write_text_utf8(manifest, content)
        return True
    return False


def main():
    print("Corrigindo projeto para GitHub Pages...")
    print(f"Raiz: {ROOT}")
    print(f"Base GitHub Pages: {GITHUB_BASE}")
    print(f"Downloads continuarão em: {HOSTINGER_BASE}start.php")
    print()

    changed_root = fix_root_index(ROOT / "index.html")

    film_pages = list((ROOT / "filme").glob("*/index.html")) if (ROOT / "filme").exists() else []
    changed_films = 0
    for i, page in enumerate(film_pages, 1):
        if fix_film_page(page):
            changed_films += 1
        if i % 500 == 0:
            print(f"Processadas {i}/{len(film_pages)} páginas de filme...")

    create_404()
    create_robots()
    slugs = discover_film_slugs()
    create_sitemap(slugs)
    manifest_changed = update_manifest()

    print()
    print("Finalizado.")
    print(f"index.html alterado: {'sim' if changed_root else 'não'}")
    print(f"Páginas de filme encontradas: {len(film_pages)}")
    print(f"Páginas de filme alteradas: {changed_films}")
    print(f"site.webmanifest alterado: {'sim' if manifest_changed else 'não/não encontrado'}")
    print(f"404.html criado/atualizado: sim")
    print(f"robots.txt criado/atualizado: sim")
    print(f"sitemap.xml criado com {len(slugs) + 1} URLs")
    print()
    print("Agora faça commit e push no GitHub.")
    print("Teste depois:")
    print(f"- {GITHUB_BASE}")
    print(f"- {GITHUB_BASE}filme/ghost-in-the-cell/")
    print(f"- {GITHUB_BASE}sitemap.xml")


if __name__ == "__main__":
    main()
