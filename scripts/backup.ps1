# scripts/backup.ps1 - Резервное копирование БД для Windows
Write-Host "🚀 Создание бэкапа БД..." -ForegroundColor Green

$BackupDir = ".\backups"
$DBPath = ".\currencies.db"
$Date = Get-Date -Format "yyyyMMdd_HHmmss"
$MaxBackups = 30

# Создаём папку
if (!(Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
}

# Копируем БД
$BackupFile = "$BackupDir\currencies_backup_$Date.db"
Copy-Item $DBPath $BackupFile
Write-Host "✅ Создан бэкап: $BackupFile" -ForegroundColor Green

# Удаляем старые (оставляем $MaxBackups)
$Backups = Get-ChildItem "$BackupDir\currencies_backup_*.db" | Sort-Object LastWriteTime
if ($Backups.Count -gt $MaxBackups) {
    $ToDelete = $Backups[0..($Backups.Count - $MaxBackups - 1)]
    $ToDelete | Remove-Item
    Write-Host "🧹 Удалено $($ToDelete.Count) старых бэкапов" -ForegroundColor Yellow
}

Write-Host "📊 Всего бэкапов: $((Get-ChildItem $BackupDir).Count)" -ForegroundColor Cyan
