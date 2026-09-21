# Contributing to AWAS

Thank you for your interest in contributing to the AI Web Action Standard (AWAS)! This document provides guidelines for contributing.

## Code of Conduct

Be respectful, inclusive, and constructive in all interactions.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/TamTunnel/AWAS/issues)
2. If not, create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (browser, server, etc.)

### Suggesting Enhancements

1. Check [Discussions](https://github.com/TamTunnel/AWAS/discussions) for similar ideas
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

This repository is a documentation and specification repository — there is no package to install and no test suite to run. The contents are Markdown specification documents, example manifests, JSON schemas, and sample middleware code.

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/AWAS.git
cd AWAS
```

To validate a manifest against the JSON schema, use any JSON Schema validator (e.g., Python's `jsonschema` package) with `schema/ai-actions-schema.json`. A convenience parser example lives in `examples/awas-parser.js` (Node.js, no dependencies) and `examples/awas_middleware.py` (Python, no third-party dependencies).

## Style Guidelines

### Specification Prose
- Follow RFC 2119 key words (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY) when writing normative text; keep them capitalized and use them only where a requirement is intended
- Use clear, concise language
- Keep the `data-ai-*` attribute names and conformance level names (L1/L2/L3) consistent with SPECIFICATION.md and CONFORMANCE_LEVELS.md — those files are canonical for terminology

### Example Code
- JavaScript: clear, idiomatic style; no build step assumed
- Python: follow PEP 8
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

## Proposing Spec Changes

Because this repo defines a specification, changes to normative text need extra care:

1. Open an issue or discussion describing the problem and the proposed wording *before* writing a large change, so maintainers and implementers can weigh in.
2. Keep changes minimal and consistent with the rest of the spec — update every file that describes the same concept (check SPECIFICATION.md, CONFORMANCE_LEVELS.md, the JSON schema, and the examples).
3. Do not change normative attribute names (`data-ai-*`), manifest fields, or conformance level semantics without a version-bump discussion in the issue.
4. Reference the related issue in your pull request.

## Review Process

1. Maintainers will review your PR
2. Address any requested changes
3. Once approved, a maintainer will merge your PR

## Questions?

Feel free to ask in [Discussions](https://github.com/TamTunnel/AWAS/discussions) or open an issue!

## License

By contributing, you agree that your contributions will be licensed under the Apache License, Version 2.0.
