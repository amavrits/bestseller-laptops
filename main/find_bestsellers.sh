#!/bin/bash

echo "🚀 Starting pipeline..."

cd "$(dirname "$0")/.."  # Go to project root

source .venv/bin/activate

export PYTHONPATH=$(pwd)

# Confirm setup
echo "🔍 Current working directory: $(pwd)"
echo "🐍 PYTHONPATH set to: $PYTHONPATH"

echo "🧲 Running amazon_webscrapper.py..."
python -m main.find_bestsellers.amazon_webscraping

echo "📝 Running collect_reviews.py..."
python -m main.find_bestsellers.collect_reviews

echo "🧠 Running summarize_reviews.py..."
python -m main.find_bestsellers.summarize_reviews

echo "📊 Running merge_summaries.py..."
python -m main.find_bestsellers.merge_summaries

echo "Running extract_brand_model.py..."
python -m main.find_bestsellers.extract_brand_model

echo "Running finalize_csv.py..."
python -m main.find_bestsellers.finalize_csv

echo "✅ All scripts completed successfully!"


