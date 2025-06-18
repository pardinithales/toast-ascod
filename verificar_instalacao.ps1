# Script para verificar instalação do Node.js e npm
Write-Host "Verificando instalação do Node.js e npm..." -ForegroundColor Cyan
Write-Host ""

# Verifica Node.js
try {
    $nodeVersion = node --version
    Write-Host "✓ Node.js instalado: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js NÃO está instalado" -ForegroundColor Red
}

# Verifica npm
try {
    $npmVersion = npm --version
    Write-Host "✓ npm instalado: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ npm NÃO está instalado" -ForegroundColor Red
}

Write-Host ""
Write-Host "Se ambos estiverem instalados, você pode executar:" -ForegroundColor Yellow
Write-Host "  npm install" -ForegroundColor White
Write-Host "  node index.js" -ForegroundColor White 