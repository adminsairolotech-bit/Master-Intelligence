Get-Process -Name chrome | Measure-Object WorkingSet -Sum | ForEach-Object {
    Write-Host "=== AI Command Center Performance ==="
    Write-Host "Chrome Processes: $($_.Count)"
    Write-Host "Total RAM: $([math]::Round($_.Sum/1MB,0)) MB"
    Write-Host "====================================="
}