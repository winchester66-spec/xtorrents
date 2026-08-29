# Fluxo do Encurtador — Sistema com 1 Link Único + PHP Session

Este documento explica como funciona o sistema de monetização por encurtador usado no site.

Objetivo: usar **apenas 1 link encurtado** para monetizar todos os botões de download, sem precisar encurtar centenas de links individualmente.

---

## 1. Visão geral

O fluxo funciona assim:

```txt
Usuário clica em Baixar
↓
start.php salva qual filme/link foi escolhido
↓
start.php redireciona para 1 link encurtado
↓
usuário passa pelo anúncio do encurtador
↓
encurtador redireciona para download.php
↓
download.php lê a sessão e abre o magnet correto
```

---

## 2. Por que usar esse sistema?

O site pode ter centenas de links de download.

Exemplo:

```txt
416 filmes
651 links magnet
```

Se cada link fosse encurtado individualmente, seria necessário criar centenas de links no encurtador.

Com este sistema, todos os downloads usam apenas um link encurtado:

```txt
https://seulink.net/MBAySxG9
```

---

## 3. Arquivos envolvidos

O sistema usa estes arquivos:

```txt
index.html
filme.php
start.php
download.php
links.php
config.php
.htaccess
```

### Função de cada arquivo

| Arquivo | Função |
|---|---|
| `index.html` | Página inicial com os cards dos filmes |
| `filme.php` | Página individual de cada filme |
| `start.php` | Salva o download escolhido na sessão e envia ao encurtador |
| `download.php` | Recebe o usuário depois do encurtador e libera o magnet correto |
| `links.php` | Guarda os magnets reais |
| `config.php` | Guarda o link único do encurtador |
| `.htaccess` | Protege arquivos privados e cria URLs amigáveis |

---

## 4. Etapa 1 — Usuário clica em Baixar

Exemplo de página:

```txt
https://torrentfilms.produtodigital.org/filme/o-fim-da-rua/
```

O botão **Baixar** aponta para:

```txt
https://torrentfilms.produtodigital.org/start.php?id=o-fim-da-rua&link=0
```

Onde:

```txt
id=o-fim-da-rua
```

é o identificador do filme.

E:

```txt
link=0
```

é o primeiro link de download daquele filme.

Se houver mais de um link, podem existir URLs como:

```txt
start.php?id=o-fim-da-rua&link=1
start.php?id=o-fim-da-rua&link=2
```

---

## 5. Etapa 2 — `start.php` salva a escolha

O `start.php` recebe os parâmetros:

```txt
id
link
```

Depois salva na sessão PHP:

```php
$_SESSION['pending_download'] = [
  'id' => 'o-fim-da-rua',
  'link' => 0,
  'time' => time()
];
```

Isso significa:

```txt
Este usuário escolheu baixar o filme o-fim-da-rua, link número 0.
```

Essa informação fica guardada temporariamente para aquele navegador/usuário.

---

## 6. Etapa 3 — Redirecionamento para o encurtador

Depois de salvar a sessão, o `start.php` redireciona para o link único configurado no `config.php`.

Exemplo:

```txt
https://seulink.net/MBAySxG9
```

O arquivo `config.php` fica assim:

```php
<?php
return [
  'encurta_url' => 'https://seulink.net/MBAySxG9'
];
```

---

## 7. Etapa 4 — Usuário passa pelo anúncio

O usuário chega ao encurtador e passa pelo anúncio.

Este é o ponto de monetização.

Fluxo:

```txt
start.php
↓
https://seulink.net/MBAySxG9
↓
anúncio do encurtador
```

---

## 8. Etapa 5 — Encurtador volta para `download.php`

O link encurtado deve ter como destino final:

```txt
https://torrentfilms.produtodigital.org/download.php
```

Depois que o usuário passa pelo anúncio, ele é enviado para:

```txt
download.php
```

---

## 9. Etapa 6 — `download.php` lê a sessão

O `download.php` verifica a sessão:

```php
$_SESSION['pending_download']
```

Se encontrar os dados, ele sabe qual filme o usuário escolheu.

Exemplo:

```txt
id = o-fim-da-rua
link = 0
```

---

## 10. Etapa 7 — `download.php` procura o magnet correto

O `download.php` consulta o arquivo:

```txt
links.php
```

O `links.php` contém os magnets reais.

Exemplo simplificado:

```php
[
  'o-fim-da-rua' => [
    'magnet:?xt=urn:btih:...',
    'magnet:?xt=urn:btih:...'
  ],
  'homem-aranha-um-novo-dia' => [
    'magnet:?xt=urn:btih:...'
  ]
]
```

Se a sessão indicar:

```txt
id=o-fim-da-rua
link=0
```

o sistema libera o primeiro magnet do filme `o-fim-da-rua`.

---

## 11. Etapa 8 — Magnet é aberto

Depois de encontrar o magnet correto, o `download.php` exibe uma pequena tela:

```txt
Download liberado
```

E redireciona automaticamente para:

```txt
magnet:?xt=urn:btih:...
```

O navegador então tenta abrir o aplicativo torrent do usuário.

---

## 12. Fluxo completo visual

```txt
Usuário clica Baixar
        ↓
start.php?id=o-fim-da-rua&link=0
        ↓
Salva na sessão:
id=o-fim-da-rua
link=0
        ↓
Redireciona para:
https://seulink.net/MBAySxG9
        ↓
Usuário passa pelo anúncio
        ↓
Encurtador envia para:
download.php
        ↓
download.php lê a sessão
        ↓
Procura magnet em links.php
        ↓
Abre o magnet correto
```

---

## 13. Vantagens desse sistema

### 1. Usa apenas 1 link encurtado

Não é necessário criar centenas de links.

```txt
651 links magnet → 1 único link encurtado
```

### 2. Evita limite diário do encurtador

Muitos encurtadores limitam a criação de links por dia.

Com esse sistema, só é necessário criar 1 link.

### 3. Monetiza todos os downloads

Todo botão **Baixar** passa pelo mesmo encurtador.

### 4. Facilita manutenção

Para trocar o encurtador, basta editar:

```txt
config.php
```

### 5. Esconde os magnets do HTML público

Os magnets reais não ficam no `index.html`.

Eles ficam em:

```txt
links.php
```

### 6. Funciona bem na Hostinger

A Hostinger suporta PHP e sessão, então esse fluxo funciona bem em hospedagem compartilhada.

---

## 14. Cuidados importantes

### O link encurtado não deve ser aberto diretamente

Se o usuário abrir direto:

```txt
https://seulink.net/MBAySxG9
```

sem antes clicar no botão **Baixar**, o `download.php` não saberá qual filme liberar.

Nesse caso, é normal aparecer:

```txt
Acesso expirado
```

Isso não é erro.

---

## 15. Teste correto

O teste correto é:

```txt
1. Acessar o site
2. Clicar em um filme
3. Clicar em Baixar
4. Passar pelo encurtador
5. Voltar para download.php
6. Conferir se o magnet abre
```

Exemplo:

```txt
https://torrentfilms.produtodigital.org/
↓
/filme/o-fim-da-rua/
↓
/start.php?id=o-fim-da-rua&link=0
↓
https://seulink.net/MBAySxG9
↓
/download.php
↓
magnet correto
```

---

## 16. `.htaccess` recomendado

O `.htaccess` deve proteger arquivos sensíveis:

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

Também pode conter a rota das páginas de filmes:

```apache
RewriteEngine On
RewriteRule ^filme/([A-Za-z0-9-]+)/?$ filme.php?slug=$1 [L,QSA]
```

---

## 17. Exemplo de `config.php`

```php
<?php
return [
  'encurta_url' => 'https://seulink.net/MBAySxG9'
];
```

---

## 18. Exemplo de botão de download

Na página do filme, o botão deve apontar para:

```html
<a href="/start.php?id=o-fim-da-rua&link=0" rel="nofollow">
  🧲 Baixar
</a>
```

Não apontar diretamente para:

```txt
magnet:?xt=urn:btih:...
```

---

## 19. Erros comuns

### Erro: `Acesso expirado`

Causa:

```txt
Usuário abriu download.php diretamente ou a sessão expirou.
```

Solução:

```txt
Voltar ao site e clicar novamente no botão Baixar.
```

### Erro 500

Possíveis causas:

```txt
Erro de sintaxe em links.php
Erro de sintaxe em config.php
PHP incompatível
.htaccess inválido
```

### Erro 404 em `/filme/slug/`

Possíveis causas:

```txt
.htaccess ausente
mod_rewrite inativo
filme.php ausente
movies.php ausente
arquivos enviados para pasta errada
```

---

## 20. Resumo em uma frase

O site salva o download escolhido em uma sessão, envia o usuário para um único link encurtado monetizado e, quando ele volta do encurtador, libera automaticamente o magnet correto.
