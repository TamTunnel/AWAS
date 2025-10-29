# Contributing to AWAS

Thank you for your interest in contributing to the AI Web Action Standard (AWAS)! This document provides guidelines for contributing.

## Code of Conduct

Be respectful, inclusive, and constructive in all interactions.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/TamTunnel/awas/issues)
2. If not, create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (browser, server, etc.)

### Suggesting Enhancements

1. Check [Discussions](https://github.com/TamTunnel/awas/discussions) for similar ideas
2. Create a new discussion or issue explaining:
   - Use case and motivation
   - Proposed solution
   - Alternative approaches considered

### Contributing Code

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow existing code style
   - Add tests if applicable
   - Update documentation

4. **Commit your changes**
   ```bash
   git commit -m "Add feature: description"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Describe your changes
   - Reference related issues
   - Wait for review

### Contributing Documentation

Documentation improvements are always welcome!
- Fix typos or clarify explanations
- Add examples or tutorials
- Translate documentation

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/awas.git
cd awas

# Install dependencies (if applicable)
npm install  # or pip install -r requirements.txt

# Run tests
npm test  # or pytest
```

## Style Guidelines

### Code Style
- JavaScript: Follow ESLint configuration
- Python: Follow PEP 8
- Use meaningful variable and function names
- Add comments for complex logic

### Commit Messages
- Use present tense ("Add feature" not "Added feature")
- First line: brief summary (50 chars or less)
- Blank line, then detailed description if needed

### Documentation Style
- Use clear, concise language
- Include code examples
- Keep lines under 100 characters
- Use Markdown formatting

## Testing

- Add tests for new features
- Ensure all tests pass before submitting PR
- Include both unit and integration tests where appropriate

## Review Process

1. Maintainers will review your PR
2. Address any requested changes
3. Once approved, a maintainer will merge your PR

## Questions?

Feel free to ask in [Discussions](https://github.com/TamTunnel/awas/discussions) or open an issue!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
