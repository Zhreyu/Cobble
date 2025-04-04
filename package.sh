#!/bin/bash
# Package the Smart File Sorter application for distribution

# Ensure we're in the correct directory
cd "$(dirname "$0")"

# Create a dist directory if it doesn't exist
mkdir -p dist

# Clean up any previous builds
rm -rf dist/* build/ *.egg-info/

# Create a source distribution
python3 setup.py sdist

# Create a wheel package
python3 setup.py bdist_wheel

echo "Packaging complete! Distribution files are in the dist/ directory."
echo "To install the package, run: pip install dist/*.whl"
