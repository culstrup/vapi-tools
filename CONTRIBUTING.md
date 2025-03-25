# Contributing to VAPI Tools

Thank you for your interest in contributing to VAPI Tools! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We aim to foster an inclusive and welcoming community.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue on GitHub with the following information:

- A clear, descriptive title
- A detailed description of the issue
- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- Screenshots (if applicable)
- Your environment (OS, Python version, etc.)

### Suggesting Enhancements

We welcome suggestions for enhancements! When suggesting a feature, please:

- Use a clear, descriptive title
- Provide a detailed description of the suggested enhancement
- Explain why this enhancement would be useful
- Suggest an implementation approach if possible

### Pull Requests

1. Fork the repository
2. Create a new branch from `main` (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Add tests for your changes if applicable
5. Run the tests (`pytest tests/`)
6. Commit your changes (`git commit -m 'Add some feature'`)
7. Push to the branch (`git push origin feature/your-feature-name`)
8. Open a Pull Request

## Development Setup

1. Clone your forked repository
   ```
   git clone https://github.com/YOUR_USERNAME/vapi-tools.git
   cd vapi-tools
   ```

2. Create a virtual environment and install dependencies
   ```
   python3 -m venv venv
   source venv/bin/activate
   pip install vapi_server_sdk
   pip install pytest pytest-cov
   ```

3. Create a `.env` file with your VAPI API key
   ```
   VAPI_API_KEY=your_api_key_here
   ```

4. Run the tests to ensure everything is working
   ```
   pytest tests/
   ```

## Coding Guidelines

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use descriptive variable names
- Add type hints to functions (using `typing` module)
- Include docstrings for all functions and classes
- Keep script files executable with the shebang `#!/usr/bin/env python3`
- Ensure proper error handling with specific error types and logging

## Testing

- Add tests for new features
- Ensure existing tests pass
- Use pytest for running tests

## Documentation

- Update the README.md if necessary
- Add comments to explain complex logic
- Keep docstrings up-to-date

## License

By contributing to this project, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).

## Questions?

If you have any questions, feel free to open an issue to discuss them.

Thank you for contributing to VAPI Tools!