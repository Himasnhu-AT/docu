#!/bin/bash
set -e

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to handle errors
handle_error() {
    echo -e "${RED}Error: $1${NC}"
    exit 1
}

# Ensure we're in the project root
cd "$(dirname "$0")/.." || handle_error "Could not navigate to project root"

echo -e "${BLUE}Installing dependencies...${NC}"
pip install -r requirements.txt || handle_error "Failed to install dependencies"

echo -e "${BLUE}Installing package in development mode...${NC}"
pip install -e . || handle_error "Failed to install package"

# Directory setup
OUTPUT_DIR="docs"
EXAMPLE_DIR="examples"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR" || handle_error "Could not create output directory"

echo -e "\n${BLUE}Demonstrating different templates and doc styles...${NC}"

# Function to generate docs with a specific template
generate_docs() {
    local file=$1
    local template=$2
    local doc_style=$3
    local description=$4
    local output_file="${OUTPUT_DIR}/$(basename "${file%.*}")_${template}.html"
    
    echo -e "\n${GREEN}Generating documentation for $(basename "$file") with ${template} template (${doc_style} style)...${NC}"
    echo "Description: ${description}"
    python -m docu "$file" \
        --output-dir "$OUTPUT_DIR" \
        --template "$template" \
        --doc-style "$doc_style" \
        --format html || handle_error "Failed to generate docs with ${template} template"
}

# Process each Python file in examples directory
for py_file in "$EXAMPLE_DIR"/*.py; do
    echo -e "\n${BLUE}Processing $(basename "$py_file")...${NC}"
    
    # Generate docs with each template
    generate_docs "$py_file" "default" "google" "Clean, responsive template with proper code formatting"
    generate_docs "$py_file" "minimal" "google" "Lightweight template with basic styling"
    generate_docs "$py_file" "modern" "google" "Modern template with dark/light mode support"
    generate_docs "$py_file" "rtd" "sphinx" "ReadTheDocs-inspired template with sidebar navigation"
    
    # Also generate markdown version
    echo -e "\n${GREEN}Generating markdown documentation for $(basename "$py_file")...${NC}"
    python -m docu "$py_file" \
        --output-dir "$OUTPUT_DIR" \
        --format markdown || handle_error "Failed to generate markdown docs"
done

echo -e "\n${BLUE}Documentation generated successfully in ${OUTPUT_DIR}/ directory${NC}"
echo -e "${GREEN}Generated files:${NC}"
ls -l "$OUTPUT_DIR"

echo -e "\n${BLUE}Generated Documentation Files:${NC}"
for file in "$OUTPUT_DIR"/*; do
    filename=$(basename "$file")
    filesize=$(du -h "$file" | cut -f1)
    echo -e "${GREEN}${filename}${NC} (${filesize})"
done

echo -e "\n${BLUE}You can now open these HTML files in your browser to view the documentation${NC}"