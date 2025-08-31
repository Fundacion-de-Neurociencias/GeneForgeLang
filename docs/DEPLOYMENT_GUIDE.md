# Documentation Deployment Guide

This guide explains how to deploy and maintain the GeneForgeLang documentation website.

## 🌐 Live Documentation

The documentation is automatically deployed to GitHub Pages at:
**https://fundacion-de-neurociencias.github.io/GeneForgeLang/**

## 🏗️ Architecture

Our documentation system uses:
- **MkDocs Material**: Modern documentation framework with beautiful themes
- **GitHub Actions**: Automatic deployment on every commit
- **GitHub Pages**: Free hosting for the documentation website

## 📁 Documentation Structure

```
docs/
├── index.md                          # Homepage
├── installation.md                   # Installation guide
├── tutorial.md                       # Step-by-step tutorial
├── cli.md                           # CLI documentation
├── API_REFERENCE.md                 # API documentation
├── WEB_API_IMPLEMENTATION_SUMMARY.md # Web platform guide
├── ENHANCED_INFERENCE_SUMMARY.md    # AI/ML features
├── PHASE_4_PLANNING.md              # Roadmap
├── SECURITY_ADVISORY.md             # Security information
├── DOCUMENTATION_EXPORT_GUIDE.md    # This guide
├── stylesheets/
│   └── extra.css                    # Custom styling
└── images/                          # Documentation images
```

## 🚀 Automatic Deployment

The documentation is automatically built and deployed when:
1. Changes are pushed to the `main` or `master` branch
2. Files in the `docs/` directory are modified
3. The `mkdocs.yml` configuration is updated
4. Any markdown files in the root are changed

### GitHub Actions Workflow

The deployment is handled by `.github/workflows/docs.yml`:
- **Build**: Installs dependencies, builds documentation with MkDocs
- **Deploy**: Publishes to GitHub Pages (only on main/master branch)

## 🛠️ Local Development

### Prerequisites
```bash
pip install mkdocs-material
```

### Serve Locally
```bash
# Serve with hot reload
mkdocs serve

# Serve on specific address
mkdocs serve --dev-addr=127.0.0.1:8000
```

### Build Locally
```bash
# Build static site
mkdocs build

# Build with strict mode (fail on warnings)
mkdocs build --strict
```

## 📝 Adding New Documentation

### 1. Create the markdown file
```bash
# Add to docs/ directory
docs/new-guide.md
```

### 2. Update navigation
Edit `mkdocs.yml`:
```yaml
nav:
  - Home: index.md
  - New Guide: new-guide.md  # Add here
  - ...
```

### 3. Test locally
```bash
mkdocs serve
```

### 4. Commit and push
```bash
git add docs/new-guide.md mkdocs.yml
git commit -m "docs: add new guide"
git push origin main
```

## 🎨 Customization

### Theme Configuration
Edit `mkdocs.yml` to customize:
- Colors and fonts
- Navigation structure
- Features and extensions
- Social links

### Custom CSS
Add styles to `docs/stylesheets/extra.css`:
```css
/* Custom documentation styles */
.custom-class {
    color: #your-color;
}
```

## 🔧 Configuration Files

### mkdocs.yml
Main configuration file containing:
- Site metadata
- Theme settings
- Navigation structure
- Plugin configuration
- Extensions

### .github/workflows/docs.yml
GitHub Actions workflow for:
- Building documentation
- Deploying to GitHub Pages
- Caching dependencies

## 📊 GitHub Pages Setup

To enable GitHub Pages:
1. Go to repository **Settings** → **Pages**
2. Select **GitHub Actions** as source
3. The workflow will handle the rest automatically

## 🔍 Troubleshooting

### Documentation not updating?
1. Check GitHub Actions tab for build errors
2. Verify branch is `main` or `master`
3. Ensure GitHub Pages is enabled

### Local build failing?
1. Update MkDocs Material: `pip install --upgrade mkdocs-material`
2. Check for syntax errors in markdown files
3. Validate `mkdocs.yml` syntax

### Missing pages warnings?
Update navigation in `mkdocs.yml` or create the missing files.

## 📚 Best Practices

### Writing Documentation
- Use clear, concise language
- Include code examples
- Add navigation links between related pages
- Test all code snippets

### File Organization
- Keep related content in subdirectories
- Use descriptive filenames
- Maintain consistent formatting

### Version Control
- Commit documentation changes with descriptive messages
- Review documentation in pull requests
- Keep documentation up-to-date with code changes

## 🆘 Getting Help

- **MkDocs Documentation**: https://www.mkdocs.org/
- **Material Theme**: https://squidfunk.github.io/mkdocs-material/
- **GitHub Pages**: https://docs.github.com/en/pages

## 📈 Analytics

The documentation includes Google Analytics integration (configured via environment variable `GOOGLE_ANALYTICS_KEY` in the deployment environment).

---

For questions about the documentation system, please open an issue in the repository.
