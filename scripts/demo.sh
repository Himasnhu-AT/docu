#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Running Docu demonstration...${NC}"

# Check for virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Running setup script first...${NC}"
    ./scripts/setup.sh
fi

# Activate virtual environment
source venv/bin/activate

# Ensure the docs directory exists
mkdir -p docs

# Generate examples
echo -e "\n${GREEN}Example 1: Generating HTML documentation${NC}"
docu examples/completeDocs.py --format html --output-dir docs --verbose
echo -e "\n${GREEN}The HTML documentation has been saved to docs/completeDocs.html${NC}"

echo -e "\n${GREEN}Example 2: Generating Markdown documentation (printed to console)${NC}"
docu examples/completeDocs.py --format markdown --verbose

echo -e "\n${BLUE}Demonstration complete!${NC}"
echo -e "${YELLOW}For more examples and usage information, see the README.md file.${NC}"