# GeneForgeLang v1.0.0 Release Script for Windows

Write-Host "🚀 Starting GeneForgeLang v1.0.0 Release Process" -ForegroundColor Green

# 1. Verify we're on the main branch
Write-Host "🔍 Checking current branch..." -ForegroundColor Yellow
$currentBranch = git rev-parse --abbrev-ref HEAD
if ($currentBranch -ne "main" -and $currentBranch -ne "master") {
    Write-Host "⚠️  Warning: You're not on the main branch. Current branch: $currentBranch" -ForegroundColor Yellow
    $response = Read-Host "Continue anyway? (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "❌ Release cancelled" -ForegroundColor Red
        exit 1
    }
}

# 2. Ensure working directory is clean
Write-Host "🔍 Checking for uncommitted changes..." -ForegroundColor Yellow
$uncommitted = git status --porcelain
if ($uncommitted) {
    Write-Host "❌ Error: Uncommitted changes found. Please commit or stash them before releasing." -ForegroundColor Red
    Write-Host $uncommitted
    exit 1
}

# 3. Run tests
Write-Host "🧪 Running tests..." -ForegroundColor Yellow
python -m pytest tests/ -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Tests failed. Aborting release." -ForegroundColor Red
    exit 1
}

# 4. Build the package
Write-Host "📦 Building package..." -ForegroundColor Yellow
python -m build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed. Aborting release." -ForegroundColor Red
    exit 1
}

# 5. Create Git tag
Write-Host "🏷️  Creating Git tag..." -ForegroundColor Yellow
git tag -a v1.0.0 -m "Release version 1.0.0"

# 6. Push to GitHub
Write-Host "☁️  Pushing to GitHub..." -ForegroundColor Yellow
git push origin main
git push origin v1.0.0

# 7. Upload to PyPI
Write-Host "🐍 Uploading to PyPI..." -ForegroundColor Yellow
python -m twine upload dist/*

Write-Host "🎉 GeneForgeLang v1.0.0 Release Complete!" -ForegroundColor Green
Write-Host "✅ Don't forget to:" -ForegroundColor Green
Write-Host "   1. Create a GitHub release with the announcement" -ForegroundColor Green
Write-Host "   2. Update the documentation website" -ForegroundColor Green
Write-Host "   3. Notify the community via mailing list/social media" -ForegroundColor Green
Write-Host "   4. Update any related projects that depend on GFL" -ForegroundColor Green