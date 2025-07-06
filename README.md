# Collaborative PoC

An advanced conversational AI platform with persona-aware LLM orchestration, featuring intelligent memory management and contextual conversation capabilities.

## 🏗️ Architecture

This is a monorepo containing:

- **Backend**: FastAPI + Python with LangChain orchestration and Neo4j graph database
- **Frontend**: React + Vite + TypeScript with modern UI components

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** with [Poetry](https://python-poetry.org/docs/#installation)
- **Node.js 18+** with npm
- **Neo4j Database** (local or cloud instance)
- **Anthropic API Key** for Claude integration

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies with Poetry:
   ```bash
   poetry install
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your actual values:
   # ANTHROPIC_API_KEY=your_key_here
   # NEO4J_URI=bolt://localhost:7687
   # NEO4J_USERNAME=neo4j
   # NEO4J_PASSWORD=your_password
   ```

4. Start the development server:
   ```bash
   poetry run start
   # or alternatively: poetry run uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:5173` and will proxy API calls to the backend at `http://localhost:8000`.

## 🧠 Personas

### Sage (The Nurturer)
- **Tone**: Warm, non-directive, supportive
- **Function**: Contextual conversation with intelligent memory integration
- **Memory Focus**: Multi-dimensional memory storage and retrieval

## 🛠️ Development

### Backend Development

```bash
cd backend

# Run tests
poetry run pytest

# Code formatting
poetry run black .
poetry run isort .

# Type checking
poetry run mypy backend/

# Linting
poetry run flake8
```

### Frontend Development

```bash
cd frontend

# Type checking
npm run type-check

# Linting
npm run lint

# Build for production
npm run build
```

## 📦 Project Structure

```
agentic-therapy-poc/
├── backend/                 # FastAPI backend
│   ├── main.py             # FastAPI app entrypoint
│   ├── routers/            # API route handlers
│   ├── personas/           # Persona-specific logic
│   │   └── sage/           # Sage persona implementation
│   ├── services/           # Business logic services
│   │   ├── anthropic_service.py    # Claude API integration
│   │   ├── neo4j.py               # Graph database service
│   │   └── memory_analyzer.py     # Intelligent memory processing
│   ├── models/             # Pydantic models
│   └── pyproject.toml      # Poetry configuration
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── agents/         # Frontend agent logic
│   │   ├── utils/          # Utility functions
│   │   └── pages/          # Page components
│   ├── package.json        # npm configuration
│   └── vite.config.ts      # Vite configuration
└── README.md               # This file
```

## 🎯 Current Status

This is a **Full-Stack** implementation featuring:

- ✅ **Real Service Integration**: Live Claude API and Neo4j database
- ✅ **Intelligent Memory System**: Advanced context-aware memory storage
- ✅ **Persona Implementation**: Fully functional conversational AI
- ✅ **Modern UI**: React-based chat interface with memory sidebar
- ✅ **Graph Database**: Neo4j for complex relationship storage
- ✅ **API Integration**: Complete backend/frontend communication
- ✅ **Error Handling**: Robust fallback mechanisms

## 🚧 Development Workflow

The project was developed in chunks with separate branches for review:

1. **chunk1-project-setup** - Project structure and configuration ✅
2. **chunk2-backend-foundation** - FastAPI setup and basic structure ✅
3. **chunk3-frontend-foundation** - React + Vite setup and basic structure ✅
4. **chunk4-backend-apis** - Core API endpoints implementation ✅
5. **chunk5-real-services** - Live Claude API and Neo4j integration ✅
6. **chunk6-intelligent-memory** - Advanced memory processing and storage ✅

## 🔧 Technical Features

- **Memory Management**: Multi-dimensional memory analysis and storage
- **Contextual Conversations**: AI maintains context across sessions
- **Graph Database**: Complex relationship modeling with Neo4j
- **Real-time Processing**: Live API integration with intelligent caching
- **Modern Frontend**: React with TypeScript and Tailwind CSS
- **Robust Architecture**: Comprehensive error handling and monitoring

## 📄 License

See [LICENSE](LICENSE) file for details. 
