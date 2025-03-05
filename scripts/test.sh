#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Running tests for Docu...${NC}"

# Check if the virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}Virtual environment not found. Running setup script first...${NC}"
    ./scripts/setup.sh
fi

# Activate virtual environment
source venv/bin/activate

# Run pytest with coverage
echo -e "${BLUE}Running tests with coverage...${NC}"
python -m pytest --cov=docu --cov-report=term-missing

# Run linting checks
echo -e "${BLUE}Running linting checks...${NC}"
echo "${RED}Not operational yet${NC}"
# python -m flake8 docu tests

# Optionally run type checking
echo -e "${BLUE}Running type checking...${NC}"
python -m mypy docu

echo -e "${GREEN}All tests completed!${NC}"