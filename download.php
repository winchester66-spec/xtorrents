<?php
// download.php
// Recebe o usuário depois do encurtador e libera o magnet correto.
// Agora lê sessão e também cookie de fallback.

session_start();

$linksFile = __DIR__ . '/links.php';
if (!file_exists($linksFile)) {
  http_response_code(500);
  echo 'Erro: links.php não encontrado.';
  exit;
}
$links = require $linksFile;

function fail_page($title, $msg, $code = 403) {
  http_response_code($code);
  echo '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>'.htmlspecialchars($title, ENT_QUOTES, 'UTF-8').'</title><style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#080b13;color:#fff;font-family:Arial,sans-serif}.box{width:min(92vw,580px);background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.12);border-radius:20px;padding:28px;text-align:center}h1{color:#ffc400}a{color:#ffc400}</style></head><body><div class="box"><h1>'.htmlspecialchars($title, ENT_QUOTES, 'UTF-8').'</h1><p>'.htmlspecialchars($msg, ENT_QUOTES, 'UTF-8').'</p><a href="/">Voltar ao catálogo</a></div></body></html>';
  exit;
}

function read_cookie_payload() {
  if (empty($_COOKIE['xt_pending_download'])) return null;
  $raw = base64_decode($_COOKIE['xt_pending_download'], true);
  if (!$raw) return null;
  $data = json_decode($raw, true);
  return is_array($data) ? $data : null;
}

$pending = $_SESSION['pending_download'] ?? $_SESSION['download'] ?? $_SESSION['selected_download'] ?? null;

$id = null;
$idx = 0;
$time = time();

if (is_array($pending)) {
  $id = $pending['id'] ?? $pending['slug'] ?? $pending['movie'] ?? null;
  $idx = isset($pending['link']) ? intval($pending['link']) : (isset($pending['index']) ? intval($pending['index']) : 0);
  $time = isset($pending['time']) ? intval($pending['time']) : time();
}

// Compatibilidade com sessão simples.
if (!$id && isset($_SESSION['download_id'])) {
  $id = $_SESSION['download_id'];
  $idx = isset($_SESSION['download_link']) ? intval($_SESSION['download_link']) : 0;
  $time = isset($_SESSION['download_time']) ? intval($_SESSION['download_time']) : time();
}

// Fallback por cookie caso a sessão não tenha sobrevivido ao encurtador.
if (!$id) {
  $cookiePayload = read_cookie_payload();
  if ($cookiePayload) {
    $id = $cookiePayload['id'] ?? null;
    $idx = isset($cookiePayload['link']) ? intval($cookiePayload['link']) : 0;
    $time = isset($cookiePayload['time']) ? intval($cookiePayload['time']) : time();
  }
}

if (!$id) {
  fail_page('Acesso expirado', 'Volte ao site e clique novamente no botão Baixar. O download precisa começar pelo catálogo.');
}

$id = preg_replace('/[^a-z0-9\-]/i', '', $id);

if (time() - intval($time) > 3600) {
  unset($_SESSION['pending_download'], $_SESSION['download'], $_SESSION['selected_download'], $_SESSION['download_id'], $_SESSION['download_link'], $_SESSION['download_time']);
  setcookie('xt_pending_download', '', ['expires' => time() - 3600, 'path' => '/']);
  fail_page('Download expirado', 'A sessão de download expirou. Volte ao site e clique novamente em Baixar.');
}

$url = $links[$id][$idx] ?? null;
if (!$url) {
  fail_page('Link não encontrado', 'Não foi possível encontrar o magnet deste título. Slug: '.$id.' / link: '.$idx, 404);
}

// Limpa depois de usar para evitar repetir download antigo ao abrir o encurtador direto depois.
unset($_SESSION['pending_download'], $_SESSION['download'], $_SESSION['selected_download'], $_SESSION['download_id'], $_SESSION['download_link'], $_SESSION['download_time']);
setcookie('xt_pending_download', '', ['expires' => time() - 3600, 'path' => '/']);

$safe = htmlspecialchars($url, ENT_QUOTES, 'UTF-8');
?>
<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Download liberado</title>
<style>
body{margin:0;min-height:100vh;display:grid;place-items:center;background:radial-gradient(circle at top,#1a2440,#080b13 55%,#05060a);color:#fff;font-family:Arial,sans-serif}.box{width:min(92vw,520px);background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.12);border-radius:20px;padding:28px;text-align:center;box-shadow:0 24px 60px rgba(0,0,0,.4)}h1{margin:0 0 10px;color:#ffc400}.loader{width:46px;height:46px;border:4px solid rgba(255,255,255,.18);border-top-color:#ffc400;border-radius:50%;margin:18px auto;animation:spin 1s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}a.btn{display:inline-block;margin-top:14px;background:linear-gradient(90deg,#ffc400,#ff7a18);color:#160f00;text-decoration:none;font-weight:900;padding:12px 18px;border-radius:999px}.muted{color:#b8c0d0;font-size:.9rem}.back{display:block;margin-top:16px;color:#ffc400;text-decoration:none;font-size:.85rem}
</style>
</head>
<body>
<div class="box">
  <h1>Download liberado</h1>
  <p class="muted">O magnet será aberto automaticamente. Se não abrir, clique no botão abaixo.</p>
  <div class="loader"></div>
  <a class="btn" id="go" href="<?= $safe ?>">Abrir download</a>
  <a class="back" href="/">Voltar ao catálogo</a>
</div>
<script>
setTimeout(function(){ window.location.href = document.getElementById('go').href; }, 900);
</script>
</body>
</html>
