# Collaborative PoC

An advanced conversational AI platform with persona-aware LLM orchestration, featuring intelligent memory management, GraphRAG therapy analysis, and contextual conversation capabilities.

## 🏗️ Architecture

This is a monorepo containing:

- **Backend**: FastAPI + Python with LangChain orchestration (pending) and Neo4j graph database
- **Frontend**: React + Vite + TypeScript with modern UI components

### GraphRAG Implementation

We maintain **two GraphRAG implementations** for therapy data analysis:

1. **Custom Implementation** (`backend/services/graphrag.py`) - Optimized with pre-computed embeddings and direct vector search
2. **Official Neo4j GraphRAG** (`backend/services/official_graphrag.py`) - Uses the official neo4j-graphrag package with dynamic retrievers

Both implementations provide intelligent therapy data analysis with confidence scoring and user-friendly data source reporting.

## See it in action

I've created a brief demo video to explain this project!

[Click me to see the demo video](https://www.loom.com/share/8488cd8eb3104020a32031cbb342cc1a?sid=6b3564cc-fce4-4be0-9c8f-82dbf6019ac1)

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** with [Poetry](https://python-poetry.org/docs/#installation)
- **Node.js 18+** with npm
- **Neo4j Database** (local or cloud instance)
- **Anthropic API Key** for Claude integration
- **OpenAI API Key** for embeddings and GraphRAG analysis

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
   # ANTHROPIC_API_KEY=your_anthropic_key_here
   # OPENAI_API_KEY=your_openai_key_here
   # NEO4J_URI=bolt://localhost:7687
   # NEO4J_USERNAME=neo4j
   # NEO4J_PASSWORD=your_neo4j_password
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
- **Analysis**: Intelligent conversation analysis for therapeutic insights

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
├── backend/                    # FastAPI backend
│   ├── main.py                # FastAPI app entrypoint
│   ├── config.py              # Configuration management
│   ├── routers/               # API route handlers
│   │   ├── chat.py           # Chat conversation endpoints
│   │   └── users.py          # User management and GraphRAG analysis
│   ├── personas/              # Persona-specific logic
│   │   └── sage/             # Sage persona implementation
│   │       ├── handler.py    # Main persona handler
│   │       ├── memory.py     # Memory context management
│   │       └── prompt.j2     # Jinja2 prompt template
│   ├── services/              # Business logic services
│   │   ├── anthropic_service.py    # Claude API integration
│   │   ├── neo4j.py               # Graph database service
│   │   ├── memory_analyzer.py     # Intelligent memory processing
│   │   ├── embedding.py           # OpenAI embeddings service
│   │   ├── graphrag.py           # Custom GraphRAG implementation
│   │   ├── official_graphrag.py  # Official Neo4j GraphRAG
│   │   └── router.py             # Persona routing service
│   ├── utils/                 # Utility modules
│   │   ├── graphrag_utils.py  # Shared GraphRAG utilities
│   │   └── name_generator.py  # User name generation
│   ├── models/                # Pydantic models
│   │   └── schema.py         # API schemas and data models
│   ├── tests/                 # Test suite
│   └── pyproject.toml         # Poetry configuration
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── MemorySidebar.tsx     # Memory visualization
│   │   │   ├── MessageBubble.tsx     # Chat message display
│   │   │   └── PersonaPanel.tsx      # Persona status display
│   │   ├── pages/             # Page components
│   │   │   ├── ChatPage.tsx          # Main chat interface
│   │   │   └── TherapistPortal.tsx   # Therapist analysis portal
│   │   ├── types/             # TypeScript type definitions
│   │   │   └── views.ts              # View-related types
│   │   ├── utils/             # Utility functions
│   │   │   └── api.ts               # API communication layer
│   │   ├── App.tsx           # Main application component
│   │   └── main.tsx          # Application entry point
│   ├── package.json          # npm configuration
│   └── vite.config.ts        # Vite configuration
└── README.md                 # This file
```

## 🎯 Current Status

This is a **Full-Stack** implementation featuring:

- ✅ **Real Service Integration**: Live Claude API, OpenAI embeddings, and Neo4j database
- ✅ **Intelligent Memory System**: Advanced context-aware memory storage and analysis
- ✅ **Dual GraphRAG Implementation**: Custom optimized + official Neo4j GraphRAG
- ✅ **Therapist Portal**: Professional analysis interface with accordion UI
- ✅ **Dynamic Confidence Scoring**: Quality-based confidence assessment
- ✅ **User-Friendly Data Sources**: Friendly naming for analysis results
- ✅ **Robust Error Handling**: JSON parsing recovery and comprehensive fallbacks
- ✅ **Persona Implementation**: Fully functional conversational AI
- ✅ **Modern UI**: React-based chat interface with memory sidebar
- ✅ **Graph Database**: Neo4j for complex relationship storage
- ✅ **API Integration**: Complete backend/frontend communication
- ✅ **Vector Search Optimization**: Pre-computed embeddings for performance
- ✅ **Dynamic Resource Management**: User-specific retriever creation

## 🚧 Development Workflow

The project was developed in chunks with separate branches for review:

1. **chunk1-project-setup** - Project structure and configuration ✅
2. **chunk2-backend-foundation** - FastAPI setup and basic structure ✅
3. **chunk3-frontend-foundation** - React + Vite setup and basic structure ✅
4. **chunk4-backend-apis** - Core API endpoints implementation ✅
5. **chunk5-real-services** - Live Claude API and Neo4j integration ✅
6. **chunk6-intelligent-memory** - Advanced memory processing and storage ✅
7. **chunk7-demo-improvements** - Added therapist portal, GraphRAG, and UI/UX improvements ✅

## 🔧 Technical Features

### Core Platform
- **Memory Management**: Multi-dimensional memory analysis and storage
- **Contextual Conversations**: AI maintains context across sessions
- **Graph Database**: Complex relationship modeling with Neo4j
- **Real-time Processing**: Live API integration with intelligent caching
- **Modern Frontend**: React with TypeScript and Tailwind CSS
- **Robust Architecture**: Comprehensive error handling and monitoring

### GraphRAG & Analysis
- **Dual Implementation**: Custom optimized + official Neo4j GraphRAG
- **Vector Search Performance**: Pre-computed embeddings with direct similarity search
- **Dynamic Resource Management**: User-specific retriever creation and filtering
- **Confidence Scoring**: Quality-based confidence assessment (0.1-0.95 scale)
- **Structured Analysis**: Organized therapeutic insights with accordion UI
- **Error Recovery**: Robust JSON parsing with truncation recovery
- **Friendly Data Sources**: User-friendly display names for analysis results

### Memory & Intelligence
- **Intelligent Analysis**: Claude-powered conversation analysis for memory storage
- **Deduplication**: Context-aware memory deduplication to prevent redundancy
- **Multi-dimensional Storage**: Moments, emotions, reflections, values, patterns, contradictions
- **Background Processing**: Non-blocking embedding generation
- **Quality Validation**: Strict content validation before storage

## 📄 License

See [LICENSE](LICENSE) file for details. 
