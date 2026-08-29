#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Encurtamento em massa via Encurta.net para o site TorrentFilms.
Uso seguro: coloque o token em variável de ambiente, sem salvar no HTML.

Linux/Mac:
  ENCURTA_TOKEN='SEU_TOKEN_AQUI' python3 encurta_net_massivo.py

Windows PowerShell:
  $env:ENCURTA_TOKEN='SEU_TOKEN_AQUI'; python encurta_net_massivo.py
"""
import os, re, json, time, html, shutil, urllib.parse, urllib.request
from pathlib import Path

DOMAIN = os.environ.get('SITE_URL', 'https://torrentfilms.produtodigital.org/').rstrip('/') + '/'
TOKEN = os.environ.get('ENCURTA_TOKEN', '').strip()
INPUT = Path(os.environ.get('INPUT_HTML', '/home/user/index_hostinger.html'))
OUTDIR = Path(os.environ.get('OUTDIR', '/home/user/hostinger_encurta_upload'))
CACHE_FILE = Path(os.environ.get('CACHE_FILE', '/home/user/encurta_cache.json'))
ADS_TYPE = os.environ.get('ENCURTA_ADS_TYPE', '1')  # 1 = anúncios/interstitial segundo wrapper público; 0 = sem anúncios
DELAY = float(os.environ.get('ENCURTA_DELAY', '0.35'))
DRY_RUN = os.environ.get('DRY_RUN', '0') == '1'

if not INPUT.exists():
    raise SystemExit(f'Arquivo HTML não encontrado: {INPUT}')

raw = INPUT.read_text(encoding='utf-8')
start = raw.find('const MOVIES = ')
if start < 0:
    raise SystemExit('Não encontrei const MOVIES no HTML.')
arr_start = start + len('const MOVIES = ')
arr_end = raw.find('];', arr_start) + 1
movies = json.loads(raw[arr_start:arr_end])

cache = {}
if CACHE_FILE.exists():
    try:
        cache = json.loads(CACHE_FILE.read_text(encoding='utf-8'))
    except Exception:
        cache = {}

links = {}
created = 0
reused = 0
failed = []

def shorten(long_url: str) -> str:
    global created, reused
    if DRY_RUN:
        return long_url
    if not TOKEN:
        raise SystemExit('Defina a variável ENCURTA_TOKEN com seu token/API key do Encurta.net.')
    if long_url in cache:
        reused += 1
        return cache[long_url]
    params = urllib.parse.urlencode({
        'api': TOKEN,
        'url': long_url,
        'type': ADS_TYPE,
    })
    api_url = 'https://encurta.net/api/?' + params
    req = urllib.request.Request(api_url, headers={'User-Agent': 'TorrentFilms-Link-Generator/1.0'})
    with urllib.request.urlopen(req, timeout=35) as resp:
        body = resp.read().decode('utf-8', 'replace').strip()
    try:
        data = json.loads(body)
    except Exception:
        # Alguns modos da API podem responder texto puro. Se parecer URL, aceita.
        if body.startswith('http'):
            cache[long_url] = body
            created += 1
            return body
        raise RuntimeError(f'Resposta inesperada da API: {body[:300]}')
    if data.get('status') == 'error':
        raise RuntimeError(str(data.get('message', data)))
    short = data.get('shortenedUrl') or data.get('shortedUrl') or data.get('shorturl') or data.get('url')
    if not short:
        raise RuntimeError(f'Não achei shortenedUrl na resposta: {data}')
    cache[long_url] = short
    created += 1
    time.sleep(DELAY)
    return short

for m in movies:
    slug = m.get('_slug') or re.sub(r'[^a-z0-9]+', '-', m['title'].lower()).strip('-')
    links[slug] = []
    for i, item in enumerate(m.get('magnets', [])):
        original = item.get('url', '')
        links[slug].append(original)
        go_url = f'{DOMAIN}go.php?id={urllib.parse.quote(slug)}&link={i}'
        try:
            item['url'] = shorten(go_url)
        except Exception as e:
            failed.append({'title': m.get('title'), 'slug': slug, 'link': i, 'error': str(e)})
            # fallback: deixa go.php direto para não quebrar download
            item['url'] = go_url

OUTDIR.mkdir(parents=True, exist_ok=True)
new_html = raw[:arr_start] + json.dumps(movies, ensure_ascii=False, separators=(',', ':')) + raw[arr_end:]
(OUTDIR / 'index.html').write_text(new_html, encoding='utf-8')

# links.php não imprime nada ao ser acessado diretamente; só retorna o array quando incluído.
php_array = "<?php\nreturn " + repr(links).replace('None', 'null').replace('True', 'true').replace('False', 'false') + ";\n"
(OUTDIR / 'links.php').write_text(php_array, encoding='utf-8')

GO_PHP = r'''<?php
$links = require __DIR__ . '/links.php';
$id = isset($_GET['id']) ? preg_replace('/[^a-z0-9\-]/i', '', $_GET['id']) : '';
$idx = isset($_GET['link']) ? intval($_GET['link']) : 0;
$url = $links[$id][$idx] ?? null;
if (!$url) {
  http_response_code(404);
  echo '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><title>Link não encontrado</title></head><body style="font-family:Arial;background:#080b13;color:#fff;text-align:center;padding:40px"><h1>Link não encontrado</h1><p>Volte ao site e tente novamente.</p><a style="color:#ffc400" href="/">Voltar</a></body></html>';
  exit;
}
$safe = htmlspecialchars($url, ENT_QUOTES, 'UTF-8');
?>
<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Preparando download...</title>
<style>
body{margin:0;min-height:100vh;display:grid;place-items:center;background:radial-gradient(circle at top,#1a2440,#080b13 55%,#05060a);color:#fff;font-family:Arial,sans-serif}.box{width:min(92vw,520px);background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.12);border-radius:20px;padding:28px;text-align:center;box-shadow:0 24px 60px rgba(0,0,0,.4)}h1{margin:0 0 10px;color:#ffc400}.loader{width:46px;height:46px;border:4px solid rgba(255,255,255,.18);border-top-color:#ffc400;border-radius:50%;margin:18px auto;animation:spin 1s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}a{display:inline-block;margin-top:14px;background:linear-gradient(90deg,#ffc400,#ff7a18);color:#160f00;text-decoration:none;font-weight:900;padding:12px 18px;border-radius:999px}
</style>
</head>
<body>
<div class="box">
  <h1>Preparando seu download</h1>
  <p>Se o download não abrir automaticamente, clique no botão abaixo.</p>
  <div class="loader"></div>
  <a id="go" href="<?= $safe ?>">Abrir download</a>
</div>
<script>
setTimeout(function(){ window.location.href = document.getElementById('go').href; }, 900);
</script>
</body>
</html>
'''
(OUTDIR / 'go.php').write_text(GO_PHP, encoding='utf-8')

robots = f"User-agent: *\nAllow: /\nDisallow: /go.php\nSitemap: {DOMAIN}sitemap.xml\n"
(OUTDIR / 'robots.txt').write_text(robots, encoding='utf-8')

sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{DOMAIN}</loc>
    <lastmod>2026-08-22</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
'''
(OUTDIR / 'sitemap.xml').write_text(sitemap, encoding='utf-8')

htaccess = r'''Options -Indexes

<Files "links.php">
  Require all denied
</Files>

<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteCond %{HTTPS} !=on
  RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
</IfModule>

<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/plain text/css text/javascript application/javascript application/json application/xml image/svg+xml
</IfModule>

<IfModule mod_headers.c>
  Header set X-Content-Type-Options "nosniff"
  Header set Referrer-Policy "strict-origin-when-cross-origin"
</IfModule>
'''
(OUTDIR / '.htaccess').write_text(htaccess, encoding='utf-8')

CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8')

zip_path = OUTDIR.with_suffix('.zip')
if zip_path.exists():
    zip_path.unlink()
import zipfile
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
    for file in OUTDIR.iterdir():
        z.write(file, arcname=file.name)

print('Finalizado.')
print('Filmes:', len(movies))
print('Links processados:', sum(len(v) for v in links.values()))
print('Criados na API:', created)
print('Reutilizados do cache:', reused)
print('Falhas:', len(failed))
print('Pasta:', OUTDIR)
print('ZIP:', zip_path)
if failed:
    fail_file = OUTDIR / 'falhas_encurta.json'
    fail_file.write_text(json.dumps(failed, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Detalhes das falhas:', fail_file)
