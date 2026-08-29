from pathlib import Path
import re,json,zipfile,html as htmlmod
DOMAIN='https://xtorrents.com.br/'
BASE=Path('/home/user')
h=Path('/home/user/xtorrent_live_utf8.html').read_text(encoding='utf-8')
m=re.search(r'window\.XT_CATALOG=(\[.*?\]);</script>',h,re.S)
if not m: raise SystemExit('XT_CATALOG não encontrado')
items=json.loads(m.group(1))
out=Path('/home/user/correcao_paginas_filmes_xtorrents')
out.mkdir(exist_ok=True)
# movies.php public catalog data
movies_php="""<?php
// Catálogo público usado para gerar as páginas individuais /filme/slug/.
$json = <<<'JSON'
%s
JSON;
return json_decode($json, true);
""" % json.dumps(items,ensure_ascii=False,separators=(',',':'))
(out/'movies.php').write_text(movies_php,encoding='utf-8')
# filme.php robust
filme_php=r'''<?php
$moviesFile = __DIR__ . '/movies.php';
if (!file_exists($moviesFile)) {
  http_response_code(500);
  echo 'Arquivo movies.php não encontrado.';
  exit;
}
$movies = require $moviesFile;
$slug = isset($_GET['slug']) ? preg_replace('/[^a-z0-9\-]/i', '', $_GET['slug']) : '';
$movie = null;
$index = 0;
foreach ($movies as $i => $m) {
  if (($m['slug'] ?? '') === $slug) { $movie = $m; $index = $i; break; }
}
if (!$movie) {
  http_response_code(404);
  echo '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="robots" content="noindex"><title>Filme não encontrado</title><style>body{font-family:Arial;background:#090b10;color:#fff;text-align:center;padding:40px}a{color:#ffc928}</style></head><body><h1>Filme não encontrado</h1><p>Volte ao catálogo e tente novamente.</p><a href="/">Voltar ao catálogo</a></body></html>';
  exit;
}
function e($s){ return htmlspecialchars((string)$s, ENT_QUOTES, 'UTF-8'); }
$title = $movie['title'] ?? 'Título';
$year = $movie['year'] ?? '';
$quality = $movie['quality'] ?? '';
$type = $movie['type'] ?? 'Filme';
$poster = $movie['poster'] ?? '';
$cats = $movie['categories'] ?? [];
$domain = 'https://xtorrents.com.br/';
$url = $domain . 'filme/' . $slug . '/';
$desc = $title . ($year ? ' ('.$year.')' : '') . ' no x-torrents: veja capa, categorias, qualidade, informações e opção de download autorizado em catálogo de filmes e séries torrent.';
$ld = [
  '@context' => 'https://schema.org',
  '@type' => (stripos($type, 'série') !== false || stripos($type, 'serie') !== false || stripos($title, 'temporada') !== false) ? 'TVSeries' : 'Movie',
  'name' => $title,
  'image' => $poster,
  'url' => $url,
  'description' => $desc,
  'datePublished' => $year ?: null,
  'genre' => array_values(array_filter($cats, function($c){ return !preg_match('/^(\d{4}|720p|1080p|2160p|4k|filmes|series|séries)$/i', $c); }))
];
$related = [];
foreach ($movies as $m) {
  if (($m['slug'] ?? '') === $slug) continue;
  $common = array_intersect($cats, $m['categories'] ?? []);
  if (count($common) > 1) $related[] = $m;
  if (count($related) >= 8) break;
}
if (count($related) < 8) {
  $total = count($movies);
  for ($o=1; $o<30 && count($related)<8; $o++) {
    $m = $movies[($index+$o)%$total];
    if (($m['slug'] ?? '') !== $slug && !in_array($m, $related, true)) $related[] = $m;
  }
}
?><!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title><?= e($title) ?><?= $year ? ' ('.e($year).')' : '' ?> — Sinopse e Download | x-torrents</title>
<meta name="description" content="<?= e($desc) ?>">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="<?= e($url) ?>">
<meta property="og:type" content="article">
<meta property="og:title" content="<?= e($title) ?><?= $year ? ' ('.e($year).')' : '' ?> — x-torrents">
<meta property="og:description" content="<?= e($desc) ?>">
<meta property="og:url" content="<?= e($url) ?>">
<meta property="og:image" content="<?= e($poster) ?>">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<script type="application/ld+json"><?= json_encode($ld, JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE) ?></script>
<style>
:root{--bg:#090b10;--panel:#11141b;--panel2:#171b24;--line:#272c38;--text:#f4f5f7;--muted:#9da4b3;--yellow:#ffc928;--orange:#ff8a00;--radius:18px}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at top,rgba(255,201,40,.13),transparent 34%),var(--bg);color:var(--text);font:15px/1.6 Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}a{color:inherit;text-decoration:none}.wrap{max-width:1160px;margin:0 auto;padding:24px}.top{display:flex;justify-content:space-between;gap:18px;align-items:center;margin-bottom:24px}.brand{font-size:24px;font-weight:900}.brand em{font-style:normal;color:var(--yellow)}.back{color:var(--yellow);font-weight:800}.hero{display:grid;grid-template-columns:270px 1fr;gap:28px;background:rgba(255,255,255,.045);border:1px solid var(--line);border-radius:24px;padding:24px;box-shadow:0 20px 48px #0007}.poster{width:100%;border-radius:18px;background:#111;box-shadow:0 18px 40px #0009}.kicker{display:inline-block;color:#111;background:linear-gradient(135deg,var(--yellow),var(--orange));border-radius:999px;padding:6px 11px;font-weight:900;font-size:12px;text-transform:uppercase}h1{font-size:clamp(34px,5vw,60px);line-height:1.02;margin:14px 0}.desc{color:#c7ccd7;font-size:17px}.badges{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0}.badge{background:#202532;border:1px solid var(--line);border-radius:999px;padding:7px 11px;font-weight:800}.badge.q{background:linear-gradient(135deg,var(--yellow),var(--orange));color:#111}.btn{display:inline-flex;margin-top:10px;background:linear-gradient(135deg,var(--yellow),var(--orange));color:#111;font-weight:900;border-radius:999px;padding:13px 18px}.section{margin-top:24px;background:rgba(255,255,255,.04);border:1px solid var(--line);border-radius:22px;padding:22px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(145px,1fr));gap:16px}.card{background:#121720;border:1px solid var(--line);border-radius:16px;overflow:hidden}.card img{width:100%;aspect-ratio:2/3;object-fit:cover;display:block}.card span{display:block;padding:10px;font-weight:800;font-size:13px}.info{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px}.info div{background:#121720;border:1px solid var(--line);border-radius:14px;padding:13px}.info strong{display:block;color:var(--yellow);text-transform:uppercase;font-size:12px}@media(max-width:760px){.hero{grid-template-columns:1fr}.poster{max-width:280px;margin:auto}.top{align-items:flex-start;flex-direction:column}}
</style>
</head>
<body><div class="wrap">
<header class="top"><a class="brand" href="/"><em>x</em>-torrents</a><a class="back" href="/">← Voltar ao catálogo</a></header>
<main>
<section class="hero"><div><img class="poster" src="<?= e($poster) ?>" alt="Capa de <?= e($title) ?>" fetchpriority="high"></div><div><span class="kicker"><?= e($type) ?></span><h1><?= e($title) ?></h1><p class="desc"><?= e($desc) ?></p><div class="badges"><?php if($quality): ?><span class="badge q"><?= e($quality) ?></span><?php endif; ?><?php if($year): ?><span class="badge"><?= e($year) ?></span><?php endif; ?><?php foreach($cats as $c): if(!in_array($c, [$quality,$year,$type])): ?><span class="badge"><?= e($c) ?></span><?php endif; endforeach; ?></div><a class="btn" rel="nofollow" href="/start.php?id=<?= e($slug) ?>&link=0">Abrir download autorizado →</a></div></section>
<section class="section"><h2>Informações</h2><div class="info"><div><strong>Título</strong><?= e($title) ?></div><div><strong>Ano</strong><?= e($year ?: 'Não informado') ?></div><div><strong>Qualidade</strong><?= e($quality ?: 'Não informado') ?></div><div><strong>Tipo</strong><?= e($type) ?></div></div></section>
<section class="section"><h2>Sinopse e informações de <?= e($title) ?></h2><p>Consulte informações sobre <strong><?= e($title) ?></strong> nesta página do catálogo x-torrents. Os dados são organizados para facilitar a descoberta do título, sua qualidade, ano, categorias relacionadas e acesso autorizado ao download.</p></section>
<section class="section"><h2>Você também pode gostar</h2><div class="grid"><?php foreach($related as $r): ?><a class="card" href="/filme/<?= e($r['slug'] ?? '') ?>/"><img loading="lazy" src="<?= e($r['poster'] ?? '') ?>" alt="Capa de <?= e($r['title'] ?? '') ?>"><span><?= e($r['title'] ?? '') ?></span></a><?php endforeach; ?></div></section>
</main></div></body></html>
'''
(out/'filme.php').write_text(filme_php,encoding='utf-8')
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

  RewriteCond %{HTTP_HOST} !^xtorrents\.com\.br$ [NC]
  RewriteRule ^ https://xtorrents.com.br%{REQUEST_URI} [L,R=301]

  RewriteRule ^filme/([A-Za-z0-9-]+)/?$ filme.php?slug=$1 [L,QSA]
</IfModule>

<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/plain text/css text/javascript application/javascript application/json application/xml image/svg+xml
</IfModule>

<IfModule mod_headers.c>
  Header set X-Content-Type-Options "nosniff"
  Header set Referrer-Policy "strict-origin-when-cross-origin"
</IfModule>
'''
(out/'.htaccess').write_text(htaccess,encoding='utf-8')
(out/'LEIA-ME-CORRECAO.txt').write_text('''# Correção das páginas /filme/ no domínio xtorrents.com.br

O erro "Esta página não existe" acontecia porque o pacote de migração enviado anteriormente continha index.html/sitemap/robots/.htaccess, mas não continha os arquivos dinâmicos responsáveis por abrir as páginas individuais:

- filme.php
- movies.php

Envie estes três arquivos para a raiz do public_html:

- filme.php
- movies.php
- .htaccess

Depois teste:
https://xtorrents.com.br/filme/ghost-in-the-cell/

Se ainda der 404, confira se o arquivo .htaccess foi enviado com o ponto inicial e se está na mesma pasta do index.html.
''',encoding='utf-8')
zip_path=Path('/home/user/correcao_paginas_filmes_xtorrents.zip')
if zip_path.exists(): zip_path.unlink()
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
    for f in out.iterdir(): z.write(f,arcname=f.name)
print(zip_path, zip_path.stat().st_size)
