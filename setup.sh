#!/bin/bash (./setup.sh to run)

# Fail on error
set -e

echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "⬇️ Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "📂 Exporting environment variables..."
# You may also want to put these in a real .env file and use python-dotenv for local dev
export FLASK_APP=run.py
export FLASK_ENV=development

echo "🔧 Setting up database (only once required)"
flask db init || true
flask db migrate -m "Initial migration"
flask db upgrade

echo "✅ Setup complete!"
