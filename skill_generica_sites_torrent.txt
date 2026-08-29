# Skill Genérica — Sites de Catálogo Torrent / Hostinger / SEO / Encurtador

Use este documento em novas conversas para reaplicar o mesmo conhecimento em **qualquer outro site de catálogo torrent ou catálogo de downloads autorizados**.

> Observação importante: use esta skill apenas em sites e conteúdos que você tem autorização para publicar/distribuir. Links de download devem respeitar direitos autorais, leis locais e políticas dos serviços de hospedagem, anúncios e encurtadores.

---

## 1. Objetivo da skill

Transformar, corrigir ou melhorar um site de catálogo de filmes/séries/downloads com foco em:

- correção de capas/posters;
- melhoria visual;
- performance;
- SEO;
- páginas individuais indexáveis;
- sitemap para Google Search Console;
- favicon personalizado;
- monetização com encurtador usando apenas 1 link;
- hospedagem em Hostinger ou servidor PHP/Apache;
- organização dos arquivos para publicação.

---

## 2. Entrada esperada do projeto

Para trabalhar em um novo site, pedir ao usuário:

```txt
1. URL atual do site, se já estiver no ar.
2. Arquivo HTML atual ou ZIP do projeto.
3. Domínio final do site.
4. Hospedagem usada: Hostinger, Netlify, Vercel, outro.
5. Se usará encurtador ou não.
6. Link único do encurtador, caso já exista.
7. Quantidade aproximada de filmes/itens.
```

Se for Hostinger, assumir suporte a:

```txt
PHP
.htaccess
Apache
public_html
```

---

## 3. Fluxo geral de trabalho

Para qualquer novo site, seguir esta ordem:

```txt
1. Baixar/analisar o site atual.
2. Identificar onde estão os dados dos filmes.
3. Corrigir capas repetidas ou quebradas.
4. Remover textos/botões indesejados.
5. Aplicar tema visual e responsivo.
6. Otimizar performance.
7. Aplicar SEO base.
8. Criar páginas individuais indexáveis.
9. Criar sitemap.xml.
10. Criar robots.txt.
11. Criar favicon.
12. Criar sistema de encurtador, se solicitado.
13. Gerar ZIP final para hospedagem.
14. Orientar testes e envio ao Google Search Console.
```

---

## 4. Correção de capas/posters

Problema comum:

```txt
Todos os filmes aparecem com a mesma capa.
```

Solução:

- Identificar array JS ou estrutura HTML onde cada filme possui campo `poster`, `image`, `cover` ou similar.
- Buscar as capas corretas nas páginas originais ou no próprio catálogo-fonte, se permitido.
- Atualizar cada item com URL de poster única.
- Validar:

```txt
número de filmes = N
número de posters únicos ≈ N
```

---

## 5. Remoções comuns solicitadas

Remover elementos como:

```txt
Página original
indexado a partir de...
créditos de site externo
botões extras
textos indesejados no footer/header
```

Sempre preservar:

- funcionamento do download;
- estrutura dos dados;
- SEO;
- responsividade.

---

## 6. Tema visual recomendado

Tema padrão sugerido:

- fundo escuro cinematográfico;
- gradientes amarelo/laranja;
- cards com posters;
- hover suave;
- seção “Destaques em Alta”;
- seção “Últimos Adicionados”;
- busca com sugestões;
- filtros rápidos;
- botão “Carregar mais”.

Evitar animações pesadas:

```txt
blur excessivo
box-shadow exagerado
filtros CSS contínuos
muitos elementos animando ao mesmo tempo
```

Preferir:

```txt
transform
opacity
transition curta
lazy loading
content-visibility
renderização paginada
```

---

## 7. Performance

Para catálogos grandes, nunca renderizar todos os itens de uma vez.

Estratégia:

```txt
PAGE_SIZE = 48
carregar os primeiros 48
botão Carregar mais
lazy loading nas imagens
busca usando índice em memória
```

Usar:

```html
<img loading="lazy" decoding="async">
```

Nos primeiros posters importantes:

```html
<img loading="eager" fetchpriority="high">
```

---

## 8. Busca com recomendações

A busca deve:

- ignorar acentos;
- ignorar maiúsculas/minúsculas;
- aceitar hífen ou espaço;
- tolerar pequenos erros de digitação;
- exibir sugestões enquanto digita.

Exemplo:

```txt
homen aranha → Homem-Aranha
homem aranha → Homem-Aranha
aranha → resultados relacionados
```

Implementar normalização:

```js
function normalizeText(value) {
  return String(value || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, ' ')
    .trim()
    .replace(/\s+/g, ' ');
}
```

---

## 9. SEO base da página inicial

Aplicar:

```html
<title>...</title>
<meta name="description" content="...">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="https://DOMINIO/">
<meta property="og:title" content="...">
<meta property="og:description" content="...">
<meta property="og:url" content="https://DOMINIO/">
<meta property="og:image" content="...">
<meta name="twitter:card" content="summary_large_image">
```

Adicionar Schema:

- `WebSite`
- `CollectionPage`
- `BreadcrumbList`
- `ItemList`
- `Movie` para itens principais, se viável.

---

## 10. Páginas individuais indexáveis

Para ranquear cada filme, criar URLs individuais:

```txt
/filme/nome-do-filme/
```

Em Hostinger/Apache, usar sistema dinâmico:

```txt
filme.php?slug=nome-do-filme
```

Mas exibir URL amigável via `.htaccess`:

```apache
RewriteRule ^filme/([A-Za-z0-9-]+)/?$ filme.php?slug=$1 [L,QSA]
```

Arquivos necessários:

```txt
filme.php
movies.php
.htaccess
sitemap.xml
```

Cada página individual deve ter:

- title próprio;
- meta description própria;
- canonical próprio;
- Open Graph próprio;
- Twitter Card próprio;
- Schema `Movie`;
- capa;
- título;
- ano;
- qualidade;
- idioma;
- tamanho;
- texto SEO;
- downloads;
- trailer, se houver;
- filmes relacionados.

Modelo de title:

```txt
Nome do Filme (Ano) — Sinopse, Trailer e Download | NomeDoSite
```

Modelo de description:

```txt
Confira Nome do Filme (Ano) com capa, trailer, qualidade, idioma e opção autorizada de download.
```

---

## 11. Sitemap para Google Search Console

Criar `sitemap.xml` com:

```txt
1 URL da página inicial
N URLs individuais de filmes
```

Exemplo:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://dominio.com/</loc>
    <lastmod>2026-08-22</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://dominio.com/filme/nome-do-filme/</loc>
    <lastmod>2026-08-22</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>
```

No Search Console enviar:

```txt
sitemap.xml
```

Se o Google der erro, verificar:

```txt
https://dominio.com/sitemap.xml
```

Deve abrir XML começando com:

```xml
<urlset
```

---

## 12. Robots.txt

Modelo:

```txt
User-agent: *
Allow: /
Disallow: /start.php
Disallow: /download.php
Sitemap: https://dominio.com/sitemap.xml
```

Se houver arquivos privados:

```txt
Disallow: /links.php
Disallow: /config.php
Disallow: /movies.php
```

Mesmo assim, bloquear via `.htaccess` também.

---

## 13. .htaccess para Hostinger

Modelo base:

```apache
Options -Indexes
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

  RewriteCond %{HTTP_HOST} !^DOMINIO_ESCAPADO$ [NC]
  RewriteRule ^ https://DOMINIO_REAL%{REQUEST_URI} [L,R=301]

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
```

Substituir:

```txt
DOMINIO_ESCAPADO = exemplo\.com
DOMINIO_REAL = exemplo.com
```

---

## 14. Sistema de encurtador com 1 link único

Usar quando o usuário quer monetizar cada clique sem criar centenas de links.

Fluxo:

```txt
Botão Baixar
↓
start.php?id=slug&link=0
↓
Salva sessão
↓
Redireciona para 1 link encurtado
↓
Encurtador volta para download.php
↓
download.php lê sessão e abre o magnet correto
```

Arquivos:

```txt
start.php
download.php
links.php
config.php
```

### `config.php`

```php
<?php
return [
  'encurta_url' => 'https://seulink.net/SEU_LINK'
];
```

### Observação importante

O link único do encurtador deve apontar para:

```txt
https://dominio.com/download.php
```

O usuário não deve abrir `download.php` diretamente. Se abrir, é normal aparecer:

```txt
Acesso expirado
```

---

## 15. Alternativa: API do encurtador em massa

Usar apenas se o usuário quiser encurtar cada link individualmente.

Problemas comuns:

- limite diário de criação;
- limite de 200 links/dia;
- bloqueio de magnet;
- necessidade de cache;
- trabalho maior.

Se houver limite diário, usar cache:

```txt
encurta_cache.json
```

Mas a solução recomendada é o sistema de 1 link único com sessão.

---

## 16. Favicon personalizado

Criar e adicionar:

```txt
favicon.ico
favicon.svg
favicon-32x32.png
apple-touch-icon.png
android-chrome-192x192.png
site.webmanifest
```

Tags no `<head>`:

```html
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#080b13">
```

---

## 17. Palavras-chave genéricas

Usar conforme o nicho e autorização do conteúdo.

### Gerais

```txt
filmes 2026
filmes lançamentos
filmes dublados
filmes legendados
filmes dual áudio
filmes 1080p
filmes em alta
lançamentos de filmes
catálogo de filmes
```

### Categorias

```txt
filmes de ação
filmes de terror
filmes de suspense
filmes de comédia
filmes de romance
filmes de aventura
filmes de animação
filmes de ficção científica
filmes documentários
```

### Long-tail

```txt
nome do filme trailer
nome do filme sinopse
nome do filme dublado
nome do filme legendado
nome do filme 1080p
nome do filme dual áudio
```

---

## 18. Checklist final para qualquer novo site

Antes de entregar:

```txt
[ ] Capas corretas
[ ] Botões indesejados removidos
[ ] Tema responsivo
[ ] Busca funcionando
[ ] Animação suave
[ ] Carregamento progressivo
[ ] Favicon adicionado
[ ] SEO base aplicado
[ ] Páginas /filme/slug/ funcionando
[ ] Sitemap com todas as URLs
[ ] Robots.txt correto
[ ] .htaccess correto
[ ] Encurtador configurado, se solicitado
[ ] links.php/config.php/movies.php bloqueados
[ ] ZIP final criado
```

Testar URLs:

```txt
https://dominio.com/
https://dominio.com/filme/algum-slug/
https://dominio.com/sitemap.xml
https://dominio.com/favicon.ico
```

Testar fluxo de download:

```txt
site → baixar → start.php → encurtador → download.php → magnet
```

---

## 19. Como usar esta skill em nova conversa

Enviar este arquivo e dizer:

```txt
Use esta skill genérica para modificar meu novo site torrent/catálogo. Quero aplicar o mesmo processo neste novo projeto.
```

Também enviar:

```txt
URL do site
ZIP ou HTML atual
domínio final
hospedagem
link do encurtador, se houver
```

---

## 20. Resultado esperado

Ao final de um novo projeto, entregar:

```txt
site_final_hostinger.zip
```

Com estrutura pronta para upload:

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
