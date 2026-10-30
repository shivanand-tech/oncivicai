#!/usr/bin/env bash
# CivicAI - All-In-One Automated Setup & Launch Script for macOS and Linux

set -e

echo "================================================================="
echo "   🚀 CivicAI: Smart Citizen Complaint Management System"
echo "                 All-In-One Automated Launcher"
echo "================================================================="

# 1. Determine script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# 2. Check for Python 3
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Error: Python 3 is not installed or not in PATH."
    exit 1
fi

echo "-> Using Python: $($PYTHON_CMD --version)"

# 3. Create Virtual Environment if not present
if [ ! -d "venv" ]; then
    echo "-> Creating Python virtual environment in ./venv..."
    $PYTHON_CMD -m venv venv
fi

# 4. Activate Virtual Environment
echo "-> Activating virtual environment..."
source venv/bin/activate

# 5. Install Dependencies
echo "-> Installing dependencies from requirements.txt..."
pip install --quiet -r requirements.txt

# 6. Ensure Database is Seeded with 40 Demo Complaints
if [ ! -f "civicai.db" ]; then
    echo "-> Initializing & seeding SQLite database with 40 demo records..."
    python database.py
fi

echo "================================================================="
echo "✅ Setup Complete!"
echo "🌐 Server launching at: http://127.0.0.1:5000"
echo "👉 Press CTRL+C to stop the server"
echo "================================================================="

# 7. Open browser automatically (macOS: open, Linux: xdg-open)
if [[ "$OSTYPE" == "darwin"* ]]; then
    (sleep 2 && open "http://127.0.0.1:5000") &
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    (sleep 2 && which xdg-open &>/dev/null && xdg-open "http://127.0.0.1:5000") &
fi

# 8. Run Flask Server
python app.py

