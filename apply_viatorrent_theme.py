import re, zipfile
from pathlib import Path

src = Path('/home/user/index_seo_profissional.html')
out = Path('/home/user/index_tema_viatorrent.html')
html = src.read_text(encoding='utf-8')

css = r'''
:root{
  --bg:#07080d;--bg2:#0b1020;--panel:#111827;--panel2:#151f33;--line:rgba(255,255,255,.09);
  --txt:#f5f7fb;--mut:#9aa4b5;--brand:#ffc400;--brand2:#ff7a18;--red:#ef233c;--green:#26e07f;--cyan:#22d3ee;
  --shadow:0 24px 60px rgba(0,0,0,.45);--radius:18px
}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{background:radial-gradient(circle at 15% 0%,rgba(255,196,0,.13),transparent 30%),radial-gradient(circle at 85% 8%,rgba(239,35,60,.12),transparent 28%),linear-gradient(180deg,var(--bg),#080b13 42%,#05060a);color:var(--txt);font-family:Inter,system-ui,-apple-system,'Segoe UI',Roboto,Arial,sans-serif;min-height:100vh;overflow-x:hidden}
body:before{content:"";position:fixed;inset:0;pointer-events:none;background-image:linear-gradient(rgba(255,255,255,.025) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.025) 1px,transparent 1px);background-size:44px 44px;mask-image:linear-gradient(to bottom,rgba(0,0,0,.8),transparent 72%);z-index:-1}
a{color:inherit}
.site-hero{position:relative;min-height:330px;padding:26px 20px 34px;border-bottom:1px solid var(--line);overflow:hidden;background:linear-gradient(135deg,rgba(12,16,29,.82),rgba(7,8,13,.94))}
.site-hero:before,.site-hero:after{content:"";position:absolute;border-radius:999px;filter:blur(8px);opacity:.55;animation:floatGlow 7s ease-in-out infinite alternate;pointer-events:none}.site-hero:before{width:260px;height:260px;background:radial-gradient(circle,var(--brand),transparent 62%);right:-90px;top:-90px}.site-hero:after{width:210px;height:210px;background:radial-gradient(circle,var(--red),transparent 64%);left:-80px;bottom:-105px;animation-delay:1.1s}
@keyframes floatGlow{from{transform:translate3d(0,0,0) scale(1)}to{transform:translate3d(-18px,18px,0) scale(1.08)}}
.topbar{position:relative;z-index:2;max-width:1240px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;gap:16px}.brand{display:flex;align-items:center;gap:12px;text-decoration:none}.logo-mark{width:44px;height:44px;border-radius:14px;background:linear-gradient(135deg,var(--brand),var(--brand2));display:grid;place-items:center;color:#151000;font-weight:1000;box-shadow:0 12px 30px rgba(255,196,0,.27);animation:pulseLogo 2.6s ease-in-out infinite}.brand-name{font-weight:1000;letter-spacing:.8px;text-transform:uppercase}.brand-name span{color:var(--brand)}@keyframes pulseLogo{50%{transform:scale(1.06);box-shadow:0 14px 40px rgba(255,196,0,.42)}}
.hero-content{position:relative;z-index:2;max-width:940px;margin:48px auto 0;text-align:center}.eyebrow{display:inline-flex;align-items:center;gap:8px;border:1px solid rgba(255,196,0,.28);background:rgba(255,196,0,.09);color:var(--brand);padding:7px 12px;border-radius:999px;font-size:.76rem;font-weight:900;text-transform:uppercase;letter-spacing:.9px;margin-bottom:16px}.hero-content h1{font-size:clamp(2.2rem,6vw,5.2rem);line-height:.92;font-weight:1000;text-transform:uppercase;letter-spacing:-2.5px;text-shadow:0 22px 42px rgba(0,0,0,.42);background:linear-gradient(180deg,#fff,#cfd6e6);-webkit-background-clip:text;background-clip:text;color:transparent}.hero-content h1 strong{display:block;color:var(--brand);background:linear-gradient(90deg,var(--brand),#fff0a8,var(--brand2));-webkit-background-clip:text;background-clip:text}.hero-content p{max-width:720px;margin:18px auto 0;color:#c7cedc;font-size:1.02rem;line-height:1.65}.search-panel{position:relative;z-index:3;max-width:920px;margin:26px auto 0;display:grid;grid-template-columns:1fr 180px;gap:10px;background:rgba(255,255,255,.08);border:1px solid var(--line);backdrop-filter:blur(14px);padding:10px;border-radius:20px;box-shadow:var(--shadow)}.search-panel input,.search-panel select{height:48px;border:0;outline:0;border-radius:14px;background:rgba(5,8,15,.86);color:var(--txt);padding:0 16px;font-weight:700}.search-panel input::placeholder{color:#717b8e}.search-panel select{cursor:pointer}.nav-pills{position:relative;z-index:3;max-width:1100px;margin:20px auto 0;display:flex;gap:10px;justify-content:center;flex-wrap:wrap}.pill{border:1px solid rgba(255,255,255,.11);background:rgba(255,255,255,.06);color:#e8edf7;text-decoration:none;border-radius:999px;padding:9px 15px;font-size:.8rem;font-weight:900;text-transform:uppercase;letter-spacing:.4px;cursor:pointer;transition:.2s}.pill:hover,.pill.active{background:linear-gradient(90deg,var(--brand),var(--brand2));color:#160f00;transform:translateY(-2px);box-shadow:0 10px 26px rgba(255,196,0,.22)}
.stats{font-size:.82rem;color:var(--mut);font-weight:800;white-space:nowrap}.section{max-width:1240px;margin:0 auto;padding:28px 20px}.section-head{display:flex;align-items:end;justify-content:space-between;gap:18px;margin-bottom:16px}.section-title{display:flex;align-items:center;gap:10px;font-size:1.28rem;text-transform:uppercase;letter-spacing:.5px;font-weight:1000}.section-title:before{content:"";width:5px;height:26px;background:linear-gradient(var(--brand),var(--brand2));border-radius:999px}.section-sub{color:var(--mut);font-size:.86rem}.featured-grid{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(170px,1fr);gap:16px;overflow-x:auto;overscroll-behavior-x:contain;scroll-snap-type:x mandatory;padding:2px 2px 16px}.featured-grid::-webkit-scrollbar{height:8px}.featured-grid::-webkit-scrollbar-thumb{background:rgba(255,255,255,.16);border-radius:999px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(175px,1fr));gap:18px}.card{position:relative;border-radius:var(--radius);overflow:hidden;min-height:318px;background:#111827;border:1px solid var(--line);box-shadow:0 12px 34px rgba(0,0,0,.28);isolation:isolate;animation:cardIn .48s ease both;transition:transform .24s ease,border-color .24s ease,box-shadow .24s ease}.card:hover{transform:translateY(-8px) scale(1.015);border-color:rgba(255,196,0,.48);box-shadow:0 26px 56px rgba(0,0,0,.48)}@keyframes cardIn{from{opacity:0;transform:translateY(20px) scale(.98)}to{opacity:1;transform:translateY(0) scale(1)}}.thumb{position:absolute;inset:0;background:var(--panel2);overflow:hidden}.thumb:after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.02) 30%,rgba(0,0,0,.55) 64%,rgba(0,0,0,.94));z-index:1}.thumb img{width:100%;height:100%;object-fit:cover;display:block;transform:scale(1.02);transition:transform .45s ease,filter .35s ease}.card:hover .thumb img{transform:scale(1.12);filter:saturate(1.12) contrast(1.06)}.rating{position:absolute;top:10px;left:10px;z-index:3;width:42px;height:42px;border-radius:50%;display:grid;place-items:center;background:rgba(5,8,15,.82);border:2px solid var(--brand);color:var(--brand);font-weight:1000;font-size:.82rem;box-shadow:0 8px 18px rgba(0,0,0,.35)}.thumb .date{position:absolute;top:12px;right:10px;z-index:3;background:linear-gradient(90deg,var(--brand),var(--brand2));color:#160f00;font-size:.68rem;padding:5px 8px;border-radius:999px;font-weight:1000}.badges{position:absolute;left:12px;right:12px;bottom:96px;z-index:3;display:flex;flex-wrap:wrap;gap:5px}.badge{font-size:.62rem;font-weight:1000;padding:4px 7px;border-radius:7px;text-transform:uppercase;letter-spacing:.25px}.badge.q{background:rgba(255,196,0,.92);color:#171000}.badge.s{background:rgba(34,211,238,.18);color:#aaf4ff;border:1px solid rgba(34,211,238,.28)}.badge.a{background:rgba(38,224,127,.88);color:#04140a}.info{position:relative;z-index:4;margin-top:198px;padding:12px 12px 14px;display:flex;flex-direction:column;gap:9px;min-height:120px}.info h2{font-size:.93rem;line-height:1.22;font-weight:1000;text-shadow:0 2px 8px rgba(0,0,0,.55);min-height:2.25em}.actions{display:grid;gap:7px;margin-top:auto}.btn{display:block;text-align:center;text-decoration:none;font-size:.78rem;font-weight:1000;padding:9px 10px;border-radius:12px;border:1px solid transparent;cursor:pointer;transition:.2s}.btn.magnet{background:linear-gradient(90deg,var(--brand),var(--brand2));color:#160f00;box-shadow:0 10px 24px rgba(255,122,24,.18)}.btn.magnet:hover{filter:brightness(1.08);transform:translateY(-1px)}details{margin-top:0}details summary{font-size:.7rem;color:#d7deeb;cursor:pointer;text-align:center;padding:3px;list-style:none}details summary::-webkit-details-marker{display:none}.links{display:flex;flex-direction:column;gap:5px;margin-top:5px;max-height:145px;overflow:auto}.links a{font-size:.67rem;color:#ffe37a;text-decoration:none;background:rgba(0,0,0,.55);border:1px solid rgba(255,255,255,.1);border-radius:8px;padding:6px 8px;word-break:break-all}.trailer{display:block;text-align:center;font-size:.72rem;color:#fff;text-decoration:none;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.1);border-radius:10px;padding:7px}.trailer:hover{background:rgba(255,255,255,.14)}.seo-intro{max-width:1240px;margin:0 auto 6px;background:linear-gradient(135deg,rgba(255,196,0,.1),rgba(239,35,60,.07));border:1px solid var(--line);border-radius:20px;padding:18px 20px}.seo-intro h2{font-size:1.1rem;margin-bottom:8px}.seo-intro p{color:var(--mut);font-size:.94rem;line-height:1.6}.empty{grid-column:1/-1;text-align:center;color:var(--mut);padding:50px 0;display:none;border:1px dashed var(--line);border-radius:18px}.site-footer{border-top:1px solid var(--line);padding:28px 20px;text-align:center;color:var(--mut);font-size:.78rem;background:rgba(0,0,0,.28)}.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}@media(max-width:760px){.topbar{align-items:flex-start}.search-panel{grid-template-columns:1fr}.site-hero{min-height:390px}.hero-content{margin-top:36px}.featured-grid{grid-auto-columns:155px}.grid{grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:14px}.card{min-height:292px}.info{margin-top:178px}.badges{bottom:100px}.stats{display:none}}@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
'''.strip()
html = re.sub(r'<style>[\s\S]*?</style>', '<style>\n'+css+'\n</style>', html, count=1)

# Body structure replacements
header = r'''
<header class="site-hero">
  <div class="topbar">
    <a class="brand" href="/" aria-label="Página inicial">
      <span class="logo-mark">▶</span>
      <span class="brand-name">FILMES <span>2026</span></span>
    </a>
    <span class="stats" id="stats"></span>
  </div>
  <div class="hero-content">
    <span class="eyebrow">Catálogo atualizado</span>
    <h1>Filmes e <strong>Séries</strong></h1>
    <p>Lançamentos 2026 com capas, trailers, qualidade, idioma e opções oficiais de download autorizadas em uma experiência visual moderna.</p>
  </div>
  <div class="search-panel">
    <input id="q" type="search" name="q" placeholder="Buscar filme, série ou lançamento..." autocomplete="off" aria-label="Buscar filme por título">
    <select id="audio" aria-label="Filtrar por idioma ou áudio">
      <option value="">Áudio: Todos</option>
      <option value="dublado">Dublado</option>
      <option value="dual">Dual Áudio</option>
      <option value="inglês">Inglês</option>
      <option value="legendado">Legendado</option>
    </select>
  </div>
  <nav class="nav-pills" aria-label="Filtros rápidos">
    <button class="pill active" type="button" data-filter="">Todos</button>
    <button class="pill" type="button" data-filter="1080p">1080p</button>
    <button class="pill" type="button" data-filter="dublado">Dublado</button>
    <button class="pill" type="button" data-filter="dual">Dual Áudio</button>
    <button class="pill" type="button" data-filter="legendado">Legendado</button>
    <button class="pill" type="button" data-filter="cam">CAM</button>
  </nav>
</header>'''.strip()
html = re.sub(r'<header>[\s\S]*?</header>', header, html, count=1)

main = r'''
<main>
  <section class="section featured" aria-labelledby="featured-title">
    <div class="section-head">
      <div>
        <h2 class="section-title" id="featured-title">Destaques em Alta</h2>
        <p class="section-sub">Seleção dos lançamentos mais recentes do catálogo</p>
      </div>
    </div>
    <div class="featured-grid" id="featuredGrid" role="list" aria-label="Destaques em alta"></div>
  </section>
  <section class="section seo-intro" aria-labelledby="intro-title">
    <h2 id="intro-title">Catálogo atualizado de filmes 2026</h2>
    <p>Veja lançamentos de filmes 2026 com capa, data de publicação, qualidade, idioma, trailers e opções oficiais de download autorizadas. Use a busca para encontrar rapidamente filmes dublados, dual áudio, legendados e em alta definição.</p>
  </section>
  <section class="section" aria-labelledby="latest-title">
    <div class="section-head">
      <div>
        <h2 class="section-title" id="latest-title">Últimos Filmes Adicionados</h2>
        <p class="section-sub">Navegue por todos os títulos indexados neste catálogo</p>
      </div>
    </div>
    <div class="grid" id="grid" role="list" aria-label="Lista de filmes 2026"></div>
    <div class="empty" id="empty">Nenhum filme encontrado para esta busca.</div>
  </section>
</main>'''.strip()
html = re.sub(r'<main>[\s\S]*?</main>', main, html, count=1)
html = re.sub(r'<footer>[\s\S]*?</footer>', '<footer class="site-footer">Catálogo de filmes 2026 atualizado. Todo conteúdo listado deve ser disponibilizado apenas com autorização dos titulares de direitos.</footer>', html, count=1)

# Replace JS constants to include featuredGrid and activeFilter
html = html.replace("const grid = document.getElementById('grid');\nconst empty", "const grid = document.getElementById('grid');\nconst featuredGrid = document.getElementById('featuredGrid');\nconst empty", 1)
html = html.replace("if (params.get('q')) q.value = params.get('q');", "if (params.get('q')) q.value = params.get('q');\nlet quickFilter = '';", 1)

old = re.search(r'function card\(m\) \{[\s\S]*?\n\}\n\nfunction render\(\) \{[\s\S]*?\n\}\n\nq\.addEventListener', html)
if not old:
    raise SystemExit('JS block not found')
new = r'''function ratingFor(m) {
  let n = 0;
  for (const ch of m.title) n = (n + ch.charCodeAt(0)) % 41;
  return (5 + n / 10).toFixed(1).replace('.0','');
}
function textBag(m) {
  return (m.title + ' ' + m.magnets.map(l => l.label).join(' ') + ' ' + m.badges.map(b => b[1]).join(' ')).toLowerCase();
}
function card(m, compact=false) {
  const badges = m.badges.map(b => '<span class="badge ' + b[0] + '">' + esc(b[1]) + '</span>').join('');
  const magnets = m.magnets.map(l => '<a rel="nofollow" href="' + esc(l.url) + '">' + esc(l.label.replace(/^\W+/, '')) + '</a>').join('');
  let extra = '';
  if (m.magnets.length > 1) {
    extra = '<details><summary>+ ' + (m.magnets.length - 1) + ' link(s) magnet</summary><div class="links">' + magnets + '</div></details>';
  } else if (m.magnets.length === 1 && !compact) {
    extra = '<details><summary>+ detalhes do link</summary><div class="links">' + magnets + '</div></details>';
  }
  const trailer = m.other.map(l => '<a class="trailer" href="' + esc(l.url) + '" target="_blank" rel="nofollow noopener noreferrer">' + esc(l.label) + '</a>').join('');
  const date = m.date ? '<time class="date" datetime="' + esc(m.date) + '">' + esc(m.date.slice(0,4)) + '</time>' : '';
  const magnetHref = m.magnets.length ? esc(m.magnets[0].url) : '#';
  const quality = (m.badges.find(b => b[0] === 'q') || ['', ''])[1];
  const audioInfo = (m.badges.find(b => b[0] === 'a') || ['', ''])[1];
  const label = esc(m.title + (quality ? ' - ' + quality : '') + (audioInfo ? ' - ' + audioInfo : ''));
  return '<article id="' + esc(m._slug) + '" class="card" role="listitem" itemscope itemtype="https://schema.org/Movie" aria-label="' + label + '">' +
    '<meta itemprop="url" content="#' + esc(m._slug) + '">' +
    '<div class="thumb"><img itemprop="image" loading="lazy" decoding="async" src="' + esc(m.poster) + '" alt="Capa do filme ' + esc(m.title) + '" title="' + esc(m.title) + '"><span class="rating">' + ratingFor(m) + '</span><div class="badges">' + badges + '</div>' + date + '</div>' +
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

function renderFeatured() {
  const top = MOVIES.slice(0, 15);
  featuredGrid.innerHTML = top.map(m => card(m, true)).join('');
}

function render() {
  const term = q.value.trim().toLowerCase();
  const au = audio.value.toLowerCase();
  const list = MOVIES.filter(m => {
    const bag = textBag(m);
    if (term && bag.indexOf(term) === -1) return false;
    if (au && bag.indexOf(au) === -1) return false;
    if (quickFilter && bag.indexOf(quickFilter) === -1) return false;
    return true;
  });
  grid.innerHTML = list.map(m => card(m)).join('');
  empty.style.display = list.length ? 'none' : 'block';
  stats.textContent = list.length + ' de ' + MOVIES.length + ' filmes';
  document.title = term ? ('Busca por ' + q.value.trim() + ' | Filmes 2026') : 'Filmes 2026: Lançamentos, Trailers e Downloads Oficiais';
}

document.querySelectorAll('.pill').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.pill').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    quickFilter = (btn.dataset.filter || '').toLowerCase();
    render();
    document.getElementById('latest-title').scrollIntoView({behavior:'smooth', block:'start'});
  });
});

renderFeatured();

q.addEventListener'''
html = html[:old.start()] + new + html[old.end()-len("q.addEventListener"):]

out.write_text(html, encoding='utf-8')

# Zip package
pack = Path('/home/user/site_tema_viatorrent.zip')
with zipfile.ZipFile(pack, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('index.html', html)
    for name in ['robots.txt','sitemap.xml']:
        p = Path('/home/user')/name
        if p.exists(): z.write(p, arcname=name)
print(out)
print(pack, pack.stat().st_size)
