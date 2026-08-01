try {
    $tcp = New-Object System.Net.Sockets.TcpClient("localhost", 5432)
    $tcp.Close()
    Write-Host "[INFO] PostgreSQL is active on localhost:5432. Connecting to PostgreSQL database..." -ForegroundColor Green
    $env:DATABASE_URL="postgresql+asyncpg://xecurity:password@localhost:5432/xecurity_platform"
} catch {
    Write-Host "[WARN] PostgreSQL is not reachable on port 5432. Falling back to local SQLite database (dev.db)..." -ForegroundColor Yellow
    $env:DATABASE_URL="sqlite+aiosqlite:///./dev.db"
}

$env:PYTHONPATH="."
uv run uvicorn app.main:app --reload --port 8080
