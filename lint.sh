#!/bin/bash

# Run pylint on the project code

# Make sure we're in the project root directory
cd "$(dirname "$0")"

# Activate the virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "Running pylint..."
pylint app.py handlers/ services/ views/ || true

echo -e "\nPylint check completed."

# Display hint about fixing issues
echo -e "\nTo fix issues, consider running: pylint --generate-rcfile > .pylintrc"
echo "Then customize the .pylintrc file to suit your project needs." 