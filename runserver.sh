#!/bin/bash

# Local development server script for Jekyll
# This script sets up and runs the Jekyll development server

echo "🚀 Starting Jekyll development server..."

# Check if bundle is installed
if ! command -v bundle &> /dev/null; then
    echo "❌ Bundler is not installed. Installing..."
    gem install bundler
fi

# Check if Gemfile.lock exists, if not run bundle install
if [ ! -f "Gemfile.lock" ]; then
    echo "📦 Installing dependencies..."
    bundle install
else
    echo "📦 Updating dependencies..."
    bundle update
fi

# Start the Jekyll server with live reload
echo "🌐 Starting server at http://127.0.0.1:4000"
echo "📝 Press Ctrl+C to stop the server"
echo "🔄 The server will automatically reload when you make changes"
echo ""

bundle exec jekyll serve --livereload --open-url