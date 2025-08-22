# JokerNet

JokerNet is an AI-powered automation system for Balatro with a Streamlit interface.

## Features

- AI agents for automated gameplay using gamepad and mouse controls
- Streamlit web interface for interaction
- Model Context Protocol (MCP) integration
- Docker support for containerized gaming environment

## Installation

### Using UV (Recommended)

```bash
# Clone the repository
git clone https://github.com/Javier-Jimenez99/JokerNet.git
cd JokerNet

# Install uv if you haven't already
pipx install uv

# Install all dependencies (creates virtual environment automatically)
uv sync

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your Azure OpenAI credentials

# Run the application
uv run streamlit run src/app.py
```

### Using Traditional pip

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run the application
streamlit run src/app.py
```

## Configuration

1. **Azure OpenAI**: Configure your Azure OpenAI endpoint and API key in `.env`
2. **Docker**: If using BalatroDocker, set up Steam credentials
3. **Game Settings**: Adjust default deck and stake preferences

## Usage

1. Start the Docker environment (if using containerized Balatro)
2. Launch the Streamlit interface
3. Configure your AI agent settings (gamepad vs mouse control)
4. Begin automated gameplay through the chat interface

## Development

This project uses uv for dependency management. To contribute:

```bash
# Install with development dependencies
uv sync --group dev

# Run tests
uv run pytest

# Format code
uv run black src/
uv run isort src/

# Type checking
uv run mypy src/
```

## File Structure

- `src/` - Main source code
  - `app.py` - Streamlit application entry point
  - `agents/` - AI agent implementations
  - `ui_components/` - Streamlit UI components
- `BalatroDocker/` - Docker containerization setup
- `notebooks/` - Jupyter notebooks for development
- `pyproject.toml` - Project configuration and dependencies
- `uv.lock` - Locked dependency versions (for reproducible installs)

## Dependencies on Other Machines

Other developers can easily install the exact same dependency versions:

```bash
# Clone and install with exact locked versions
git clone https://github.com/Javier-Jimenez99/JokerNet.git
cd JokerNet
uv sync  # Installs exact versions from uv.lock
```
