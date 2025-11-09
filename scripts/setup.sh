#!/bin/bash
# Setup script for RiskLens AI

echo "=========================================="
echo "RiskLens AI - Setup Script"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p data
mkdir -p state
mkdir -p logs
mkdir -p output

# Copy environment template if .env doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp ENV_TEMPLATE .env
    echo "⚠️  IMPORTANT: Edit .env and add your NVIDIA_API_KEY"
fi

# Generate sample PDFs
echo ""
echo "Generating sample PDFs..."
python scripts/create_sample_pdfs.py

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env and add your NVIDIA_API_KEY"
echo "2. Get API key from: https://build.nvidia.com/"
echo "3. Run: source venv/bin/activate"
echo "4. Run: python main.py --pdf data/sample_vendor_acme.pdf"
echo ""

