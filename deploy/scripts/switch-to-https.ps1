param(
  [Parameter(Mandatory = $true)]
  [string]$Domain
)

$ErrorActionPreference = 'Stop'

$templatePath = "deploy/nginx/conf.d/lovezs.https.template.conf"
$targetPath = "deploy/nginx/conf.d/lovezs.https.conf"

if (-not (Test-Path $templatePath)) {
  throw "模板不存在: $templatePath"
}

$content = Get-Content $templatePath -Raw
$content = $content.Replace('{{DOMAIN}}', $Domain)
Set-Content -Path $targetPath -Value $content -Encoding UTF8

Write-Host "已生成 HTTPS Nginx 配置: $targetPath"
Write-Host "下一步: 将 docker-compose.prod.yml 中 nginx 的配置挂载改为 lovezs.https.conf 并开放 443 端口。"

