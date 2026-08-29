import json, re, html as htmlmod, zipfile, shutil
from pathlib import Path
from datetime import date

DOMAIN='https://torrentfilms.produtodigital.org/'
LASTMOD='2026-08-22'
UPLOAD=Path('/home/user/hostinger_encurta_unico_upload')
INDEX=UPLOAD/'index.html'
if not INDEX.exists():
    raise SystemExit('index.html do pacote não encontrado')
html=INDEX.read_text(encoding='utf-8')
pos=html.find('const MOVIES = ')+len('const MOVIES = ')
end=html.find('];',pos)+1
movies=json.loads(html[pos:end])

def esc(s): return htmlmod.escape(str(s or ''), quote=True)
def clean_year(title):
    m=re.search(r'\((\d{4})\)', title or '')
    return m.group(1) if m else '2026'
def strip_year(title):
    return re.sub(r'\s*\(\d{4}\)\s*$', '', title or '').strip()
def badge(m, kind):
    return next((b[1] for b in m.get('badges',[]) if b[0]==kind), '')
def summary(m):
    title=m['title']; q=badge(m,'q'); a=badge(m,'a'); s=badge(m,'s')
    parts=[]
    if q: parts.append(q)
    if a: parts.append(a)
    if s: parts.append(s)
    details=', '.join(parts)
    return f"Confira {title} no TorrentFilms com capa, trailer, informações de qualidade{(' ('+details+')') if details else ''} e opção autorizada de download."
def page_url(slug): return DOMAIN+'filme/'+slug+'/'
def download_url(slug, i=0): return '../../start.php?id='+slug+'&link='+str(i)
def abs_download_url(slug, i=0): return DOMAIN+'start.php?id='+slug+'&link='+str(i)

# Add visible link to details in index cards
if 'Ver detalhes</a>' not in html:
    html=html.replace("'<div class=\"info\"><h2 itemprop=\"name\">' + esc(m.title) + '</h2>' +",
                      "'<div class=\"info\"><h2 itemprop=\"name\"><a href=\"filme/' + esc(m._slug) + '/\">' + esc(m.title) + '</a></h2>' +", 1)
    html=html.replace("'<div class=\"actions\"><a class=\"btn magnet\" rel=\"nofollow\" href=\"' + magnetHref + '\" aria-label=\"Baixar ' + esc(m.title) + '\">🧲 Baixar</a>' + extra + trailer + '</div>' +",
                      "'<div class=\"actions\"><a class=\"btn magnet\" rel=\"nofollow\" href=\"' + magnetHref + '\" aria-label=\"Baixar ' + esc(m.title) + '\">🧲 Baixar</a><a class=\"trailer\" href=\"filme/' + esc(m._slug) + '/\">Ver detalhes</a>' + extra + trailer + '</div>' +", 1)
    # make h2 link inherit style
    if '.info h2 a{' not in html:
        html=html.replace('.info h2{', '.info h2 a{color:inherit;text-decoration:none}.info h2 a:hover{color:var(--brand)}.info h2{', 1)
    INDEX.write_text(html,encoding='utf-8')

film_root=UPLOAD/'filme'
if film_root.exists():
    shutil.rmtree(film_root)
film_root.mkdir(parents=True,exist_ok=True)

base_css='''
:root{--bg:#080b13;--panel:#111827;--line:rgba(255,255,255,.1);--txt:#f5f7fb;--mut:#a8b1c2;--brand:#ffc400;--brand2:#ff7a18;--green:#26e07f;--cyan:#22d3ee}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at top,#1a2440,#080b13 55%,#05060a);color:var(--txt);font-family:Arial,system-ui,sans-serif;line-height:1.55}a{color:inherit}.wrap{max-width:1120px;margin:0 auto;padding:22px}.top{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:14px 0 22px}.brand{font-weight:1000;text-transform:uppercase;text-decoration:none;font-size:1.2rem}.brand span{color:var(--brand)}.back{color:var(--brand);text-decoration:none;font-weight:800}.hero{display:grid;grid-template-columns:260px 1fr;gap:26px;background:rgba(255,255,255,.06);border:1px solid var(--line);border-radius:22px;padding:22px;box-shadow:0 20px 48px rgba(0,0,0,.28)}.poster{width:100%;border-radius:16px;box-shadow:0 18px 40px rgba(0,0,0,.45)}.eyebrow{display:inline-block;color:#171000;background:linear-gradient(90deg,var(--brand),var(--brand2));border-radius:999px;padding:5px 10px;font-weight:1000;font-size:.78rem;margin-bottom:10px}h1{font-size:clamp(2rem,4vw,3.6rem);line-height:1;margin:0 0 12px}.desc{color:#d1d7e4;font-size:1.02rem}.badges{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0}.badge{font-size:.78rem;font-weight:1000;padding:7px 10px;border-radius:9px}.q{background:var(--brand);color:#171000}.s{background:rgba(34,211,238,.14);color:#b9f6ff;border:1px solid rgba(34,211,238,.35)}.a{background:var(--green);color:#04140a}.actions{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}.btn{display:inline-block;text-decoration:none;background:linear-gradient(90deg,var(--brand),var(--brand2));color:#171000;font-weight:1000;border-radius:999px;padding:12px 18px}.btn.secondary{background:rgba(255,255,255,.08);color:#fff;border:1px solid var(--line)}.section{margin-top:24px;background:rgba(255,255,255,.045);border:1px solid var(--line);border-radius:20px;padding:20px}.section h2{margin:0 0 10px;font-size:1.25rem}.info-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px}.info-card{background:rgba(0,0,0,.22);border:1px solid var(--line);border-radius:14px;padding:12px}.info-card strong{display:block;color:var(--brand);font-size:.82rem;text-transform:uppercase}.related{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:14px}.rel{text-decoration:none;background:rgba(0,0,0,.22);border:1px solid var(--line);border-radius:14px;overflow:hidden}.rel img{width:100%;aspect-ratio:2/3;object-fit:cover;display:block}.rel span{display:block;padding:9px;font-size:.8rem;font-weight:800}.download-list{display:flex;flex-direction:column;gap:10px}.download-list a{text-decoration:none;background:rgba(255,196,0,.1);border:1px solid rgba(255,196,0,.25);border-radius:12px;padding:12px;color:#ffe37a;font-weight:800}.footer{color:var(--mut);font-size:.8rem;text-align:center;padding:28px 0}@media(max-width:760px){.hero{grid-template-columns:1fr}.poster{max-width:260px;margin:auto}.top{align-items:flex-start;flex-direction:column}}
'''.strip()

for idx,m in enumerate(movies):
    slug=m['_slug']; title=m['title']; year=clean_year(title); name=strip_year(title)
    q=badge(m,'q'); a=badge(m,'a'); s=badge(m,'s')
    desc=summary(m)
    trailer=next((o.get('url') for o in m.get('other',[]) if 'youtube' in o.get('url','') or 'youtu.be' in o.get('url','')), '')
    related=[]
    # related by audio/quality, fallback neighbors
    for other in movies:
        if other['_slug']==slug: continue
        if (a and badge(other,'a')==a) or (q and badge(other,'q')==q):
            related.append(other)
        if len(related)>=8: break
    if len(related)<8:
        for off in range(1,12):
            other=movies[(idx+off)%len(movies)]
            if other['_slug']!=slug and other not in related: related.append(other)
            if len(related)>=8: break
    ld={
        '@context':'https://schema.org','@type':'Movie','name':title,'image':m.get('poster'),
        'url':page_url(slug),'datePublished':m.get('date') or year,'description':desc,
        'inLanguage': a or 'pt-BR'
    }
    if trailer:
        ld['trailer']={'@type':'VideoObject','name':'Trailer de '+title,'embedUrl':trailer,'thumbnailUrl':m.get('poster')}
    downloads=''.join(f'<a rel="nofollow" href="{esc(download_url(slug,i))}">🧲 {esc(dl.get("label","Download").lstrip("🧲 "))}</a>' for i,dl in enumerate(m.get('magnets',[])))
    rel_html=''.join(f'<a class="rel" href="../{esc(r["_slug"])}/"><img loading="lazy" src="{esc(r.get("poster"))}" alt="Capa de {esc(r.get("title"))}"><span>{esc(r.get("title"))}</span></a>' for r in related)
    page=f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} — Sinopse, Trailer e Download | TorrentFilms</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{esc(page_url(slug))}">
<meta property="og:type" content="video.movie">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{esc(page_url(slug))}">
<meta property="og:image" content="{esc(m.get('poster'))}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{esc(m.get('poster'))}">
<script type="application/ld+json">{json.dumps(ld,ensure_ascii=False,separators=(',',':'))}</script>
<style>{base_css}</style>
</head>
<body>
<div class="wrap">
<header class="top"><a class="brand" href="../../">Torrent<span>Films</span></a><a class="back" href="../../">← Voltar ao catálogo</a></header>
<main>
<section class="hero">
  <div><img class="poster" src="{esc(m.get('poster'))}" alt="Capa do filme {esc(title)}" fetchpriority="high"></div>
  <div>
    <span class="eyebrow">{esc(year)} • Filme</span>
    <h1>{esc(title)}</h1>
    <p class="desc">{esc(desc)}</p>
    <div class="badges">{''.join([f'<span class="badge q">{esc(q)}</span>' if q else '', f'<span class="badge s">{esc(s)}</span>' if s else '', f'<span class="badge a">{esc(a)}</span>' if a else ''])}</div>
    <div class="actions">
      {f'<a class="btn" rel="nofollow" href="{esc(download_url(slug,0))}">🧲 Baixar</a>' if m.get('magnets') else ''}
      {f'<a class="btn secondary" rel="nofollow noopener" target="_blank" href="{esc(trailer)}">▶ Assistir trailer</a>' if trailer else ''}
    </div>
  </div>
</section>
<section class="section"><h2>Informações do filme</h2><div class="info-grid">
  <div class="info-card"><strong>Título</strong>{esc(name)}</div>
  <div class="info-card"><strong>Ano</strong>{esc(year)}</div>
  <div class="info-card"><strong>Qualidade</strong>{esc(q or 'Não informado')}</div>
  <div class="info-card"><strong>Idioma</strong>{esc(a or 'Não informado')}</div>
  <div class="info-card"><strong>Tamanho</strong>{esc(s or 'Não informado')}</div>
  <div class="info-card"><strong>Publicado</strong>{esc(m.get('date') or year)}</div>
</div></section>
<section class="section"><h2>Sinopse de {esc(name)}</h2><p>{esc(name)} é um lançamento de {esc(year)} disponível no catálogo TorrentFilms. Nesta página você encontra capa, detalhes de qualidade, idioma, trailer quando disponível e opções autorizadas de download. A página foi criada para facilitar a navegação e ajudar você a encontrar rapidamente informações sobre o filme.</p></section>
<section class="section"><h2>Downloads disponíveis</h2><div class="download-list">{downloads or '<p>Nenhum link disponível no momento.</p>'}</div></section>
<section class="section"><h2>Filmes relacionados</h2><div class="related">{rel_html}</div></section>
</main>
<footer class="footer">TorrentFilms — Catálogo de filmes 2026. Todo conteúdo listado deve ser disponibilizado apenas com autorização dos titulares de direitos.</footer>
</div>
</body>
</html>'''
    d=film_root/slug
    d.mkdir(parents=True,exist_ok=True)
    (d/'index.html').write_text(page,encoding='utf-8')

# sitemap direct with all URLs
urls=[('https://torrentfilms.produtodigital.org/','daily','1.0')]
for m in movies:
    urls.append((page_url(m['_slug']),'weekly','0.8'))
sitemap=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for loc,cf,prio in urls:
    sitemap += ['  <url>', f'    <loc>{esc(loc)}</loc>', f'    <lastmod>{LASTMOD}</lastmod>', f'    <changefreq>{cf}</changefreq>', f'    <priority>{prio}</priority>', '  </url>']
sitemap += ['</urlset>','']
(UPLOAD/'sitemap.xml').write_text('\n'.join(sitemap),encoding='utf-8')
(UPLOAD/'robots.txt').write_text(f'''User-agent: *\nAllow: /\nDisallow: /start.php\nDisallow: /download.php\nSitemap: {DOMAIN}sitemap.xml\n''',encoding='utf-8')

zip_path=Path('/home/user/site_hostinger_paginas_filmes_seo.zip')
if zip_path.exists(): zip_path.unlink()
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
    for f in UPLOAD.rglob('*'):
        if f.is_file():
            z.write(f,arcname=str(f.relative_to(UPLOAD)))
print('Páginas criadas:', len(movies))
print('Sitemap URLs:', len(urls))
print('ZIP:', zip_path, zip_path.stat().st_size)
