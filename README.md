# Optimization RAG System

A Retrieval-Augmented Generation (RAG) system for cloud cost optimization knowledge retrieval. This system ingests cloud cost optimization best practices from trusted sources, creates embeddings, and provides a FastAPI service for natural language queries.

## 🎯 Overview

This system helps users retrieve cloud cost optimization techniques using natural language queries. It includes:

- **Data Ingestion**: Collects optimization content from AWS, Azure, GCP, and other trusted sources
- **Vector Database**: Stores embeddings using PGVector with semantic search capabilities  
- **Retrieval Pipeline**: Implements semantic search with cross-encoder reranking
- **FastAPI Service**: Provides REST API endpoints for queries and system management
- **Evaluation Framework**: Measures retrieval quality using Recall@K and MRR metrics

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Sources  │───▶│  Vector Database │───▶│  FastAPI Service │
│  (AWS, Azure,   │    │   (PGVector)     │    │   (REST API)    │
│   GCP, Blogs)   │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Preprocessing │    │   OpenAI         │    │   Retrieval     │
│   & Chunking    │    │   Embeddings     │    │   & Reranking   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
optimization-rag-system/
├── app/                          # FastAPI application
│   ├── __init__.py
│   └── main.py                   # Main API server
├── data/                         # Data configuration and sources
│   └── sources.yaml              # Data sources configuration
├── eval/                         # Evaluation framework
│   ├── gold_labels.jsonl         # Test queries with ground truth
│   └── llm_eval_report.md        # LLM evaluation report (bonus)
├── tests/                        # Test suite
├── docs/                         # Additional documentation
├── build_vector_db.ipynb         # Data ingestion notebook
├── retrieval_pipeline.py         # Retrieval and reranking logic
├── retrieval_eval.md             # Retrieval evaluation report
├── agent_orchestrator.py         # Agent orchestration (bonus)
├── requirements.txt              # Python dependencies
├── env.example                   # Environment configuration template
├── README.md                     # This file
├── DEPLOYMENT.md                 # Deployment instructions
└── .gitignore                    # Git ignore rules
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Docker (for running pgvector/PostgreSQL container)
- OpenAI API key
- LangSmith API key (optional, for agent testing in UI)

### Installation

1. **Clone the repository**
   ```bash
   git clone <https://github.com/Sarfaraz021/optimization-rag-system>
   cd optimization-rag-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup PGVector Database**

   ### Step-by-Step Setup

   **Step 1: Open Terminal**
   Open your Mac Terminal app

   **Step 2: Check if Container Exists**
   ```bash
   docker ps -a | grep pgvector
   ```
   If you see a container, go to Step 3. If not, go to Step 4.

   **Step 3: If Container Exists (Start It)**
   ```bash
   docker start pgvector-container
   ```
   Wait 5 seconds, then verify it's running:
   ```bash
   docker ps
   ```
   You should see `pgvector-container` with status "Up".
   ✅ Skip to Step 5 to test connection

   **Step 4: If Container Doesn't Exist (Create It)**
   ```bash
   docker run --name pgvector-container \
     -e POSTGRES_USER=langchain \
     -e POSTGRES_PASSWORD=langchain \
     -e POSTGRES_DB=langchain \
     -p 6024:5432 \
     -d pgvector/pgvector:pg16
   ```
   Wait 10 seconds for it to fully start, then check:
   ```bash
   docker ps
   ```
   You should see `pgvector-container` running!

   **Step 5: Test the Connection**
   ```bash
   docker exec -it pgvector-container psql -U langchain -d langchain
   ```
   If successful, you'll see:
   ```
   psql (16.x)
   Type "help" for help.

   langchain=#
   ```
   Type `\q` to exit.

5. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your OpenAI API key
   ```

6. **Build vector database**
   ```bash
   jupyter notebook build_vector_db.ipynb
   # Run all cells to ingest data
   ```

7. **Start the API server**
   ```bash
   python app/main.py
   # API available at http://localhost:8000
   ```

## 🤖 **Alternative: Test Agent in LangSmith UI**

If you want to test the agent directly in LangSmith's interactive UI:

### **Setup for LangSmith**

1. **Get LangSmith API Key**
   - Sign up at [smith.langchain.com](https://smith.langchain.com)
   - Get your API key from Settings > API Keys

2. **Configure Environment**
   ```bash
   # Add to your .env file
   LANGSMITH_API_KEY=your_langsmith_api_key_here
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_PROJECT=optimization-rag-system
   ```

3. **Install LangGraph CLI**
   ```bash
   pip install langgraph-cli
   ```

4. **Install Project in Editable Mode**
   ```bash
   pip install -e .
   ```
   This allows LangGraph to import your project modules.

5. **Start LangGraph Development Server**
   ```bash
   langgraph dev
   ```
   
   This will:
   - Start the agent server locally
   - Open LangSmith UI in your browser
   - Allow interactive testing of your agent

6. **Test in Browser**
   - Navigate to the LangSmith UI (opens automatically)
   - Find your "Cloud Cost Optimization Agent"
   - Test queries like:
     - "How to reduce AWS S3 storage costs?"
     - "What are Azure Spot VM savings?"
     - "Optimize Google BigQuery costs"

### **Benefits of LangSmith UI Testing**
- **Interactive chat interface** - test like ChatGPT
- **Real-time tracing** - see exactly how your agent works
- **Performance monitoring** - track response times and token usage
- **Debug tools** - inspect retrieval results and reasoning steps

## 📊 Usage

### API Endpoints

- **Health Check**: `GET /health`
- **Query Optimization**: `POST /query`
- **System Statistics**: `GET /stats`
- **Rebuild Database**: `POST /rebuild` (optional)

### Example Queries

```bash
# Health check
curl http://localhost:8000/health

# Query for optimization advice
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Reduce Azure Blob storage cost with lifecycle policies", "top_k": 5}'
```

### Sample Test Queries

The system is designed to handle queries like:

- "Reduce Azure Blob storage cost with lifecycle policies"
- "Save money using AWS S3 Intelligent Tiering"
- "What are Azure Spot VM savings compared to pay-as-you-go?"
- "Optimize Google BigQuery storage cost"
- "Give rightsizing recommendations for EC2 compute"

## 🔧 Configuration

Key configuration is managed in `data/sources.yaml`:

```yaml
# Vector Database
vector_db:
  type: "pgvector"
  connection: "postgresql+psycopg://langchain:langchain@localhost:6024/langchain"

# Models
embedding:
  model: "text-embedding-3-small"
  dimension: 1536

reranking:
  model: "cross-encoder/ms-marco-MiniLM-L6-v2"
  enabled: true
```

## 📈 Evaluation

The system includes comprehensive evaluation metrics:

- **Recall@K**: Measures retrieval coverage at different K values
- **Mean Reciprocal Rank (MRR)**: Evaluates ranking quality
- **Confidence Scores**: Assesses result relevance

Run evaluation using the RetrievalEvaluator class in `retrieval_pipeline.py`. View results in `retrieval_eval.md`.

### Agent Orchestration (Part D)
- minimal agent integrated with rag pipline
- Query routing and refinement

## 🔍 System Statistics

Access system information via the API:

```bash
curl http://localhost:8000/stats
```

Returns database size, embedding model info, and provider breakdown.
