#!/bin/bash
# Setup script for pipeline.

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Installing required packages..."
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOL
# # AWS Configuration
# AWS_ACCESS_KEY_ID=your_access_key
# AWS_SECRET_ACCESS_KEY=your_secret_key
# S3_BUCKET_NAME=your_bucket_name

# EOL
#     echo "Please update the .env file with your actual configuration values"
# fi
