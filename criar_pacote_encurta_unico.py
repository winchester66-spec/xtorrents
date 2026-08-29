import json, re, zipfile
from pathlib import Path

DOMAIN='https://torrentfilms.produtodigital.org/'
src=Path('/home/user/index_hostinger.html')
html=src.read_text(encoding='utf-8')
# Parse MOVIES
pos=html.find('const MOVIES = ')+len('const MOVIES = ')
end=html.find('];',pos)+1
movies=json.loads(html[pos:end])

# Build private links mapping and public movies without magnet URLs
links={}
public_movies=[]
for m in movies:
    slug=m.get('_slug') or re.sub(r'[^a-z0-9]+','-',m['title'].lower()).strip('-')
    links[slug]=[x.get('url','') for x in m.get('magnets',[])]
    nm=dict(m)
    nm['magnets']=[{'label': x.get('label','')} for x in m.get('magnets',[])]
    nm['_slug']=slug
    # remove old source link if exists
    nm.pop('link', None)
    public_movies.append(nm)

html=html[:pos]+json.dumps(public_movies,ensure_ascii=False,separators=(',',':'))+html[end:]

# Patch JS to route all download clicks to start.php, not magnet URLs
if 'function downloadUrl(m, idx)' not in html:
    needle="function card(m, compact=false, eager=false) {"
    html=html.replace(needle, "function downloadUrl(m, idx) {\n  return 'start.php?id=' + encodeURIComponent(m._slug) + '&link=' + encodeURIComponent(idx || 0);\n}\n"+needle, 1)

# Replace compact magnets mapping line in optimized JS
html=html.replace("const magnets = compact ? '' : m.magnets.map(l => '<a rel=\"nofollow\" href=\"' + esc(l.url) + '\">' + esc(l.label.replace(/^\\W+/, '')) + '</a>').join('');",
                  "const magnets = compact ? '' : m.magnets.map((l, idx) => '<a rel=\"nofollow\" href=\"' + downloadUrl(m, idx) + '\">' + esc(l.label.replace(/^\\W+/, '')) + '</a>').join('');")
html=html.replace("const magnetHref = m.magnets.length ? esc(m.magnets[0].url) : '#';",
                  "const magnetHref = m.magnets.length ? esc(downloadUrl(m, 0)) : '#';")
# If older variant has slightly different mapping
html=html.replace("const magnets = m.magnets.map(l => '<a rel=\"nofollow\" href=\"' + esc(l.url) + '\">' + esc(l.label.replace(/^\\W+/, '')) + '</a>').join('');",
                  "const magnets = m.magnets.map((l, idx) => '<a rel=\"nofollow\" href=\"' + downloadUrl(m, idx) + '\">' + esc(l.label.replace(/^\\W+/, '')) + '</a>').join('');")

outdir=Path('/home/user/hostinger_encurta_unico_upload')
outdir.mkdir(exist_ok=True)
(outdir/'index.html').write_text(html,encoding='utf-8')

# links.php
php_links="<?php\n// Arquivo privado com os magnets reais. Não edite a menos que saiba o que está fazendo.\nreturn "+repr(links).replace('None','null').replace('True','true').replace('False','false')+";\n"
(outdir/'links.php').write_text(php_links,encoding='utf-8')

config="""<?php
// Cole aqui o ÚNICO link encurtado do Encurta.net.
// Esse link deve apontar para: https://torrentfilms.produtodigital.org/download.php
// Exemplo: 'https://encurta.net/abc123'
return [
  'encurta_url' => 'COLE_AQUI_SEU_LINK_ENCURTADO_DO_ENCURTA_NET'
];
"""
(outdir/'config.php').write_text(config,encoding='utf-8')

start_php=r'''<?php
session_start();
$links = require __DIR__ . '/links.php';
$config = require __DIR__ . '/config.php';

$id = isset($_GET['id']) ? preg_replace('/[^a-z0-9\-]/i', '', $_GET['id']) : '';
$idx = isset($_GET['link']) ? intval($_GET['link']) : 0;

if (!$id || !isset($links[$id]) || !isset($links[$id][$idx])) {
  http_response_code(404);
  echo '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><title>Download não encontrado</title></head><body style="font-family:Arial;background:#080b13;color:#fff;text-align:center;padding:40px"><h1>Download não encontrado</h1><p>Volte ao catálogo e tente novamente.</p><a style="color:#ffc400" href="/">Voltar</a></body></html>';
  exit;
}

$_SESSION['pending_download'] = [
  'id' => $id,
  'link' => $idx,
  'time' => time()
];

$short = trim($config['encurta_url'] ?? '');
$placeholder = 'COLE_AQUI_SEU_LINK_ENCURTADO_DO_ENCURTA_NET';

// Enquanto você ainda não colou o link do Encurta.net em config.php,
// o sistema redireciona direto para download.php apenas para teste.
if (!$short || $short === $placeholder) {
  $short = '/download.php';
}

header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
header('Location: ' . $short, true, 302);
exit;
'''
(outdir/'start.php').write_text(start_php,encoding='utf-8')

download_php=r'''<?php
session_start();
$links = require __DIR__ . '/links.php';
$pending = $_SESSION['pending_download'] ?? null;

if (!$pending || !isset($pending['id'], $pending['link'], $pending['time'])) {
  http_response_code(403);
  echo '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Acesso expirado</title><style>body{font-family:Arial;background:#080b13;color:#fff;text-align:center;padding:40px}a{color:#ffc400}</style></head><body><h1>Acesso expirado</h1><p>Volte ao site e clique novamente no botão Baixar.</p><a href="/">Voltar ao catálogo</a></body></html>';
  exit;
}

if (time() - intval($pending['time']) > 1800) {
  unset($_SESSION['pending_download']);
  http_response_code(403);
  echo '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Download expirado</title><style>body{font-family:Arial;background:#080b13;color:#fff;text-align:center;padding:40px}a{color:#ffc400}</style></head><body><h1>Download expirado</h1><p>Volte ao site e clique novamente no botão Baixar.</p><a href="/">Voltar ao catálogo</a></body></html>';
  exit;
}

$id = preg_replace('/[^a-z0-9\-]/i', '', $pending['id']);
$idx = intval($pending['link']);
$url = $links[$id][$idx] ?? null;
if (!$url) {
  http_response_code(404);
  echo '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Link não encontrado</title><style>body{font-family:Arial;background:#080b13;color:#fff;text-align:center;padding:40px}a{color:#ffc400}</style></head><body><h1>Link não encontrado</h1><p>Volte ao site e tente novamente.</p><a href="/">Voltar</a></body></html>';
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
<title>Download liberado</title>
<style>
body{margin:0;min-height:100vh;display:grid;place-items:center;background:radial-gradient(circle at top,#1a2440,#080b13 55%,#05060a);color:#fff;font-family:Arial,sans-serif}.box{width:min(92vw,520px);background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.12);border-radius:20px;padding:28px;text-align:center;box-shadow:0 24px 60px rgba(0,0,0,.4)}h1{margin:0 0 10px;color:#ffc400}.loader{width:46px;height:46px;border:4px solid rgba(255,255,255,.18);border-top-color:#ffc400;border-radius:50%;margin:18px auto;animation:spin 1s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}a.btn{display:inline-block;margin-top:14px;background:linear-gradient(90deg,#ffc400,#ff7a18);color:#160f00;text-decoration:none;font-weight:900;padding:12px 18px;border-radius:999px}.muted{color:#b8c0d0;font-size:.9rem}.back{display:block;margin-top:16px;color:#ffc400;text-decoration:none;font-size:.85rem}
</style>
</head>
<body>
<div class="box">
  <h1>Download liberado</h1>
  <p class="muted">O magnet será aberto automaticamente. Se não abrir, clique no botão abaixo.</p>
  <div class="loader"></div>
  <a class="btn" id="go" href="<?= $safe ?>">Abrir download</a>
  <a class="back" href="/">Voltar ao catálogo</a>
</div>
<script>
setTimeout(function(){ window.location.href = document.getElementById('go').href; }, 1000);
</script>
</body>
</html>
'''
(outdir/'download.php').write_text(download_php,encoding='utf-8')

robots=f'''User-agent: *
Allow: /
Disallow: /start.php
Disallow: /download.php
Sitemap: {DOMAIN}sitemap.xml
'''
(outdir/'robots.txt').write_text(robots,encoding='utf-8')

sitemap=f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{DOMAIN}</loc>
    <lastmod>2026-08-22</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
'''
(outdir/'sitemap.xml').write_text(sitemap,encoding='utf-8')

htaccess=r'''Options -Indexes

<Files "links.php">
  Require all denied
</Files>
<Files "config.php">
  Require all denied
</Files>

<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteCond %{HTTPS} !=on
  RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
  RewriteCond %{HTTP_HOST} !^torrentfilms\.produtodigital\.org$ [NC]
  RewriteRule ^ https://torrentfilms.produtodigital.org%{REQUEST_URI} [L,R=301]
</IfModule>

<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/plain text/css text/javascript application/javascript application/json application/xml image/svg+xml
</IfModule>

<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType text/html "access plus 0 seconds"
  ExpiresByType image/jpeg "access plus 1 month"
  ExpiresByType image/png "access plus 1 month"
  ExpiresByType image/webp "access plus 1 month"
  ExpiresByType image/svg+xml "access plus 1 month"
</IfModule>

<IfModule mod_headers.c>
  Header set X-Content-Type-Options "nosniff"
  Header set Referrer-Policy "strict-origin-when-cross-origin"
</IfModule>
'''
(outdir/'.htaccess').write_text(htaccess,encoding='utf-8')

zip_path=Path('/home/user/site_hostinger_encurta_unico.zip')
if zip_path.exists(): zip_path.unlink()
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
    for f in outdir.iterdir():
        z.write(f,arcname=f.name)
print('Pasta:', outdir)
print('ZIP:', zip_path, zip_path.stat().st_size)
print('Filmes:', len(public_movies), 'magnets:', sum(len(v) for v in links.values()))
print('old magnet exposed count:', html.count('magnet:?'))
