#!/bin/bash

# Setup script for LangGraph Multi-Agent System

echo "=================================================="
echo "LangGraph Multi-Agent System - Setup Script"
echo "=================================================="
echo ""

# Check if .env exists in backend root
if [ ! -f ../../.env ]; then
    echo "📝 Creating .env file from template..."
    cp ../../.env.example ../../.env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your API keys:"
    echo "   - GOOGLE_API_KEY"
    echo "   - PINECONE_API_KEY"
    echo "   - PINECONE_ENVIRONMENT"
    echo "   - PINECONE_INDEX_NAME"
    echo ""
else
    echo "✅ .env file already exists"
    echo ""
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r ../../requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "=================================================="
echo "✅ Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Ensure your Pinecone index has the required namespaces:"
echo "   - transcript (time-stamped lecture transcripts)"
echo "   - slides (slide content)"
echo "   - papers (research papers)"
echo "3. Run tests: python test_agents.py"
echo "4. Start the API: python app.py"
echo ""
echo "For more information, see README.md"
echo ""
