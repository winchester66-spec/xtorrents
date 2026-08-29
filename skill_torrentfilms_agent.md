# Skill — TorrentFilms / Hostinger / SEO / Encurtador

Use este documento como uma **skill/instrução de continuidade** em uma nova conversa.  
Objetivo: permitir que outro atendimento continue o projeto do site **TorrentFilms** sem precisar redescobrir tudo.

---

## 1. Identidade do projeto

Site principal:

```txt
https://torrentfilms.produtodigital.org/
```

Hospedagem:

```txt
Hostinger
```

Tipo de site:

```txt
Catálogo de filmes 2026 com capas, busca, filtros, páginas individuais de filmes e monetização via encurtador.
```

Tema visual:

- Estilo escuro/cinematográfico.
- Inspirado visualmente no modelo do ViaTorrent, sem copiar código.
- Cards animados, mas otimizados para performance.
- Busca com recomendações.
- Botão de download monetizado.

---

## 2. Histórico resumido do que foi feito

### Correções iniciais

- O site original tinha todas as capas repetidas.
- Foram corrigidas as capas de **416 filmes**.
- O botão **“Página original”** foi removido.
- O texto **“indexado a partir de baixetorrents.net”** foi removido.

### SEO inicial

Foi aplicado SEO no HTML:

- Meta title.
- Meta description.
- Robots index/follow.
- Canonical.
- Open Graph.
- Twitter Card.
- Schema JSON-LD:
  - `WebSite`
  - `CollectionPage`
  - `BreadcrumbList`
  - `ItemList`
  - `Movie`

### Tema

Foi aplicado um tema moderno:

- Header com hero.
- Seção “Destaques em Alta”.
- Seção “Últimos Filmes Adicionados”.
- Filtros rápidos.
- Cards com capa, nota fake visual, badges, botão baixar e trailer.

### Performance

Foram feitas otimizações:

- Carregamento progressivo dos filmes.
- Botão “Carregar mais filmes”.
- Lazy loading nas imagens.
- Redução de sombras, blur e filtros pesados.
- Busca com índice interno.
- Animações mais suaves.

### Hostinger

O site foi migrado para Hostinger com domínio:

```txt
https://torrentfilms.produtodigital.org/
```

Foram ajustados:

- canonical
- og:url
- schema
- robots.txt
- sitemap.xml
- .htaccess

### Encurtador

Foi decidido usar **1 único link encurtado + sistema PHP com sessão**.

Fluxo final:

```txt
Usuário clica em Baixar
↓
start.php salva id/link na sessão
↓
redireciona para link único do encurtador
↓
usuário passa pelo anúncio
↓
encurtador volta para download.php
↓
download.php abre o magnet correto
```

Link único configurado:

```txt
https://seulink.net/MBAySxG9
```

Importante: **não salvar tokens de API em arquivos públicos**.

### Páginas individuais

Foi solicitado criar páginas indexáveis para cada filme.

Versão corrigida final usa sistema dinâmico:

```txt
/filme/o-fim-da-rua/
/filme/homem-aranha-um-novo-dia/
/filme/a-captura/
```

Essas URLs são roteadas pelo `.htaccess` para:

```txt
filme.php?slug=o-fim-da-rua
```

Arquivos relacionados:

```txt
filme.php
movies.php
.htaccess
sitemap.xml
```

### Favicon

Foi criado favicon personalizado:

```txt
favicon.ico
favicon.svg
favicon-32x32.png
apple-touch-icon.png
android-chrome-192x192.png
site.webmanifest
```

---

## 3. Arquitetura final recomendada

Arquivos principais no Hostinger:

```txt
index.html
filme.php
movies.php
links.php
config.php
start.php
download.php
robots.txt
sitemap.xml
.htaccess
favicon.ico
favicon.svg
favicon-32x32.png
apple-touch-icon.png
android-chrome-192x192.png
site.webmanifest
```

### Função de cada arquivo

#### `index.html`

Página inicial do catálogo.

Contém:

- lista pública dos filmes;
- busca;
- filtros;
- cards;
- links para páginas individuais;
- botões `Baixar` apontando para `start.php`.

#### `filme.php`

Gera dinamicamente a página individual de cada filme.

Recebe:

```txt
/filme/slug-do-filme/
```

via `.htaccess`.

Renderiza:

- title individual;
- meta description;
- canonical;
- OG/Twitter;
- Schema Movie;
- capa;
- badges;
- informações;
- download;
- relacionados.

#### `movies.php`

Contém os dados públicos dos filmes para o `filme.php`.

Deve ser bloqueado no `.htaccess`.

#### `links.php`

Contém os magnets reais.

Deve ser bloqueado no `.htaccess`.

#### `config.php`

Contém o link único do encurtador.

Exemplo:

```php
<?php
return [
  'encurta_url' => 'https://seulink.net/MBAySxG9'
];
```

Deve ser bloqueado no `.htaccess`.

#### `start.php`

Recebe o clique:

```txt
/start.php?id=o-fim-da-rua&link=0
```

Salva na sessão:

```txt
id do filme
índice do link
horário
```

Depois redireciona para o link único do encurtador.

#### `download.php`

Recebe o usuário depois do encurtador.

Lê a sessão e abre o magnet correto.

Se o usuário acessar direto, exibe:

```txt
Acesso expirado
```

Isso é esperado.

#### `.htaccess`

Deve conter regras para:

- bloquear `links.php`, `config.php`, `movies.php`;
- forçar HTTPS;
- forçar domínio correto;
- rotear `/filme/slug/` para `filme.php?slug=slug`;
- compressão/cache.

Regra essencial:

```apache
RewriteRule ^filme/([A-Za-z0-9-]+)/?$ filme.php?slug=$1 [L,QSA]
```

---

## 4. Últimos pacotes gerados no projeto

Os pacotes mais importantes criados foram:

```txt
site_hostinger_filmes_dinamico_corrigido.zip
site_hostinger_com_favicon.zip
```

O mais atual visualmente e com favicon:

```txt
site_hostinger_com_favicon.zip
```

Mas se houver dúvida, conferir se o pacote contém:

```txt
filme.php
movies.php
favicon.ico
favicon.svg
.htaccess
sitemap.xml
```

---

## 5. Sitemap correto

O sitemap final deve conter:

```txt
417 URLs
```

Sendo:

```txt
1 página inicial
416 páginas individuais de filmes
```

Exemplo:

```xml
<url>
  <loc>https://torrentfilms.produtodigital.org/filme/o-fim-da-rua/</loc>
  <lastmod>2026-08-22</lastmod>
  <changefreq>weekly</changefreq>
  <priority>0.8</priority>
</url>
```

No Search Console, enviar:

```txt
sitemap.xml
```

URL completa:

```txt
https://torrentfilms.produtodigital.org/sitemap.xml
```

---

## 6. Troubleshooting importante

### Erro 500 ao clicar em baixar

Possíveis causas:

- erro no `links.php`;
- erro no `config.php`;
- PHP incompatível;
- `.htaccess` inválido.

Correção que já foi aplicada:

- `links.php` passou a carregar JSON interno com `json_decode`, evitando erro de sintaxe.

### Página `/filme/.../` mostra 404

Possíveis causas:

- `.htaccess` não foi enviado;
- o arquivo foi enviado sem o ponto: `htaccess` em vez de `.htaccess`;
- regra `RewriteRule` ausente;
- arquivos enviados para pasta errada;
- `filme.php` ou `movies.php` ausentes.

Correção:

Garantir `.htaccess` com:

```apache
RewriteEngine On
RewriteRule ^filme/([A-Za-z0-9-]+)/?$ filme.php?slug=$1 [L,QSA]
```

E garantir que existam:

```txt
filme.php
movies.php
```

### `download.php` mostra “Acesso expirado”

Normal se abrir direto.

O fluxo correto é:

```txt
site → botão Baixar → start.php → encurtador → download.php
```

### Sitemap mostra erro no Google

Verificar se:

```txt
https://torrentfilms.produtodigital.org/sitemap.xml
```

abre no navegador e começa com:

```xml
<urlset
```

Não usar sitemap index se o Search Console estiver falhando.

---

## 7. Estratégia SEO recomendada

### Prioridade máxima

- Manter páginas individuais indexáveis.
- Atualizar sitemap sempre que novos filmes forem adicionados.
- Criar textos únicos e mais ricos para cada filme.
- Melhorar títulos e descriptions por filme.

### Palavras-chave principais

```txt
filmes 2026
filmes dublados 2026
filmes legendados 2026
filmes dual áudio
filmes 1080p
lançamentos de filmes 2026
filmes de ação 2026
filmes de terror 2026
filmes de suspense 2026
filmes de comédia 2026
```

### Modelo de title por filme

```txt
Nome do Filme (2026) — Sinopse, Trailer e Download | TorrentFilms
```

### Modelo de description por filme

```txt
Confira Nome do Filme (2026) no TorrentFilms com capa, trailer, qualidade, idioma e opção autorizada de download.
```

---

## 8. Como usar esta skill em nova conversa

Em uma nova conversa, envie este arquivo e diga:

```txt
Use esta skill como contexto do projeto TorrentFilms. Continue a partir dela.
```

Se possível, também envie o pacote mais recente do site, principalmente:

```txt
site_hostinger_com_favicon.zip
```

ou os arquivos atuais baixados da Hostinger.

---

## 9. Comandos úteis para gerar pacote ZIP

Se precisar empacotar uma pasta para Hostinger:

```python
import zipfile
from pathlib import Path
folder = Path('hostinger_filmes_dinamico_upload')
zip_path = Path('site_final.zip')
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in folder.rglob('*'):
        if f.is_file():
            z.write(f, arcname=str(f.relative_to(folder)))
```

---

## 10. Segurança

Nunca publicar:

```txt
API token do Encurta.net
senhas
credenciais FTP
credenciais Hostinger
```

Arquivos que devem ser bloqueados no `.htaccess`:

```txt
links.php
config.php
movies.php
```

Exemplo:

```apache
<Files "links.php">
  Require all denied
</Files>
<Files "config.php">
  Require all denied
</Files>
<Files "movies.php">
  Require all denied
</Files>
```

---

## 11. Estado final desejado

O site final deve ter:

- página inicial rápida;
- busca funcional;
- botão carregar mais;
- favicon personalizado;
- páginas individuais `/filme/slug/` funcionando;
- sitemap com 417 URLs;
- download monetizado por link único;
- SEO básico por filme;
- arquivos privados protegidos;
- Search Console sem erro de sitemap.

---

## 12. Checklist antes de publicar

Antes de subir na Hostinger, conferir:

```txt
[ ] index.html existe
[ ] filme.php existe
[ ] movies.php existe
[ ] links.php existe
[ ] config.php existe
[ ] start.php existe
[ ] download.php existe
[ ] .htaccess existe com ponto inicial
[ ] sitemap.xml contém 417 URLs
[ ] robots.txt aponta para sitemap.xml
[ ] favicon.ico existe
[ ] favicon.svg existe
[ ] config.php contém o link único do encurtador
```

Depois de publicar, testar:

```txt
https://torrentfilms.produtodigital.org/
https://torrentfilms.produtodigital.org/filme/o-fim-da-rua/
https://torrentfilms.produtodigital.org/filme/homem-aranha-um-novo-dia/
https://torrentfilms.produtodigital.org/sitemap.xml
https://torrentfilms.produtodigital.org/favicon.ico
```

E testar fluxo de download clicando no botão **Baixar** dentro do site.
