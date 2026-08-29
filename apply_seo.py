import json, re, unicodedata, html as htmlmod
from pathlib import Path

src = Path('/home/user/index_corrigido_final.html')
out = Path('/home/user/index_seo_profissional.html')
html = src.read_text(encoding='utf-8')
base_url = 'https://grand-gingersnap-c926b6.netlify.app/'
site_name = 'Filmes 2026'
seo_title = 'Filmes 2026: Lançamentos, Trailers e Downloads Oficiais'
desc = 'Catálogo atualizado de filmes 2026 com capas, qualidade, idioma, trailers e links oficiais de download autorizados. Encontre lançamentos em 1080p, dublado, dual áudio e legendado.'

# Parse MOVIES array
pos = html.find('const MOVIES = ') + len('const MOVIES = ')
end = html.find('];', pos) + 1
movies = json.loads(html[pos:end])

def slugify(s):
    s = re.sub(r'\(\d{4}\)', '', s).strip().lower()
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return s or 'filme'

# Ensure unique slugs
seen = {}
for m in movies:
    base = slugify(m['title'])
    n = seen.get(base, 0)
    seen[base] = n + 1
    m['_slug'] = base if n == 0 else f'{base}-{n+1}'

# JSON-LD graph: WebSite + WebPage + Breadcrumb + ItemList with Movie entries
item_list = []
for i, m in enumerate(movies, 1):
    quality = next((b[1] for b in m.get('badges', []) if b[0] == 'q'), None)
    size = next((b[1] for b in m.get('badges', []) if b[0] == 's'), None)
    language = next((b[1] for b in m.get('badges', []) if b[0] == 'a'), None)
    movie_obj = {
        '@type': 'Movie',
        '@id': base_url + '#' + m['_slug'],
        'url': base_url + '#' + m['_slug'],
        'name': m['title'],
        'image': m['poster'],
        'datePublished': m.get('date') or '2026',
    }
    if language:
        movie_obj['inLanguage'] = language
    if quality or size:
        movie_obj['description'] = 'Filme {} disponível{}{}.'.format(
            m['title'],
            f' em {quality}' if quality else '',
            f' com arquivo de {size}' if size else ''
        )
    if m.get('other'):
        yt = next((o['url'] for o in m['other'] if 'youtube.com' in o.get('url','') or 'youtu.be' in o.get('url','')), None)
        if yt:
            movie_obj['trailer'] = {'@type': 'VideoObject', 'name': 'Trailer de ' + m['title'], 'embedUrl': yt}
    item_list.append({'@type': 'ListItem', 'position': i, 'url': base_url + '#' + m['_slug'], 'item': movie_obj})

ld = {
    '@context': 'https://schema.org',
    '@graph': [
        {
            '@type': 'WebSite',
            '@id': base_url + '#website',
            'url': base_url,
            'name': site_name,
            'inLanguage': 'pt-BR',
            'description': desc,
            'potentialAction': {
                '@type': 'SearchAction',
                'target': base_url + '?q={search_term_string}',
                'query-input': 'required name=search_term_string'
            }
        },
        {
            '@type': 'CollectionPage',
            '@id': base_url + '#webpage',
            'url': base_url,
            'name': seo_title,
            'isPartOf': {'@id': base_url + '#website'},
            'inLanguage': 'pt-BR',
            'description': desc,
            'primaryImageOfPage': movies[0]['poster'],
            'dateModified': '2026-08-22'
        },
        {
            '@type': 'BreadcrumbList',
            '@id': base_url + '#breadcrumb',
            'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': 'Início', 'item': base_url},
                {'@type': 'ListItem', 'position': 2, 'name': 'Filmes 2026', 'item': base_url}
            ]
        },
        {
            '@type': 'ItemList',
            '@id': base_url + '#filmes-2026',
            'name': 'Lista de filmes 2026',
            'numberOfItems': len(movies),
            'itemListOrder': 'https://schema.org/ItemListOrderDescending',
            'itemListElement': item_list
        }
    ]
}
ld_script = '<script type="application/ld+json">\n' + json.dumps(ld, ensure_ascii=False, separators=(',', ':')) + '\n</script>\n'

# Replace title and inject meta tags
html = re.sub(r'<title>.*?</title>', f'<title>{htmlmod.escape(seo_title)}</title>', html, count=1, flags=re.S)
meta_block = f'''<meta name="description" content="{htmlmod.escape(desc)}">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
<meta name="googlebot" content="index, follow, max-image-preview:large">
<meta name="author" content="{htmlmod.escape(site_name)}">
<meta name="theme-color" content="#0e1117">
<meta name="language" content="pt-BR">
<meta name="keywords" content="filmes 2026, lançamentos 2026, filmes dublados, filmes dual áudio, filmes legendados, trailers de filmes, downloads oficiais">
<link rel="canonical" href="{base_url}">
<link rel="sitemap" type="application/xml" href="/sitemap.xml">
<meta property="og:locale" content="pt_BR">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{htmlmod.escape(site_name)}">
<meta property="og:title" content="{htmlmod.escape(seo_title)}">
<meta property="og:description" content="{htmlmod.escape(desc)}">
<meta property="og:url" content="{base_url}">
<meta property="og:image" content="{movies[0]['poster']}">
<meta property="og:image:alt" content="{htmlmod.escape(movies[0]['title'])}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{htmlmod.escape(seo_title)}">
<meta name="twitter:description" content="{htmlmod.escape(desc)}">
<meta name="twitter:image" content="{movies[0]['poster']}">
{ld_script}'''
# Insert before style if not already present
html = html.replace('<style>', meta_block + '<style>', 1)

# CSS improvements
html = html.replace('.info h3{font-size:.84rem;line-height:1.25;font-weight:600;min-height:2.4em}', '.info h2{font-size:.84rem;line-height:1.25;font-weight:600;min-height:2.4em}.seo-intro{background:linear-gradient(135deg,rgba(59,130,246,.12),rgba(34,211,238,.07));border:1px solid var(--border);border-radius:16px;padding:18px 20px;margin:0 0 20px}.seo-intro h2{font-size:1.1rem;margin-bottom:8px;color:var(--txt)}.seo-intro p{color:var(--mut);font-size:.92rem;line-height:1.55}.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}')

# Header H1 and form aria
html = html.replace('<h1>Filmes Torrent 2026</h1>', '<h1>Filmes 2026: Lançamentos e Downloads Oficiais</h1>', 1)
html = html.replace('<input id="q" type="search" placeholder="Buscar filme..." autocomplete="off">', '<input id="q" type="search" name="q" placeholder="Buscar filme..." autocomplete="off" aria-label="Buscar filme por título">', 1)
html = html.replace('<select id="audio">', '<select id="audio" aria-label="Filtrar por idioma ou áudio">', 1)
html = html.replace('<main>\n  <div class="grid" id="grid"></div>', '''<main>
  <section class="seo-intro" aria-labelledby="intro-title">
    <h2 id="intro-title">Catálogo atualizado de filmes 2026</h2>
    <p>Veja lançamentos de filmes 2026 com capa, data de publicação, qualidade, idioma, trailers e opções oficiais de download autorizadas. Use a busca para encontrar rapidamente filmes dublados, dual áudio, legendados e em alta definição.</p>
  </section>
  <div class="grid" id="grid" role="list" aria-label="Lista de filmes 2026"></div>''', 1)
html = re.sub(r'<footer>[\s\S]*?</footer>', '<footer>Catálogo de filmes 2026 atualizado em 2026-08-22. Todo conteúdo listado deve ser disponibilizado apenas com autorização dos titulares de direitos.</footer>', html, count=1)

# Inject slug into MOVIES array for runtime anchors
runtime_movies = [{k:v for k,v in m.items() if k != 'link'} for m in movies]  # keep? maybe remove external original links from data? safer; but render no longer uses link
newjson = json.dumps(runtime_movies, ensure_ascii=False, separators=(',', ':'))
pos = html.find('const MOVIES = ') + len('const MOVIES = ')
end = html.find('];', pos) + 1
html = html[:pos] + newjson + html[end:]

# Replace JS function block card + enhance render URL query
old_card = re.search(r'function card\(m\) \{[\s\S]*?\n\}\n\nfunction render\(\)', html)
if not old_card:
    raise SystemExit('function card block not found')
new_card = r'''function card(m) {
  const badges = m.badges.map(b => '<span class="badge ' + b[0] + '">' + esc(b[1]) + '</span>').join('');
  const magnets = m.magnets.map(l => '<a rel="nofollow" href="' + esc(l.url) + '">' + esc(l.label.replace(/^\W+/, '')) + '</a>').join('');
  let extra = '';
  if (m.magnets.length > 1) {
    extra = '<details><summary>+ ' + (m.magnets.length - 1) + ' link(s) magnet</summary><div class="links">' + magnets + '</div></details>';
  } else if (m.magnets.length === 1) {
    extra = '<details><summary>+ detalhes do link</summary><div class="links">' + magnets + '</div></details>';
  }
  const trailer = m.other.map(l => '<a class="trailer" href="' + esc(l.url) + '" target="_blank" rel="nofollow noopener noreferrer">' + esc(l.label) + '</a>').join('');
  const date = m.date ? '<time class="date" datetime="' + esc(m.date) + '">' + esc(m.date) + '</time>' : '';
  const magnetHref = m.magnets.length ? esc(m.magnets[0].url) : '#';
  const quality = (m.badges.find(b => b[0] === 'q') || ['', ''])[1];
  const audioInfo = (m.badges.find(b => b[0] === 'a') || ['', ''])[1];
  const label = esc(m.title + (quality ? ' - ' + quality : '') + (audioInfo ? ' - ' + audioInfo : ''));
  return '<article id="' + esc(m._slug) + '" class="card" role="listitem" itemscope itemtype="https://schema.org/Movie" aria-label="' + label + '">' +
    '<meta itemprop="url" content="#' + esc(m._slug) + '">' +
    '<div class="thumb"><img itemprop="image" loading="lazy" decoding="async" src="' + esc(m.poster) + '" alt="Capa do filme ' + esc(m.title) + '" title="' + esc(m.title) + '"><div class="badges">' + badges + '</div>' + date + '</div>' +
    '<div class="info">' +
      '<h2 itemprop="name">' + esc(m.title) + '</h2>' +
      '<p class="sr-only" itemprop="description">' + label + '. Confira trailer e opções oficiais de download autorizadas.</p>' +
      '<div class="actions">' +
        '<a class="btn magnet" rel="nofollow" href="' + magnetHref + '" aria-label="Baixar ' + esc(m.title) + '">🧲 Baixar Magnet</a>' +
        extra +
        trailer +
      '</div>' +
    '</div>' +
  '</article>';
}

function render()'''
html = html[:old_card.start()] + new_card + html[old_card.end():]

# Add URL query handling and update URL softly while searching
html = html.replace("const esc = s => String(s).replace(/[&<>\"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',\"'\":'&#39;'}[c]));", "const esc = s => String(s).replace(/[&<>\"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',\"'\":'&#39;'}[c]));\nconst params = new URLSearchParams(location.search);\nif (params.get('q')) q.value = params.get('q');", 1)
html = html.replace("  stats.textContent = list.length + ' de ' + MOVIES.length + ' filmes';\n}", "  stats.textContent = list.length + ' de ' + MOVIES.length + ' filmes';\n  document.title = term ? ('Busca por ' + q.value.trim() + ' | Filmes 2026') : '" + seo_title.replace("'", "\\'") + "';\n}\n", 1)
html = html.replace("q.addEventListener('input', render);", "q.addEventListener('input', () => {\n  const url = new URL(location.href);\n  q.value.trim() ? url.searchParams.set('q', q.value.trim()) : url.searchParams.delete('q');\n  history.replaceState(null, '', url);\n  render();\n});", 1)

out.write_text(html, encoding='utf-8')

# robots.txt and sitemap.xml
Path('/home/user/robots.txt').write_text(f'''User-agent: *
Allow: /
Sitemap: {base_url}sitemap.xml
''', encoding='utf-8')
Path('/home/user/sitemap.xml').write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{base_url}</loc>
    <lastmod>2026-08-22</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
''', encoding='utf-8')

print('SEO aplicado em', out)
print('Filmes no schema:', len(movies))
print('Arquivos extras: /home/user/robots.txt /home/user/sitemap.xml')
