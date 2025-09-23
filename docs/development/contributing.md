# Contributing to GeneForgeLang

Thank you for your interest in contributing to GeneForgeLang! This guide explains how to contribute to the project.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a new branch for your feature or bug fix
4. Make your changes
5. Write tests for your changes
6. Commit your changes with a clear commit message
7. Push your branch to your fork
8. Open a pull request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/Fundacion-de-Neurociencias/GeneForgeLang.git
cd GeneForgeLang

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## Code Quality Standards

### Style Guide
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Write docstrings for all public functions and classes
- Keep functions focused and small
- Use type hints where appropriate

### Testing
- Write unit tests for all new functionality
- Ensure all tests pass before submitting a pull request
- Aim for high test coverage
- Include both positive and negative test cases

### Documentation
- Update documentation when changing functionality
- Write clear, concise documentation
- Include examples for complex features
- Keep the documentation up-to-date

## Pull Request Process

1. Ensure your code follows the style guide
2. Run all tests to ensure they pass
3. Add documentation for new features
4. Update the CHANGELOG.md file with a description of your changes
5. Submit a pull request with a clear title and description

## Reporting Issues

If you find a bug or have a feature request, please open an issue on GitHub with:

1. A clear and descriptive title
2. A detailed description of the problem or feature
3. Steps to reproduce the issue (if applicable)
4. Expected behavior vs. actual behavior
5. Screenshots or code examples (if helpful)

## Community Guidelines

- Be respectful and inclusive
- Provide constructive feedback
- Help others when possible
- Follow the code of conduct

## License

By contributing to GeneForgeLang, you agree that your contributions will be licensed under the MIT License.