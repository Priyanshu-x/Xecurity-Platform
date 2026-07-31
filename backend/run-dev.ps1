$env:DATABASE_URL="postgresql+asyncpg://xecurity:password@localhost:5432/xecurity_platform"
$env:PYTHONPATH="."
uv run uvicorn app.main:app --reload --port 8080
