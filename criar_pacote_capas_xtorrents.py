import json, re, requests, shutil, zipfile, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image, ImageOps, ImageDraw
from io import BytesIO

BASE = Path('/home/user')
# Prefer latest index with descriptions if available, fallback to live captured index
candidates = [
    BASE/'patch_descricoes_xtorrents/index.html',
    BASE/'current_xtorrents_home_utf8.html',
    BASE/'xtorrent_live_utf8.html',
]
for p in candidates:
    if p.exists():
        INDEX_SRC = p
        break
else:
    raise SystemExit('Nenhum index base encontrado')

html = INDEX_SRC.read_text(encoding='utf-8')
m = re.search(r'window\.XT_CATALOG=(\[.*?\]);</script>', html, re.S)
if not m:
    raise SystemExit('Não encontrei window.XT_CATALOG no index')
items = json.loads(m.group(1))

out = BASE/'capas_local_xtorrents'
capas_dir = out/'capas'
if out.exists():
    shutil.rmtree(out)
capas_dir.mkdir(parents=True)

session = requests.Session()
session.headers.update({'User-Agent':'Mozilla/5.0 (compatible; XTorrentsCoverBot/1.0)'})

# placeholder for missing/broken cover
def make_placeholder(path, title='x-torrents'):
    im = Image.new('RGB',(200,300),(12,15,22))
    d = ImageDraw.Draw(im)
    d.rectangle((0,0,199,299), outline=(255,201,40), width=4)
    d.text((22,128),'x-torrents', fill=(255,201,40))
    im.save(path, 'WEBP', quality=82, method=6)

def convert_bytes_to_webp(content, dest):
    im = Image.open(BytesIO(content))
    im = ImageOps.exif_transpose(im).convert('RGB')
    # normalize poster size, preserving ratio with cover crop to 400x600 for better Google preview
    target=(400,600)
    im.thumbnail((target[0], 10000), Image.Resampling.LANCZOS)
    # if width less, resize to target width
    if im.width != target[0]:
        ratio=target[0]/im.width
        im=im.resize((target[0], max(1,int(im.height*ratio))), Image.Resampling.LANCZOS)
    # center crop/pad to 400x600
    if im.height >= target[1]:
        top=(im.height-target[1])//2
        im=im.crop((0,top,target[0],top+target[1]))
    else:
        bg=Image.new('RGB',target,(12,15,22))
        y=(target[1]-im.height)//2
        bg.paste(im,(0,y))
        im=bg
    im.save(dest, 'WEBP', quality=82, method=6)

def download_one(item):
    slug = item.get('slug') or 'sem-slug'
    url = item.get('poster') or ''
    dest = capas_dir/(slug + '.webp')
    if not url:
        make_placeholder(dest, item.get('title',''))
        return slug, False, 'sem_url'
    try:
        r = session.get(url, timeout=20)
        r.raise_for_status()
        convert_bytes_to_webp(r.content, dest)
        return slug, True, ''
    except Exception as e:
        make_placeholder(dest, item.get('title',''))
        return slug, False, str(e)[:160]

start=time.time()
fail=[]
with ThreadPoolExecutor(max_workers=24) as ex:
    futures=[ex.submit(download_one,it) for it in items]
    done=0
    for fut in as_completed(futures):
        slug, ok, err = fut.result()
        done += 1
        if not ok:
            fail.append({'slug':slug,'error':err})
        if done % 500 == 0:
            print(f'{done}/{len(items)} capas processadas...')

# Update catalog poster paths for local hosting
updated=[]
for it in items:
    ni=dict(it)
    ni['poster']='/capas/' + ni['slug'] + '.webp'
    updated.append(ni)

html2 = html[:m.start(1)] + json.dumps(updated, ensure_ascii=False, separators=(',',':')) + html[m.end(1):]
# reinforce image meta? Homepage og-image can remain or use logo. Do not set to a random cover.
(out/'index.html').write_text(html2, encoding='utf-8')

movies_php = """<?php
// Catálogo público do x-torrents com capas locais em /capas/slug.webp.
$json = <<<'JSON'
%s
JSON;
return json_decode($json, true);
""" % json.dumps(updated, ensure_ascii=False, separators=(',',':'))
(out/'movies.php').write_text(movies_php, encoding='utf-8')

# Copy filme.php from current patch if available; it reads poster from movies.php, so local covers work automatically
for fp in [BASE/'patch_descricoes_xtorrents/filme.php', BASE/'correcao_paginas_filmes_xtorrents/filme.php']:
    if fp.exists():
        shutil.copy2(fp, out/'filme.php')
        break

# Add htaccess snippet for webp cache
(out/'htaccess_cache_webp.txt').write_text('''# Adicione ao seu .htaccess para cache das capas locais:\n<IfModule mod_expires.c>\n  ExpiresActive On\n  ExpiresByType image/webp "access plus 1 month"\n</IfModule>\n\n<IfModule mod_headers.c>\n  <FilesMatch "\\.webp$">\n    Header set Cache-Control "public, max-age=2592000"\n  </FilesMatch>\n</IfModule>\n''', encoding='utf-8')

# manifest report
report = {
    'fonte_index': str(INDEX_SRC),
    'total_itens': len(items),
    'capas_geradas': len(list(capas_dir.glob('*.webp'))),
    'falhas_com_placeholder': len(fail),
    'pasta_capas': 'capas/',
    'formato': 'webp',
    'tamanho_padrao': '400x600',
    'qualidade_webp': 82,
}
(out/'relatorio_capas.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
(out/'falhas_capas.json').write_text(json.dumps(fail, ensure_ascii=False, indent=2), encoding='utf-8')
(out/'LEIA-ME-CAPAS.txt').write_text(f'''# Pacote de capas locais — x-torrents\n\nForam geradas {len(items)} capas locais em WebP na pasta /capas/.\n\nArquivos principais:\n- capas/ → todas as capas em WebP\n- index.html → catálogo atualizado para usar /capas/slug.webp\n- movies.php → dados das páginas individuais com capas locais\n- filme.php → se incluído, usa o movies.php atualizado\n- htaccess_cache_webp.txt → trecho opcional de cache para .htaccess\n\nComo subir:\n1. Envie a pasta `capas` inteira para a raiz public_html.\n2. Substitua `index.html` e `movies.php`.\n3. Se `filme.php` estiver no pacote, substitua também.\n4. Não mexa em links.php, start.php, iniciar.php, download.php e config.php se o download já está funcionando.\n\nTeste depois:\nhttps://xtorrents.com.br/capas/ghost-in-the-cell.webp\nhttps://xtorrents.com.br/filme/ghost-in-the-cell/\n\nObservação: algumas capas que falharam no download recebem placeholder. Veja falhas_capas.json.\n''', encoding='utf-8')

# Zip package
zip_path=BASE/'pacote_capas_locais_xtorrents.zip'
if zip_path.exists(): zip_path.unlink()
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in out.rglob('*'):
        if f.is_file():
            z.write(f, arcname=str(f.relative_to(out)))

print('Finalizado')
print('Fonte index:', INDEX_SRC)
print('Total itens:', len(items))
print('Capas geradas:', len(list(capas_dir.glob('*.webp'))))
print('Falhas/placeholders:', len(fail))
print('Tempo:', round(time.time()-start,1),'s')
print('Pasta:', out)
print('ZIP:', zip_path, zip_path.stat().st_size)
