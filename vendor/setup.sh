#!/bin/bash

# AI Tools Setup Script
# This script sets up the AI tools module for PDF description generation

echo "🤖 Setting up AI Tools for PDF Description Generation"
echo "=================================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "✅ pip3 found: $(pip3 --version)"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check for OpenAI API key
echo ""
echo "🔑 Checking OpenAI API key..."

if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY environment variable is not set"
    echo ""
    echo "Please set your OpenAI API key:"
    echo "export OPENAI_API_KEY='your-api-key-here'"
    echo ""
    echo "For permanent setup, add this to your shell profile:"
    echo "echo 'export OPENAI_API_KEY=\"your-api-key-here\"' >> ~/.bashrc"
    echo "source ~/.bashrc"
    echo ""
    echo "You can get an API key from: https://platform.openai.com/api-keys"
else
    echo "✅ OPENAI_API_KEY is set"
fi

# Test the installation
echo ""
echo "🧪 Testing the installation..."
python3 test_ai_tools.py

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Set your OpenAI API key if you haven't already"
echo "2. Run 'python3 test_ai_tools.py' to verify everything works"
echo "3. Use the module in your generate_text.py script"
echo ""
echo "For more information, see README.md"
