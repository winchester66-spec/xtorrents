from pathlib import Path
from bs4 import BeautifulSoup
import json, re, unicodedata, zipfile, html as htmlmod

DOMAIN='https://xtorrents.com.br/'
DESC_HOME='Baixando Filmes Torrent - Baixa Filmes - Séries Torrent - O Melhor Site De Filmes Via Torrent e Lançamentos De Filmes e Séries em 1080p, 720p 4K.'
TITLE_HOME='x-torrents - Filmes Torrent - Séries Torrent - Downloads Grátis'

# Current index from live bytes, decode as UTF-8 despite server header
home_bytes=Path('/home/user/current_xtorrents_home.html').read_bytes()
index_html=home_bytes.decode('utf-8','replace')
# Extract current catalog
m=re.search(r'window\.XT_CATALOG=(\[.*?\]);</script>', index_html, re.S)
if not m:
    raise SystemExit('Não encontrei window.XT_CATALOG no index atual')
items=json.loads(m.group(1))

# Source draft from Netlify with complete descriptions
src_bytes=Path('/home/user/current_sage.html').read_bytes()
src_html=src_bytes.decode('utf-8','replace')
soup=BeautifulSoup(src_html,'html.parser')

def norm(t):
    t=re.sub(r'\s*\(\d{4}\)','',str(t or ''))
    t=unicodedata.normalize('NFKD',t).encode('ascii','ignore').decode('ascii').lower()
    return re.sub(r'[^a-z0-9]+',' ',t).strip()

def slug_from_url(url):
    seg=url.rstrip('/').split('/')[-1]
    seg=re.sub(r'-(?:19|20)\d{2}(?:-a-20\d{2})?$', '', seg)
    seg=re.sub(r'^(baixar-|download-)','',seg)
    return seg

def clean_desc(desc):
    desc=' '.join(str(desc or '').split())
    # keep source text, only fix missing spaces in common malformed titles
    desc=desc.replace('Download –', 'Download – ')
    return desc

by_slug={}
by_title={}
for art in soup.select('article.card'):
    summ=art.select_one('p.summary')
    if not summ: continue
    desc=clean_desc(summ.get_text(' ',strip=True))
    if not desc: continue
    href=None
    for a in art.find_all('a',href=True):
        if 'baixetorrents.net' in a['href'] and not a['href'].startswith('magnet:'):
            href=a['href']
    if href:
        by_slug[slug_from_url(href)]=desc
    if ' Torrent ' in desc:
        title=desc.split(' Torrent ')[0].strip()
        if title: by_title[norm(title)]=desc

matched=0
for it in items:
    slug=it.get('slug','')
    desc=by_slug.get(slug) or by_slug.get(re.sub(r'-\d+$','',slug)) or by_title.get(norm(it.get('title','')))
    if desc:
        it['description']=desc
        matched+=1
    else:
        it['description']=f"{it.get('title','Este título')} está disponível no catálogo x-torrents com informações de ano, qualidade, categorias e opção de download autorizado."

# Patch index HTML catalog data
start=m.start(1); end=m.end(1)
index_html=index_html[:start]+json.dumps(items,ensure_ascii=False,separators=(',',':'))+index_html[end:]

# SEO text/head clean
index_html=re.sub(r'<title>.*?</title>', f'<title>{TITLE_HOME}</title>', index_html, count=1, flags=re.S)
index_html=re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC_HOME}">', index_html, count=1)
index_html=re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{TITLE_HOME}">', index_html, count=1)
index_html=re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{DESC_HOME}">', index_html, count=1)
index_html=index_html.replace('https://xtorrent.produtodigital.org/','https://xtorrents.com.br/')
index_html=index_html.replace('SEU PRÓXIMO TÍTULO ESTÁ AQUI','FILMES TORRENT E SÉRIES TORRENT')
index_html=index_html.replace('<h1>Filmes e séries,<br><em>sem perder tempo.</em></h1>', '<h1>Filmes Torrent,<br><em>Séries Torrent e Downloads Grátis.</em></h1>')
index_html=index_html.replace('Explore um catálogo amplo com busca inteligente, filtros rápidos e páginas próprias para cada título.', DESC_HOME)
# Add CSS for summaries in cards
if '.card-summary' not in index_html:
    index_html=index_html.replace('.card-copy p{margin:0;color:var(--muted);font-size:12px}', '.card-copy p{margin:0;color:var(--muted);font-size:12px}.card-summary{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;margin-top:6px!important;color:#b8bfcd!important;font-size:12px!important;line-height:1.35}', 1)
# Patch JS card + search to use description
old_card=re.search(r'function card\(m\)\{return `.*?`\}function render', index_html, re.S)
if old_card:
    new_card="""function card(m){const d=(m.description||'').replace(/\s+/g,' ').slice(0,150);return `<a class=\"card\" href=\"/filme/${encodeURIComponent(m.slug)}/\"><div class=\"cover\"><img loading=\"lazy\" decoding=\"async\" src=\"${esc(m.poster)}\" alt=\"Capa de ${esc(m.title)}\"><span>${esc(m.quality||m.type)}</span></div><div class=\"card-copy\"><h3>${esc(m.title)}</h3><p>${esc(m.year||m.type)}</p><p class=\"card-summary\">${esc(d)}</p></div></a>`}function render"""
    index_html=index_html[:old_card.start()]+new_card+index_html[old_card.end():]
index_html=index_html.replace("norm(m.title+' '+m.categories.join(' ')+' '+m.year).includes(n)", "norm(m.title+' '+(m.description||'')+' '+m.categories.join(' ')+' '+m.year).includes(n)")

# movies.php with descriptions
movies_php="""<?php
// Catálogo público do x-torrents com descrições completas importadas do rascunho Netlify.
$json = <<<'JSON'
%s
JSON;
return json_decode($json, true);
""" % json.dumps(items,ensure_ascii=False,separators=(',',':'))

# Dynamic filme.php using description
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
function cleanText($s){ return trim(preg_replace('/\s+/', ' ', (string)$s)); }
$title = $movie['title'] ?? 'Título';
$year = $movie['year'] ?? '';
$quality = $movie['quality'] ?? '';
$type = $movie['type'] ?? 'Filme';
$poster = $movie['poster'] ?? '';
$cats = $movie['categories'] ?? [];
$domain = 'https://xtorrents.com.br/';
$url = $domain . 'filme/' . $slug . '/';
$fullDesc = cleanText($movie['description'] ?? '');
if (!$fullDesc) {
  $fullDesc = $title . ($year ? ' ('.$year.')' : '') . ' no x-torrents: veja capa, categorias, qualidade, informações e opção de download autorizado em catálogo de filmes e séries torrent.';
}
$metaDesc = mb_substr($fullDesc, 0, 155, 'UTF-8');
if (mb_strlen($fullDesc, 'UTF-8') > 155) $metaDesc .= '...';
$schemaType = (stripos($type, 'série') !== false || stripos($type, 'serie') !== false || stripos($title, 'temporada') !== false) ? 'TVSeries' : 'Movie';
$genre = array_values(array_filter($cats, function($c){ return !preg_match('/^(\d{4}|720p|1080p|2160p|4k|filmes|series|séries)$/i', $c); }));
$ld = ['@context'=>'https://schema.org','@type'=>$schemaType,'name'=>$title,'image'=>$poster,'url'=>$url,'description'=>$fullDesc,'datePublished'=>$year ?: null,'genre'=>$genre];
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
<meta name="description" content="<?= e($metaDesc) ?>">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="<?= e($url) ?>">
<meta property="og:type" content="article">
<meta property="og:title" content="<?= e($title) ?><?= $year ? ' ('.e($year).')' : '' ?> — x-torrents">
<meta property="og:description" content="<?= e($metaDesc) ?>">
<meta property="og:url" content="<?= e($url) ?>">
<meta property="og:image" content="<?= e($poster) ?>">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<script type="application/ld+json"><?= json_encode($ld, JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE) ?></script>
<style>
:root{--bg:#090b10;--panel:#11141b;--panel2:#171b24;--line:#272c38;--text:#f4f5f7;--muted:#9da4b3;--yellow:#ffc928;--orange:#ff8a00;--radius:18px}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at top,rgba(255,201,40,.13),transparent 34%),var(--bg);color:var(--text);font:15px/1.6 Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}a{color:inherit;text-decoration:none}.wrap{max-width:1160px;margin:0 auto;padding:24px}.top{display:flex;justify-content:space-between;gap:18px;align-items:center;margin-bottom:24px}.brand{font-size:24px;font-weight:900}.brand em{font-style:normal;color:var(--yellow)}.back{color:var(--yellow);font-weight:800}.hero{display:grid;grid-template-columns:270px 1fr;gap:28px;background:rgba(255,255,255,.045);border:1px solid var(--line);border-radius:24px;padding:24px;box-shadow:0 20px 48px #0007}.poster{width:100%;border-radius:18px;background:#111;box-shadow:0 18px 40px #0009}.kicker{display:inline-block;color:#111;background:linear-gradient(135deg,var(--yellow),var(--orange));border-radius:999px;padding:6px 11px;font-weight:900;font-size:12px;text-transform:uppercase}h1{font-size:clamp(34px,5vw,60px);line-height:1.02;margin:14px 0}.desc{color:#d8dde8;font-size:17px}.badges{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0}.badge{background:#202532;border:1px solid var(--line);border-radius:999px;padding:7px 11px;font-weight:800}.badge.q{background:linear-gradient(135deg,var(--yellow),var(--orange));color:#111}.btn{display:inline-flex;margin-top:10px;background:linear-gradient(135deg,var(--yellow),var(--orange));color:#111;font-weight:900;border-radius:999px;padding:13px 18px}.section{margin-top:24px;background:rgba(255,255,255,.04);border:1px solid var(--line);border-radius:22px;padding:22px}.section p{color:#d8dde8}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(145px,1fr));gap:16px}.card{background:#121720;border:1px solid var(--line);border-radius:16px;overflow:hidden}.card img{width:100%;aspect-ratio:2/3;object-fit:cover;display:block}.card span{display:block;padding:10px;font-weight:800;font-size:13px}.info{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px}.info div{background:#121720;border:1px solid var(--line);border-radius:14px;padding:13px}.info strong{display:block;color:var(--yellow);text-transform:uppercase;font-size:12px}@media(max-width:760px){.hero{grid-template-columns:1fr}.poster{max-width:280px;margin:auto}.top{align-items:flex-start;flex-direction:column}}
</style>
</head>
<body><div class="wrap">
<header class="top"><a class="brand" href="/"><em>x</em>-torrents</a><a class="back" href="/">← Voltar ao catálogo</a></header>
<main>
<section class="hero"><div><img class="poster" src="<?= e($poster) ?>" alt="Capa de <?= e($title) ?>" fetchpriority="high"></div><div><span class="kicker"><?= e($type) ?></span><h1><?= e($title) ?></h1><p class="desc"><?= e($fullDesc) ?></p><div class="badges"><?php if($quality): ?><span class="badge q"><?= e($quality) ?></span><?php endif; ?><?php if($year): ?><span class="badge"><?= e($year) ?></span><?php endif; ?><?php foreach($cats as $c): if(!in_array($c, [$quality,$year,$type])): ?><span class="badge"><?= e($c) ?></span><?php endif; endforeach; ?></div><a class="btn" rel="nofollow" href="/start.php?id=<?= e($slug) ?>&link=0">Abrir download autorizado →</a></div></section>
<section class="section"><h2>Informações</h2><div class="info"><div><strong>Título</strong><?= e($title) ?></div><div><strong>Ano</strong><?= e($year ?: 'Não informado') ?></div><div><strong>Qualidade</strong><?= e($quality ?: 'Não informado') ?></div><div><strong>Tipo</strong><?= e($type) ?></div></div></section>
<section class="section"><h2>Sinopse completa de <?= e($title) ?></h2><p><?= e($fullDesc) ?></p></section>
<section class="section"><h2>Você também pode gostar</h2><div class="grid"><?php foreach($related as $r): ?><a class="card" href="/filme/<?= e($r['slug'] ?? '') ?>/"><img loading="lazy" src="<?= e($r['poster'] ?? '') ?>" alt="Capa de <?= e($r['title'] ?? '') ?>"><span><?= e($r['title'] ?? '') ?></span></a><?php endforeach; ?></div></section>
</main></div></body></html>
'''

# htaccess snippet for charset (do not overwrite routing, but include suggested full file)
htaccess_sugerido='''Options -Indexes
DirectoryIndex index.html index.php
AddDefaultCharset UTF-8

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

<IfModule mod_headers.c>
  Header set X-Content-Type-Options "nosniff"
  Header set Referrer-Policy "strict-origin-when-cross-origin"
</IfModule>
'''

out=Path('/home/user/patch_descricoes_xtorrents')
out.mkdir(exist_ok=True)
(out/'index.html').write_text(index_html,encoding='utf-8')
(out/'movies.php').write_text(movies_php,encoding='utf-8')
(out/'filme.php').write_text(filme_php,encoding='utf-8')
(out/'htaccess_sugerido.txt').write_text(htaccess_sugerido,encoding='utf-8')
(out/'LEIA-ME.txt').write_text(f'''# Patch de descrições completas — x-torrents

Foram importadas descrições do rascunho:
https://sage-semolina-16fcfe.netlify.app/

Resultado:
- Títulos no catálogo: {len(items)}
- Descrições correspondidas diretamente/fallback: {matched}
- Arquivos principais: index.html, movies.php, filme.php

O que subir:
1. Envie `index.html`, `movies.php` e `filme.php` para a raiz do public_html, substituindo os atuais.
2. Não substitua `links.php`, `start.php`, `iniciar.php`, `download.php` ou `config.php` se já estão funcionando.
3. Se ainda houver textos quebrados com Ã©/Ã¡, copie a linha `AddDefaultCharset UTF-8` do arquivo htaccess_sugerido.txt para seu `.htaccess`.

Depois teste:
https://xtorrents.com.br/filme/ghost-in-the-cell/

A página deve mostrar a descrição real:
"Ghost in the Cell Torrent Dual Áudio Download – Uma prisão notória..."
''',encoding='utf-8')
zip_path=Path('/home/user/patch_descricoes_completas_xtorrents.zip')
if zip_path.exists(): zip_path.unlink()
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
    for f in out.iterdir(): z.write(f,arcname=f.name)
print('Itens:',len(items))
print('Descrições encontradas:',matched)
print('ZIP:',zip_path,zip_path.stat().st_size)
print('Ghost desc:', next(it['description'] for it in items if it['slug']=='ghost-in-the-cell')[:200])
