# EcoGuard Backend Startup Script
Write-Host "Starting EcoGuard Backend (Stability Mode)..."

# [v1.4] Fix forrtl: error (200) on Windows
$env:FOR_DISABLE_CONSOLE_CTRL_HANDLER = "T"
$env:OMP_NUM_THREADS = "1"

cd backend
python -u -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
