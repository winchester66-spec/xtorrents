<?php
// start.php / iniciar.php
// Salva o download escolhido em sessão + cookie e redireciona para o link único do encurtador.

session_start();

$linksFile = __DIR__ . '/links.php';
$configFile = __DIR__ . '/config.php';

if (!file_exists($linksFile)) {
  http_response_code(500);
  echo 'Erro: links.php não encontrado.';
  exit;
}

$links = require $linksFile;
$config = file_exists($configFile) ? require $configFile : [];

$id = isset($_GET['id']) ? preg_replace('/[^a-z0-9\-]/i', '', $_GET['id']) : '';
$idx = isset($_GET['link']) ? intval($_GET['link']) : 0;

if (!$id || !isset($links[$id]) || !isset($links[$id][$idx])) {
  http_response_code(404);
  echo '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><title>Download não encontrado</title><style>body{font-family:Arial;background:#080b13;color:#fff;text-align:center;padding:40px}a{color:#ffc400}</style></head><body><h1>Download não encontrado</h1><p>Volte ao catálogo e tente novamente.</p><a href="/">Voltar</a></body></html>';
  exit;
}

$payload = [
  'id' => $id,
  'link' => $idx,
  'time' => time()
];

// Grava em múltiplas chaves para compatibilidade.
$_SESSION['pending_download'] = $payload;
$_SESSION['download'] = $payload;
$_SESSION['selected_download'] = $payload;
$_SESSION['download_id'] = $id;
$_SESSION['download_link'] = $idx;
$_SESSION['download_time'] = time();

// Fallback importante: alguns encurtadores quebram a continuidade da sessão.
// Por isso também salvamos em cookie próprio do domínio.
$cookieValue = base64_encode(json_encode($payload, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE));
$secure = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off');
setcookie('xt_pending_download', $cookieValue, [
  'expires' => time() + 3600,
  'path' => '/',
  'secure' => $secure,
  'httponly' => true,
  'samesite' => 'Lax'
]);

// Garante que a sessão foi gravada antes de sair para domínio externo.
session_write_close();

$short = trim($config['encurta_url'] ?? $config['short_url'] ?? $config['shortener_url'] ?? '');
$placeholder = 'COLE_AQUI_SEU_LINK_ENCURTADO_DO_ENCURTA_NET';

// Se config.php ainda não tiver link, cai direto no download.php para teste.
if (!$short || $short === $placeholder) {
  $short = '/download.php';
}

header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
header('Pragma: no-cache');
header('Location: ' . $short, true, 302);
exit;
