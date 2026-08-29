<?php
$path = __DIR__ . '/data/links.json.gz';
$raw = @file_get_contents($path);
if ($raw === false) { throw new RuntimeException('Base de links não encontrada.'); }
$json = @gzdecode($raw);
if ($json === false) { throw new RuntimeException('Base de links inválida.'); }
return json_decode($json, true, 512, JSON_THROW_ON_ERROR);
