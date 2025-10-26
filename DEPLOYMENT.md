# Deployment Guide

## Prerequisites

- Python 3.8+
- PostgreSQL with pgvector extension
- OpenAI API key

## Quick Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your OpenAI API key and database connection
   ```

3. **Setup database**
   ```bash
   # Start PostgreSQL with pgvector
   docker run -d --name pgvector \
     -e POSTGRES_DB=langchain \
     -e POSTGRES_USER=langchain \
     -e POSTGRES_PASSWORD=langchain \
     -p 6024:5432 \
     pgvector/pgvector:pg16
   ```

4. **Build vector database**
   ```bash
   jupyter notebook build_vector_db.ipynb
   # Run all cells to ingest data
   ```

5. **Start API server**
   ```bash
   python app/main.py
   # API available at http://localhost:8000
   ```

## API Endpoints

- `GET /health` - Health check
- `POST /query` - Query optimization knowledge
- `GET /stats` - System statistics
- `POST /rebuild` - Rebuild database

## Production Notes

- Use environment variables for secrets
- Configure proper database connection pooling
- Set up monitoring and logging
- Use reverse proxy (nginx) for production