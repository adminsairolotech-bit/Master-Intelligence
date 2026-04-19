# ⚡ GOD LEVEL AI - 100% Power Unlocked

A comprehensive AI framework dashboard with **9 fully working frameworks** at 100% power.

## 🚀 Quick Start

```bash
cd god-level-extension
npm start
```

Then open: **http://localhost:3500**

## 📦 Installed Frameworks

| Framework | Version | Status | Purpose |
|-----------|---------|--------|---------|
| **LangGraph** | 1.1.8 | ✅ ACTIVE | Graph-based agent orchestration |
| **CrewAI** | 1.14.1 | ✅ ACTIVE | Multi-agent collaboration |
| **Agno** | 2.5.17 | ✅ ACTIVE | Production-ready agents |
| **AutoGen** | 0.5.7 | ✅ ACTIVE | Microsoft conversational agents |
| **LlamaIndex** | 0.14.20 | ✅ READY | RAG framework |
| **ChromaDB** | 1.1.1 | ✅ ACTIVE | Vector database |
| **DeepEval** | 3.9.7 | ✅ ACTIVE | LLM evaluation |
| **Arize Phoenix** | 14.8.0 | ✅ READY | ML observability |
| **Weaviate** | 4.20.5 | ✅ READY | Vector search engine |

## 🎯 Features

- **Real Python Demos**: Each framework runs actual Python code
- **Live Console Output**: See real-time execution results
- **One-Click Execution**: Run individual demos or all at once
- **Architecture Diagrams**: Visual representation of each framework
- **Status Indicators**: Real-time feedback on execution status

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/demos` | GET | List all available demos |
| `/api/run/{name}` | GET | Run specific framework demo |
| `/api/run-all` | GET | Run all demos at once |

## 📂 Project Structure

```
god-level-extension/
├── index.html          # Main dashboard UI
├── server.js          # Node.js API server
├── package.json        # Dependencies
├── README.md          # This file
└── demos/
    ├── 01_langgraph_demo.py
    ├── 02_crewai_demo.py
    ├── 03_agno_demo.py
    ├── 04_autogen_demo.py
    ├── 05_llamaindex_demo.py
    ├── 06_chromadb_demo.py
    ├── 07_deepeval_demo.py
    ├── 08_phoenix_demo.py
    └── 09_weaviate_demo.py
```

## 🎮 Usage

### Run Individual Demo
Click any "Run Demo" button on the dashboard.

### Run All Demos
Click "🎯 RUN ALL FRAMEWORK DEMOS" button.

### CLI Usage
```bash
# Run specific framework
npm run langgraph
npm run crewai
npm run chromadb

# Run all demos
npm run all
```

## 📊 Demo Outputs

Each demo:
1. Imports the actual framework
2. Creates real instances (agents, collections, indexes)
3. Executes actual operations
4. Displays architecture and results

## 🔑 Requirements

- Node.js 18+
- Python 3.8+
- All AI framework packages installed

## 📜 License

MIT - SAI Rolotech
