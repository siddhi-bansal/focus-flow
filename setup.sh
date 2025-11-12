#!/usr/bin/env zsh

# 🎯 FocusPulse Quick Start Script
# Run this once to set everything up

set -e  # Exit on error

echo "🎯 FocusPulse Setup Script"
echo "=========================="
echo ""

# Check Python version
echo "✓ Checking Python..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Found Python $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "✓ Creating virtual environment..."
    python3 -m venv venv
    echo "  ✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "✓ Installing dependencies..."
pip install -q -r requirements.txt
echo "  ✓ All packages installed"

# Create data directory
mkdir -p data

echo ""
echo "=========================="
echo "✅ Setup Complete!"
echo ""
echo "🚀 Next Steps:"
echo ""
echo "1. Start the tracker (in terminal 1):"
echo "   python -m src.tracker"
echo ""
echo "2. View the dashboard (in terminal 2):"
echo "   streamlit run app.py"
echo ""
echo "3. Open your browser to:"
echo "   http://localhost:8501"
echo ""
echo "📖 See IMPLEMENTATION_GUIDE.md for detailed docs"
echo ""
