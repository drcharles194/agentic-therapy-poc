# Collaborative PoC

An agentic therapy platform with persona-aware LLM orchestration, featuring the **Sage** persona for emotional validation and reflection.

## 🏗️ Architecture

This is a monorepo containing:

- **Backend**: FastAPI + Python with LangChain orchestration and Neo4j memory graph
- **Frontend**: React + Vite + TypeScript with Tailwind CSS for the chat interface

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
   # Edit .env with your actual values
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
- **Function**: Emotional validation, reflection, gentle framing
- **Memory Focus**: Reflections, emotions, self-kindness events, contradictions

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

This is a **Proof of Concept** implementation focusing on:

- [ ] Basic project structure and setup ✅
- [ ] Backend FastAPI foundation
- [ ] Frontend React foundation  
- [ ] Core API endpoints (/chat, /memory, /healthcheck)
- [ ] Sage persona implementation
- [ ] Chat UI components
- [ ] Memory sidebar integration
- [ ] End-to-end integration testing

## 🚧 Development Workflow

The project is being developed in chunks with separate branches for review:

1. **chunk1-project-setup** - Project structure and configuration ✅
2. **chunk2-backend-foundation** - FastAPI setup and basic structure
3. **chunk3-frontend-foundation** - React + Vite setup and basic structure
4. **chunk4-backend-apis** - Core API endpoints implementation
5. **chunk5-frontend-components** - Chat UI components
6. **chunk6-sage-persona** - Complete Sage persona implementation
7. **chunk7-integration** - Full integration and testing

## 📄 License

See [LICENSE](LICENSE) file for details. 