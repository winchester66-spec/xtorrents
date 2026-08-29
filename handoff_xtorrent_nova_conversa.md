# Handoff do Projeto — x-torrent

Use este arquivo em uma nova conversa para continuar o trabalho no site **x-torrent**.

---

## 1. Site principal

Domínio:

```txt
https://xtorrent.produtodigital.org/
```

Nome do site:

```txt
x-torrent
```

Tipo:

```txt
Catálogo de filmes e séries com páginas individuais, busca, filtros e sistema de download via encurtador.
```

Hospedagem:

```txt
Hostinger
```

Pasta observada na Hostinger:

```txt
public_html
```

---

## 2. Site fonte dos magnets

Os links magnéticos aplicados no site x-torrent vieram deste site hospedado na Netlify:

```txt
https://sage-semolina-16fcfe.netlify.app/
```

Esse site contém os cards com:

- capa;
- categorias;
- descrição;
- hash;
- link magnet;
- postagem original.

Foi usado para gerar o arquivo privado:

```txt
links.php
```

---

## 3. Estado atual do catálogo

Ao analisar o site principal:

```txt
https://xtorrent.produtodigital.org/
```

foi identificado que o catálogo usa no HTML uma variável JavaScript:

```js
window.XT_CATALOG = [...]
```

Quantidade atual:

```txt
5.683 títulos no catálogo
```

Sitemap gerado posteriormente:

```txt
5.684 URLs
```

Sendo:

```txt
1 página inicial
5.683 páginas individuais de filmes/séries
```

---

## 4. Estrutura de URLs

Página inicial:

```txt
https://xtorrent.produtodigital.org/
```

Páginas individuais:

```txt
https://xtorrent.produtodigital.org/filme/ghost-in-the-cell/
https://xtorrent.produtodigital.org/filme/o-fim-da-rua/
https://xtorrent.produtodigital.org/filme/a-captura/
https://xtorrent.produtodigital.org/filme/a-morte-do-demonio-em-chamas/
```

Exemplo de página testada com sucesso:

```txt
https://xtorrent.produtodigital.org/filme/ghost-in-the-cell/
```

Ela mostra:

- capa;
- título;
- ano;
- qualidade;
- tipo;
- categorias;
- sinopse;
- botão “Abrir download autorizado”.

---

## 5. Fluxo do download/encurtador

O fluxo correto do site é:

```txt
Usuário entra em uma página de filme
↓
Clica em Abrir download autorizado
↓
start.php ou iniciar.php salva id/link em sessão/cookie
↓
Redireciona para o encurtador
↓
Usuário passa pelo anúncio
↓
Encurtador volta para download.php
↓
download.php lê sessão/cookie
↓
Procura magnet em links.php
↓
Abre o magnet correto
```

---

## 6. Arquivos importantes no Hostinger

No print da Hostinger foram vistos estes arquivos/pastas:

```txt
public_html/
├── dados/
├── filme/
├── .htaccess
├── android-chrome-192x192.png
├── apple-touch-icon.png
├── config.php
├── favicon-32x32.png
├── favicon.ico
├── favicon.svg
├── index.html
├── LEIA-ME.txt
├── links-loader.php
├── og-image.svg
├── relatorio-seo.csv
├── robots.txt
├── site.webmanifest
├── sitemap.xml
└── iniciar.php
```

Depois foi necessário adicionar/corrigir também:

```txt
download.php
links.php
start.php
iniciar.php
```

---

## 7. Problema encontrado: download.php ausente

Erro observado:

```txt
https://xtorrent.produtodigital.org/download.php
```

retornava:

```txt
404 — Esta página não existe
```

Causa:

```txt
O arquivo download.php não existia no public_html.
```

Correção realizada:

Foi gerado o pacote:

```txt
correcao_xtorrent_download_php.zip
```

Contendo:

```txt
download.php
links.php
htaccess_snippet.txt
```

O `links.php` foi gerado a partir do site fonte:

```txt
https://sage-semolina-16fcfe.netlify.app/
```

---

## 8. Problema encontrado: Acesso expirado após o encurtador

Depois de adicionar o `download.php`, o site passou a mostrar:

```txt
Acesso expirado
Volte ao site e clique novamente no botão Baixar. O download precisa começar pelo catálogo.
```

Mesmo clicando em um filme, depois de passar pelo encurtador a mensagem persistia.

Causa provável:

```txt
A sessão PHP criada antes do encurtador não estava chegando corretamente ao download.php.
```

Correção realizada:

Foi gerado o pacote:

```txt
correcao_xtorrent_sessao_cookie.zip
```

Contendo:

```txt
start.php
iniciar.php
download.php
LEIA-ME.txt
```

Essa correção salvou o download escolhido de duas formas:

```txt
1. Sessão PHP
2. Cookie de fallback chamado xt_pending_download
```

Depois da correção, o usuário informou que:

```txt
funcionou normalmente
```

---

## 9. Observação sobre download.php

Abrir diretamente:

```txt
https://xtorrent.produtodigital.org/download.php
```

pode mostrar:

```txt
Acesso expirado
```

Isso é normal.

O teste correto é sempre:

```txt
site → página do filme → botão download → encurtador → download.php → magnet
```

---

## 10. Encurtador atual observado

Ao testar:

```txt
https://xtorrent.produtodigital.org/start.php?id=ghost-in-the-cell&link=0
```

foi observado redirecionamento para:

```txt
https://cl1ca.com/RTagzFOBKd
```

Esse link abre uma página do EncurtaNet/encurtador.

Importante: o link encurtado precisa ter como destino final:

```txt
https://xtorrent.produtodigital.org/download.php
```

---

## 11. links.php

O `links.php` contém os magnets reais organizados por slug.

Exemplos confirmados no arquivo gerado:

```txt
ghost-in-the-cell
o-fim-da-rua
a-captura
outer-banks-1a-a-5a-temporada
pinoquio-maldicao-de-madeira
a-morte-do-demonio-em-chamas
sterling-point-1a-temporada
```

Quantidade aproximada extraída do site fonte:

```txt
5.636 slugs
5.671 referências de magnets
```

Observação: o site principal tem 5.683 títulos, então alguns itens podem não ter magnet ou podem ter slugs ligeiramente diferentes.

---

## 12. Sitemap gerado para Google Search Console

Foi gerado o pacote:

```txt
sitemap_xtorrent_google.zip
```

Contendo:

```txt
sitemap.xml
robots.txt
```

Quantidade:

```txt
5.684 URLs no sitemap
```

Sendo:

```txt
https://xtorrent.produtodigital.org/
+ 5.683 URLs /filme/slug/
```

Exemplos:

```txt
https://xtorrent.produtodigital.org/
https://xtorrent.produtodigital.org/filme/a-morte-do-demonio-em-chamas/
https://xtorrent.produtodigital.org/filme/sterling-point-1a-temporada/
https://xtorrent.produtodigital.org/filme/a-odisseia/
https://xtorrent.produtodigital.org/filme/amor-romance-casamento/
```

Últimas URLs observadas:

```txt
https://xtorrent.produtodigital.org/filme/ultimas-palavras/
https://xtorrent.produtodigital.org/filme/ultimo-alvo/
https://xtorrent.produtodigital.org/filme/serie-ultimo-ato-1a-temporada/
https://xtorrent.produtodigital.org/filme/ubel-blatt-1a-temporada/
https://xtorrent.produtodigital.org/filme/o-morro-dos-ventos-uivantes/
```

---

## 13. Robots.txt recomendado

Conteúdo recomendado:

```txt
User-agent: *
Allow: /
Disallow: /start.php
Disallow: /iniciar.php
Disallow: /download.php
Sitemap: https://xtorrent.produtodigital.org/sitemap.xml
```

---

## 14. Search Console

Enviar ao Google Search Console:

```txt
sitemap.xml
```

URL completa:

```txt
https://xtorrent.produtodigital.org/sitemap.xml
```

Após subir o sitemap, testar no navegador:

```txt
https://xtorrent.produtodigital.org/sitemap.xml
```

Deve abrir XML começando com:

```xml
<urlset
```

---

## 15. SEO atual observado

Página inicial tem:

```txt
Title: x-torrent — Catálogo de filmes e séries
Description: Explore o catálogo x-torrent de filmes e séries, com busca rápida, filtros e páginas individuais.
Canonical: https://xtorrent.produtodigital.org/
```

Página individual testada:

```txt
https://xtorrent.produtodigital.org/filme/ghost-in-the-cell/
```

Title observado:

```txt
Ghost in the Cell (2026) — Sinopse e informações | x-torrent
```

A página tem conteúdo indexável com:

- capa;
- título;
- categorias;
- ano;
- qualidade;
- sinopse;
- relacionados.

---

## 16. Estrutura técnica observada no HTML

O catálogo é carregado em:

```js
window.XT_CATALOG = [...]
```

O JS final usa:

```js
const all = window.XT_CATALOG || []
```

Elementos observados:

```txt
#grid
#searchInput
#searchForm
#typeFilter
#yearFilter
#categoryFilter
```

O site renderiza os itens do catálogo via JavaScript.

---

## 17. Favicon e identidade visual

No Hostinger existem arquivos:

```txt
favicon.ico
favicon.svg
favicon-32x32.png
apple-touch-icon.png
android-chrome-192x192.png
site.webmanifest
og-image.svg
```

---

## 18. Se precisar criar novo encurtador

O destino do encurtador deve ser:

```txt
https://xtorrent.produtodigital.org/download.php
```

Depois colocar o novo link encurtado em:

```txt
config.php
```

Exemplo:

```php
<?php
return [
  'encurta_url' => 'https://SEU-ENCURTADOR/NOVO-LINK'
];
```

---

## 19. Se o download voltar a dar acesso expirado

Aplicar novamente a correção:

```txt
correcao_xtorrent_sessao_cookie.zip
```

Arquivos essenciais:

```txt
start.php
iniciar.php
download.php
```

O `start.php/iniciar.php` deve salvar:

```txt
$_SESSION['pending_download']
$_SESSION['download']
$_SESSION['selected_download']
$_SESSION['download_id']
$_SESSION['download_link']
$_SESSION['download_time']
```

E também cookie:

```txt
xt_pending_download
```

O `download.php` deve ler sessão e depois cookie de fallback.

---

## 20. Se o magnet não for encontrado

Mensagem provável:

```txt
Link não encontrado
Não foi possível encontrar o magnet deste título. Slug: slug-do-filme / link: 0
```

Causas possíveis:

- slug do site principal diferente do slug do `links.php`;
- item sem magnet no site fonte;
- dados do Netlify incompletos;
- `links.php` desatualizado.

Solução:

- reextrair magnets do site fonte;
- garantir que o slug usado no x-torrent exista no `links.php`;
- adicionar aliases de slug quando necessário.

---

## 21. Arquivos gerados durante o atendimento

Pacotes/arquivos relevantes:

```txt
correcao_xtorrent_download_php.zip
correcao_xtorrent_sessao_cookie.zip
sitemap_xtorrent_google.zip
fluxo_encurtador_antigravity.md
skill_generica_sites_torrent.zip
skill_sites_torrent_generica.md
```

---

## 22. Checklist para nova conversa

Ao continuar este projeto, verificar:

```txt
[ ] Site principal abre: https://xtorrent.produtodigital.org/
[ ] Página de filme abre: /filme/ghost-in-the-cell/
[ ] download.php existe
[ ] links.php existe
[ ] start.php existe
[ ] iniciar.php existe
[ ] config.php contém link do encurtador
[ ] fluxo do download funciona depois do encurtador
[ ] sitemap.xml existe e abre
[ ] robots.txt aponta para sitemap.xml
[ ] Google Search Console recebeu sitemap.xml
```

---

## 23. Instrução para usar em nova conversa

Em uma nova conversa, envie este arquivo e diga:

```txt
Use este handoff como contexto completo do projeto x-torrent. Continue a partir dessas informações.
```

Se possível, enviar também os arquivos atuais do Hostinger, especialmente:

```txt
index.html
config.php
start.php
iniciar.php
download.php
links.php
sitemap.xml
robots.txt
.htaccess
```
