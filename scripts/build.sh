#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Building Docu package...${NC}"

# Check for virtual environment
if [ ! -d "venv" ]; then
    echo -e "${RED}Virtual environment not found. Running setup script first...${NC}"
    ./scripts/setup.sh
fi

# Activate virtual environment
source venv/bin/activate

# Clean previous builds
echo -e "${BLUE}Cleaning previous builds...${NC}"
rm -rf build/ dist/ *.egg-info/

# Build the package
echo -e "${BLUE}Building distribution packages...${NC}"
python -m build

echo -e "${GREEN}Build completed successfully!${NC}"
echo -e "${BLUE}Distribution packages are in the 'dist/' directory.${NC}"
echo -e "${BLUE}To upload to PyPI, run:${NC} python -m twine upload dist/*"