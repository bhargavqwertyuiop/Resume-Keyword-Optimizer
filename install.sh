#!/bin/bash

# Resume Keyword Optimizer - Installation Script
# This script sets up the Resume Keyword Optimizer tool

echo "🎯 Resume Keyword Optimizer - Installation Script"
echo "=================================================="

# Check if Python 3.8+ is installed
echo "📋 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
REQUIRED_VERSION="3.8"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check Python version
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "❌ Python 3.8+ is required. You have Python $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Check if pip is installed
echo "📦 Checking pip..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip first."
    exit 1
fi

echo "✅ pip3 is available"

# Create virtual environment (optional but recommended)
read -p "🤔 Would you like to create a virtual environment? (recommended) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🏗️  Creating virtual environment..."
    python3 -m venv resume_optimizer_env
    
    echo "🔧 Activating virtual environment..."
    source resume_optimizer_env/bin/activate
    
    echo "✅ Virtual environment created and activated"
    echo "💡 To activate later, run: source resume_optimizer_env/bin/activate"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install --upgrade pip

if pip3 install -r requirements.txt; then
    echo "✅ Python dependencies installed successfully"
else
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

# Download spaCy model
echo "🧠 Downloading spaCy English model..."
if python3 -m spacy download en_core_web_sm; then
    echo "✅ spaCy model downloaded successfully"
else
    echo "❌ Failed to download spaCy model"
    echo "💡 You can try downloading it manually: python3 -m spacy download en_core_web_sm"
fi

# Test installation
echo "🧪 Testing installation..."
if python3 -c "
import nltk
import spacy
import streamlit
from resume_optimizer import ResumeKeywordOptimizer
print('✅ All imports successful!')
"; then
    echo "✅ Installation test passed!"
else
    echo "❌ Installation test failed"
    echo "💡 Please check the error messages above"
    exit 1
fi

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x cli.py
chmod +x demo.py

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "🚀 Quick Start Options:"
echo "1. Run demo:           python3 demo.py"
echo "2. Web interface:      streamlit run web_app.py"
echo "3. Command line:       python3 cli.py"
echo "4. Interactive mode:   python3 cli.py --interactive"
echo ""
echo "📖 For more information, see README.md"
echo ""
echo "Happy resume optimizing! 🎯"