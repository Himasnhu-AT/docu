#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Setting up Docu development environment...${NC}"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 could not be found. Please install Python 3 and try again."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${BLUE}Upgrading pip...${NC}"
pip install --upgrade pip

# Install the package in development mode
echo -e "${BLUE}Installing package in development mode...${NC}"
pip install -e .

# Install development dependencies
echo -e "${BLUE}Installing development dependencies...${NC}"
pip install -r requirements.txt

echo -e "${GREEN}Setup complete! Docu is ready for development.${NC}"
echo -e "${BLUE}To activate the virtual environment, run:${NC} source venv/bin/activate"