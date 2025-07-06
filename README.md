# PRD Maker

AI-powered Product Requirements Document generator that guides you through a structured 6-step process to create comprehensive PRDs.

## Features

- **6-Step Sequential Process**: Guided workflow from idea to complete PRD
- **AI Integration**: Support for GPT-4, Claude, and local Ollama models
- **Interactive Planning**: AI-generated questions to clarify requirements
- **Project Management**: Save, load, and manage multiple projects
- **Export Options**: Download PRD as Markdown, Text, or JSON
- **Browser Storage**: Projects saved in browser localStorage

## The Process

1. **💡 Project Idea** - Start with your basic project concept
2. **📝 Project Description** - AI generates detailed description
3. **🗣️ Planning Session** - Interactive Q&A to clarify requirements
4. **❓ Answer Questions** - Provide detailed answers to AI questions
5. **📋 Planning Summary** - AI summarizes key decisions and requirements
6. **📄 PRD Document** - Final comprehensive PRD generation

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd prd-maker
```

2. Install dependencies using uv:
```bash
uv sync
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Run the application:
```bash
streamlit run app.py
```

## Configuration

### API Keys

Add your API keys to the `.env` file:

```bash
# OpenAI (for GPT-4, GPT-3.5-turbo)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic (for Claude models)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Ollama (for local models)
OLLAMA_BASE_URL=http://localhost:11434
```

### Supported Models

- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Anthropic**: Claude-3-Sonnet, Claude-3-Haiku
- **Ollama**: Llama2, Mistral (local models)

## Usage

1. **Create a New Project**: Click "New Project" in the sidebar
2. **Enter Project Idea**: Describe your basic project concept (minimum 50 characters)
3. **Generate Description**: AI creates detailed project description
4. **Planning Session**: Answer AI-generated questions about requirements
5. **Review Summary**: AI summarizes your planning session
6. **Generate PRD**: Create final PRD document
7. **Export**: Download your PRD in various formats

## Project Structure

```
prd-maker/
├── src/prd_maker/
│   ├── models/          # Data models (Project, PRD)
│   ├── core/            # Core logic (LLM, Storage)
│   ├── ui/              # Streamlit UI components
│   └── config/          # Configuration
├── doc/                 # Documentation
├── app.py              # Main application entry point
└── pyproject.toml      # Project configuration
```

## Development

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uv run black .
uv run flake8 .
uv run mypy .
```

### Tech Stack

- **Python 3.13** - Core language
- **Streamlit** - Web interface
- **LangChain** - AI model integration
- **Pydantic** - Data validation
- **uv** - Package management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.