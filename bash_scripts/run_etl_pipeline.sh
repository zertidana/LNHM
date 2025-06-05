#!/bin/bash
# Run full ETL pipeline.

echo "🔧 Activating virtual environment..."

source ../venv/bin/activate

echo "🚰 Extracting 🚰"
python ../extract.py

echo "🧹 Transforming 🧹"
python ../transform.py

echo "📥 Loading 📥"
python ../load.py

echo "✅ ETL Pipeline complete ✅"