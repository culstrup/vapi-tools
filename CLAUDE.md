# VAPI Tools Guidelines

## Commands
- Run Python script: `python3 script_name.py`
- Create/update venv: `python3 -m venv venv && source venv/bin/activate && pip install vapi_server_sdk`
- Activate venv: `source venv/bin/activate`

## Code Style
- Keep scripts executable with shebang `#!/usr/bin/env python3`
- Use descriptive variable names in snake_case
- Add type hints (List, Dict, Optional, etc.)
- Include docstrings for functions
- Follow PEP 8 formatting
- Error handling: Use try/except with specific error types and logging
- When executing subprocess, include proper error handling and check return codes

## Important Patterns
- Store API keys in `.env` file (VAPI_API_KEY=xxx)
- For Apple Scripts, use triple quotes and subprocess.run with capture_output=True
- When working with VAPI API, use the virtual environment
- Log diagnostics to files (e.g., vapi_transcript_debug.log)
- Remember to mark scripts executable: `chmod +x script_name.py`