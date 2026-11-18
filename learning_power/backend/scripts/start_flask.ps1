# 单实例启动 Flask（5000），避免多进程占端口导致 RAG/Agent 404
$ErrorActionPreference = "SilentlyContinue"
$port = 5000
Get-NetTCPConnection -LocalPort $port -State Listen |
  ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
Start-Sleep -Seconds 1

Set-Location (Split-Path $PSScriptRoot -Parent)
$env:PYTHONUTF8 = "1"
if (-not $env:DEBUG) { $env:DEBUG = "False" }

# Embedding 模型已缓存在本地时跳过 HuggingFace 联网检查（直连 huggingface.co 会卡死 RAG 首次调用）
# 首次构建索引用: $env:HF_HUB_OFFLINE="0"; $env:HF_ENDPOINT="https://hf-mirror.com"; npm run rag:index
$env:HF_HUB_OFFLINE = "1"

Write-Host "[start] Flask at http://127.0.0.1:$port (single instance, no reloader)"
python run.py
