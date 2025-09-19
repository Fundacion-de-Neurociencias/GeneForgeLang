#!/bin/bash

# GeneForgeLang v1.0.0 Release Script

set -e  # Exit on any error

echo "🚀 Starting GeneForgeLang v1.0.0 Release Process"

# 1. Verify we're on the main branch
echo "🔍 Checking current branch..."
current_branch=$(git rev-parse --abbrev-ref HEAD)
if [ "$current_branch" != "main" ] && [ "$current_branch" != "master" ]; then
    echo "⚠️  Warning: You're not on the main branch. Current branch: $current_branch"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Release cancelled"
        exit 1
    fi
fi

# 2. Ensure working directory is clean
echo "🔍 Checking for uncommitted changes..."
if [[ -n $(git status --porcelain) ]]; then
    echo "❌ Error: Uncommitted changes found. Please commit or stash them before releasing."
    git status --porcelain
    exit 1
fi

# 3. Run tests
echo "🧪 Running tests..."
python -m pytest tests/ -v

# 4. Build the package
echo "📦 Building package..."
python -m build

# 5. Create Git tag
echo "🏷️  Creating Git tag..."
git tag -a v1.0.0 -m "Release version 1.0.0"

# 6. Push to GitHub
echo "☁️  Pushing to GitHub..."
git push origin main
git push origin v1.0.0

# 7. Upload to PyPI
echo "🐍 Uploading to PyPI..."
python -m twine upload dist/*

echo "🎉 GeneForgeLang v1.0.0 Release Complete!"
echo "✅ Don't forget to:"
echo "   1. Create a GitHub release with the announcement"
echo "   2. Update the documentation website"
echo "   3. Notify the community via mailing list/social media"
echo "   4. Update any related projects that depend on GFL"
