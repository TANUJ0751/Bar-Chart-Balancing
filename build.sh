#!/usr/bin/env bash
set -e

echo "=== System update ==="
apt-get update

echo "=== Install Chrome dependencies ==="
apt-get install -y wget gnupg apt-transport-https ca-certificates

echo "=== Install Chromium (lighter than Google Chrome) ==="
# Debian/Ubuntu packages vary; try chromium or chromium-browser
apt-get install -y chromium || apt-get install -y chromium-browser || true

echo "=== Python deps ==="
pip install --upgrade pip
pip install -r requirements.txt

echo "=== Pre-warm Kaleido Chrome discovery ==="
python - <<'EOF'
import os
import kaleido
# Try to register chromium path if needed
# If chromium is not auto-discovered, set env var
for candidate in ("/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome"):
    if os.path.exists(candidate):
        os.environ["KaleidoExecutablePath"] = candidate
        break
# Trigger lazy init (ignore errors)
try:
    kaleido.get_chrome_sync()
except Exception as e:
    print("Kaleido chrome warmup warning:", e)
EOF
