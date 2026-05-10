#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"
VENV="$ROOT/.venv_local"
PYTHON="$VENV/bin/python"

echo "Starting PFA - Gestion des Achats"
export PYTHONUTF8=1

if [ ! -x "$PYTHON" ]; then
  python3 -m venv "$VENV"
fi

"$PYTHON" -m pip install -r "$BACKEND/requirements.txt"

cd "$BACKEND"
"$PYTHON" manage.py migrate
"$PYTHON" seed_data.py
"$PYTHON" manage.py runserver 127.0.0.1:8000 &
BACKEND_PID=$!

cd "$FRONTEND"
if [ ! -d node_modules ]; then
  npm install
fi
npm run dev -- --host 127.0.0.1 &
FRONTEND_PID=$!

echo ""
echo "Application started."
echo "Frontend: http://localhost:3000"
echo "Backend : http://localhost:8000"
echo "Admin   : http://localhost:8000/admin"
echo ""
echo "Backend PID : $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"

wait
