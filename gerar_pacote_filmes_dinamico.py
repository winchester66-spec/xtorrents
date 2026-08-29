import json, re, html as htmlmod, zipfile, shutil
from pathlib import Path
DOMAIN='https://torrentfilms.produtodigital.org/'
LASTMOD='2026-08-22'
BASE=Path('/home/user/hostinger_encurta_unico_upload')
INDEX=BASE/'index.html'
html=INDEX.read_text(encoding='utf-8')
pos=html.find('const MOVIES = ')+len('const MOVIES = ')
end=html.find('];',pos)+1
movies=json.loads(html[pos:end])
# Ensure index links to detail pages
if 'Ver detalhes</a>' not in html:
    html=html.replace("'<div class=\"info\"><h2 itemprop=\"name\">' + esc(m.title) + '</h2>' +",
                      "'<div class=\"info\"><h2 itemprop=\"name\"><a href=\"filme/' + esc(m._slug) + '/\">' + esc(m.title) + '</a></h2>' +", 1)
    html=html.replace("'<div class=\"actions\"><a class=\"btn magnet\" rel=\"nofollow\" href=\"' + magnetHref + '\" aria-label=\"Baixar ' + esc(m.title) + '\">🧲 Baixar</a>' + extra + trailer + '</div>' +",
                      "'<div class=\"actions\"><a class=\"btn magnet\" rel=\"nofollow\" href=\"' + magnetHref + '\" aria-label=\"Baixar ' + esc(m.title) + '\">🧲 Baixar</a><a class=\"trailer\" href=\"filme/' + esc(m._slug) + '/\">Ver detalhes</a>' + extra + trailer + '</div>' +", 1)
    if '.info h2 a{' not in html:
        html=html.replace('.info h2{', '.info h2 a{color:inherit;text-decoration:none}.info h2 a:hover{color:var(--brand)}.info h2{', 1)
# build output folder clean
OUT=Path('/home/user/hostinger_filmes_dinamico_upload')
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir()
# copy core files from BASE, excluding physical filme folder and old sitemap variants
for f in BASE.iterdir():
    if f.name == 'filme' or f.name in ['sitemap-pages.xml','sitemap-images.xml']:
        continue
    if f.is_file():
        shutil.copy2(f, OUT/f.name)
(OUT/'index.html').write_text(html,encoding='utf-8')
# movies.php public data
movies_php="<?php\n// Dados públicos dos filmes para páginas dinâmicas.\n$json = <<<'JSON'\n"+json.dumps(movies,ensure_ascii=False,separators=(',',':'))+"\nJSON;\nreturn json_decode($json, true);\n"
(OUT/'movies.php').write_text(movies_php,encoding='utf-8')
# filme.php
filme_php=r'''<?php
$movies = require __DIR__ . '/movies.php';
$slug = isset($_GET['slug']) ? preg_replace('/[^a-z0-9\-]/i', '', $_GET['slug']) : '';
$movie = null;
$index = 0;
foreach ($movies as $i => $m) {
  if (($m['_slug'] ?? '') === $slug) { $movie = $m; $index = $i; break; }
}
if (!$movie) {
  http_response_code(404);
  echo '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="robots" content="noindex"><title>Filme não encontrado</title><style>body{font-family:Arial;background:#080b13;color:#fff;text-align:center;padding:40px}a{color:#ffc400}</style></head><body><h1>Filme não encontrado</h1><p>Volte ao catálogo e tente novamente.</p><a href="/">Voltar ao catálogo</a></body></html>';
  exit;
}
function e($s){ return htmlspecialchars((string)$s, ENT_QUOTES, 'UTF-8'); }
function badge($m,$kind){ foreach (($m['badges'] ?? []) as $b) { if (($b[0] ?? '') === $kind) return $b[1] ?? ''; } return ''; }
function yearFromTitle($title){ return preg_match('/\((\d{4})\)/', $title, $mm) ? $mm[1] : '2026'; }
function stripYear($title){ return trim(preg_replace('/\s*\(\d{4}\)\s*$/', '', $title)); }
$domain = 'https://torrentfilms.produtodigital.org/';
$title = $movie['title'] ?? 'Filme';
$name = stripYear($title);
$year = yearFromTitle($title);
$q = badge($movie,'q'); $size = badge($movie,'s'); $audio = badge($movie,'a');
$poster = $movie['poster'] ?? '';
$url = $domain . 'filme/' . $slug . '/';
$descParts = array_filter([$q, $audio, $size]);
$desc = 'Confira ' . $title . ' no TorrentFilms com capa, trailer, informações de qualidade' . (count($descParts) ? ' (' . implode(', ', $descParts) . ')' : '') . ' e opção autorizada de download.';
$trailer = '';
foreach (($movie['other'] ?? []) as $o) { $u = $o['url'] ?? ''; if (strpos($u,'youtube') !== false || strpos($u,'youtu.be') !== false) { $trailer=$u; break; } }
$ld = ['@context'=>'https://schema.org','@type'=>'Movie','name'=>$title,'image'=>$poster,'url'=>$url,'datePublished'=>$movie['date'] ?? $year,'description'=>$desc,'inLanguage'=>$audio ?: 'pt-BR'];
if ($trailer) $ld['trailer'] = ['@type'=>'VideoObject','name'=>'Trailer de '.$title,'embedUrl'=>$trailer,'thumbnailUrl'=>$poster];
$related=[];
foreach ($movies as $m) {
  if (($m['_slug'] ?? '') === $slug) continue;
  if (($audio && badge($m,'a') === $audio) || ($q && badge($m,'q') === $q)) $related[]=$m;
  if (count($related) >= 8) break;
}
if (count($related) < 8) {
  $total=count($movies);
  for($off=1;$off<20 && count($related)<8;$off++){
    $m=$movies[($index+$off)%$total];
    if (($m['_slug'] ?? '') !== $slug && !in_array($m,$related,true)) $related[]=$m;
  }
}
?><!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title><?= e($title) ?> — Sinopse, Trailer e Download | TorrentFilms</title>
<meta name="description" content="<?= e($desc) ?>">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="<?= e($url) ?>">
<meta property="og:type" content="video.movie">
<meta property="og:title" content="<?= e($title) ?>">
<meta property="og:description" content="<?= e($desc) ?>">
<meta property="og:url" content="<?= e($url) ?>">
<meta property="og:image" content="<?= e($poster) ?>">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="<?= e($title) ?>">
<meta name="twitter:description" content="<?= e($desc) ?>">
<meta name="twitter:image" content="<?= e($poster) ?>">
<script type="application/ld+json"><?= json_encode($ld, JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE) ?></script>
<style>
:root{--bg:#080b13;--panel:#111827;--line:rgba(255,255,255,.1);--txt:#f5f7fb;--mut:#a8b1c2;--brand:#ffc400;--brand2:#ff7a18;--green:#26e07f;--cyan:#22d3ee}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at top,#1a2440,#080b13 55%,#05060a);color:var(--txt);font-family:Arial,system-ui,sans-serif;line-height:1.55}a{color:inherit}.wrap{max-width:1120px;margin:0 auto;padding:22px}.top{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:14px 0 22px}.brand{font-weight:1000;text-transform:uppercase;text-decoration:none;font-size:1.2rem}.brand span{color:var(--brand)}.back{color:var(--brand);text-decoration:none;font-weight:800}.hero{display:grid;grid-template-columns:260px 1fr;gap:26px;background:rgba(255,255,255,.06);border:1px solid var(--line);border-radius:22px;padding:22px;box-shadow:0 20px 48px rgba(0,0,0,.28)}.poster{width:100%;border-radius:16px;box-shadow:0 18px 40px rgba(0,0,0,.45)}.eyebrow{display:inline-block;color:#171000;background:linear-gradient(90deg,var(--brand),var(--brand2));border-radius:999px;padding:5px 10px;font-weight:1000;font-size:.78rem;margin-bottom:10px}h1{font-size:clamp(2rem,4vw,3.6rem);line-height:1;margin:0 0 12px}.desc{color:#d1d7e4;font-size:1.02rem}.badges{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0}.badge{font-size:.78rem;font-weight:1000;padding:7px 10px;border-radius:9px}.q{background:var(--brand);color:#171000}.s{background:rgba(34,211,238,.14);color:#b9f6ff;border:1px solid rgba(34,211,238,.35)}.a{background:var(--green);color:#04140a}.actions{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}.btn{display:inline-block;text-decoration:none;background:linear-gradient(90deg,var(--brand),var(--brand2));color:#171000;font-weight:1000;border-radius:999px;padding:12px 18px}.btn.secondary{background:rgba(255,255,255,.08);color:#fff;border:1px solid var(--line)}.section{margin-top:24px;background:rgba(255,255,255,.045);border:1px solid var(--line);border-radius:20px;padding:20px}.section h2{margin:0 0 10px;font-size:1.25rem}.info-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px}.info-card{background:rgba(0,0,0,.22);border:1px solid var(--line);border-radius:14px;padding:12px}.info-card strong{display:block;color:var(--brand);font-size:.82rem;text-transform:uppercase}.related{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:14px}.rel{text-decoration:none;background:rgba(0,0,0,.22);border:1px solid var(--line);border-radius:14px;overflow:hidden}.rel img{width:100%;aspect-ratio:2/3;object-fit:cover;display:block}.rel span{display:block;padding:9px;font-size:.8rem;font-weight:800}.download-list{display:flex;flex-direction:column;gap:10px}.download-list a{text-decoration:none;background:rgba(255,196,0,.1);border:1px solid rgba(255,196,0,.25);border-radius:12px;padding:12px;color:#ffe37a;font-weight:800}.footer{color:var(--mut);font-size:.8rem;text-align:center;padding:28px 0}@media(max-width:760px){.hero{grid-template-columns:1fr}.poster{max-width:260px;margin:auto}.top{align-items:flex-start;flex-direction:column}}
</style>
</head>
<body><div class="wrap">
<header class="top"><a class="brand" href="/">Torrent<span>Films</span></a><a class="back" href="/">← Voltar ao catálogo</a></header>
<main>
<section class="hero"><div><img class="poster" src="<?= e($poster) ?>" alt="Capa do filme <?= e($title) ?>" fetchpriority="high"></div><div><span class="eyebrow"><?= e($year) ?> • Filme</span><h1><?= e($title) ?></h1><p class="desc"><?= e($desc) ?></p><div class="badges"><?php if($q): ?><span class="badge q"><?= e($q) ?></span><?php endif; ?><?php if($size): ?><span class="badge s"><?= e($size) ?></span><?php endif; ?><?php if($audio): ?><span class="badge a"><?= e($audio) ?></span><?php endif; ?></div><div class="actions"><?php if(!empty($movie['magnets'])): ?><a class="btn" rel="nofollow" href="/start.php?id=<?= e($slug) ?>&link=0">🧲 Baixar</a><?php endif; ?><?php if($trailer): ?><a class="btn secondary" rel="nofollow noopener" target="_blank" href="<?= e($trailer) ?>">▶ Assistir trailer</a><?php endif; ?></div></div></section>
<section class="section"><h2>Informações do filme</h2><div class="info-grid"><div class="info-card"><strong>Título</strong><?= e($name) ?></div><div class="info-card"><strong>Ano</strong><?= e($year) ?></div><div class="info-card"><strong>Qualidade</strong><?= e($q ?: 'Não informado') ?></div><div class="info-card"><strong>Idioma</strong><?= e($audio ?: 'Não informado') ?></div><div class="info-card"><strong>Tamanho</strong><?= e($size ?: 'Não informado') ?></div><div class="info-card"><strong>Publicado</strong><?= e($movie['date'] ?? $year) ?></div></div></section>
<section class="section"><h2>Sinopse de <?= e($name) ?></h2><p><?= e($name) ?> é um lançamento de <?= e($year) ?> disponível no catálogo TorrentFilms. Nesta página você encontra capa, detalhes de qualidade, idioma, trailer quando disponível e opções autorizadas de download. A página foi criada para facilitar a navegação e ajudar você a encontrar rapidamente informações sobre o filme.</p></section>
<section class="section"><h2>Downloads disponíveis</h2><div class="download-list"><?php foreach(($movie['magnets'] ?? []) as $i=>$dl): ?><a rel="nofollow" href="/start.php?id=<?= e($slug) ?>&link=<?= intval($i) ?>">🧲 <?= e(ltrim($dl['label'] ?? 'Download', '🧲 ')) ?></a><?php endforeach; ?></div></section>
<section class="section"><h2>Filmes relacionados</h2><div class="related"><?php foreach($related as $r): ?><a class="rel" href="/filme/<?= e($r['_slug']) ?>/"><img loading="lazy" src="<?= e($r['poster'] ?? '') ?>" alt="Capa de <?= e($r['title'] ?? '') ?>"><span><?= e($r['title'] ?? '') ?></span></a><?php endforeach; ?></div></section>
</main><footer class="footer">TorrentFilms — Catálogo de filmes 2026. Todo conteúdo listado deve ser disponibilizado apenas com autorização dos titulares de direitos.</footer>
</div></body></html>
'''
(OUT/'filme.php').write_text(filme_php,encoding='utf-8')
# sitemap with 417 urls
urls=[DOMAIN]+[DOMAIN+'filme/'+m['_slug']+'/' for m in movies]
sm=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for i,u in enumerate(urls):
    sm += ['  <url>', f'    <loc>{htmlmod.escape(u)}</loc>', f'    <lastmod>{LASTMOD}</lastmod>', f'    <changefreq>{"daily" if i==0 else "weekly"}</changefreq>', f'    <priority>{"1.0" if i==0 else "0.8"}</priority>', '  </url>']
sm += ['</urlset>','']
(OUT/'sitemap.xml').write_text('\n'.join(sm),encoding='utf-8')
(OUT/'robots.txt').write_text(f'''User-agent: *\nAllow: /\nDisallow: /start.php\nDisallow: /download.php\nSitemap: {DOMAIN}sitemap.xml\n''',encoding='utf-8')
# corrected .htaccess with rewrite
htaccess='''Options -Indexes
DirectoryIndex index.html index.php

<Files "links.php">
  Require all denied
</Files>
<Files "config.php">
  Require all denied
</Files>
<Files "movies.php">
  Require all denied
</Files>

<IfModule mod_rewrite.c>
  RewriteEngine On

  RewriteCond %{HTTPS} !=on
  RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

  RewriteCond %{HTTP_HOST} !^torrentfilms\.produtodigital\.org$ [NC]
  RewriteRule ^ https://torrentfilms.produtodigital.org%{REQUEST_URI} [L,R=301]

  RewriteRule ^filme/([A-Za-z0-9-]+)/?$ filme.php?slug=$1 [L,QSA]
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
(OUT/'.htaccess').write_text(htaccess,encoding='utf-8')
# zip
zip_path=Path('/home/user/site_hostinger_filmes_dinamico_corrigido.zip')
if zip_path.exists(): zip_path.unlink()
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
    for f in OUT.rglob('*'):
        if f.is_file(): z.write(f,arcname=str(f.relative_to(OUT)))
print('Pacote:',zip_path,zip_path.stat().st_size)
print('Arquivos:',len([f for f in OUT.rglob('*') if f.is_file()]))
print('URLs sitemap:',len(urls))
