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
- PostgreSQL with pgvector extension
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
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

4. **Setup database**
   ```bash
   # Start PostgreSQL with pgvector
   docker run -d --name pgvector \
     -e POSTGRES_DB=langchain \
     -e POSTGRES_USER=langchain \
     -e POSTGRES_PASSWORD=langchain \
     -p 6024:5432 \
     pgvector/pgvector:pg16
   ```

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

## 🎁 Bonus Features

### Agent Orchestration (Part D)
- Contextual memory for multi-turn conversations
- Query routing and refinement
- Enable with `AGENT_ENABLED=true`

### LLM Evaluation (Part E)  
- Advanced evaluation using DeepEval/RAGAS
- Relevance and citation quality metrics
- Latency and performance monitoring

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov=retrieval_pipeline

# Run specific test file
pytest tests/test_retrieval.py
```

## 📚 Data Sources

The system ingests from trusted sources:

- **AWS Well-Architected Framework** - Cost Optimization Pillar
- **Azure Cost Management** - Official documentation
- **Google Cloud Cost Optimization** - Best practices guide
- **FinOps Foundation** - Community resources
- **Cloud Provider Blogs** - Latest optimization techniques

## 🔍 System Statistics

Access system information via the API:

```bash
curl http://localhost:8000/stats
```

Returns database size, embedding model info, and provider breakdown.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions or issues:

1. Check the documentation in `docs/`
2. Review `DEPLOYMENT.md` for deployment issues
3. Open an issue on GitHub
4. Check the evaluation reports for performance insights

## 🔄 Development Roadmap

- [ ] Advanced chunking strategies
- [ ] Multi-modal support (images, diagrams)
- [ ] Real-time data source updates
- [ ] Advanced agent capabilities
- [ ] Integration with cloud cost APIs
- [ ] Custom embedding fine-tuning