#!/usr/bin/env bash
# Launcher for macOS and Linux: installs everything needed on first run, then starts the automation.
set -e
cd "$(dirname "$0")"

pause() { read -r -p "Press Enter to close this window..." _ || true; }
trap 'echo; echo "❌ Something went wrong (see the message above)."; pause' ERR

export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

if ! command -v uv >/dev/null 2>&1; then
    echo "📦 First run: installing uv (one time only, no admin needed)..."
    if command -v curl >/dev/null 2>&1; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
    else
        wget -qO- https://astral.sh/uv/install.sh | sh
    fi
fi

echo "📦 Checking Python and packages..."
uv sync

echo "🌐 Checking WebKit browser..."
uv run playwright install webkit

if [ "$(uname)" = "Linux" ] && [ ! -f .venv/.linux-deps-installed ]; then
    echo "🔧 First run on Linux: installing browser system libraries (may ask for your computer password)..."
    if uv run playwright install-deps webkit; then
        touch .venv/.linux-deps-installed
    else
        echo "⚠ Could not install them automatically. If the browser fails to open, see README > If something goes wrong."
    fi
fi

uv run binus_automation.py
