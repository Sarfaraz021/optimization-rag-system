import os
import sys
import json
from typing import List, Optional
from datetime import datetime, timezone

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv

# Add parent directory to path to import retrieval_pipeline
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from retrieval_pipeline import RetrievalPipeline

# Load environment variables
load_dotenv()


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(5, ge=1, le=20)
    use_reranking: bool = True
    provider_filter: Optional[List[str]] = None


class QueryResult(BaseModel):
    content: str
    source: str
    provider: str
    url: str
    confidence_score: float
    rerank_score: Optional[float] = None


class QueryResponse(BaseModel):
    query: str
    results: List[QueryResult]
    total_results: int
    processing_time_ms: float


class SystemStats(BaseModel):
    total_documents: int
    total_chunks: int
    embedding_model: str
    providers: List[str]
    vector_db_type: str


class RebuildResponse(BaseModel):
    status: str
    message: str
    task_id: Optional[str] = None


app = FastAPI(title="Optimization RAG System")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

retrieval_pipeline = None

def get_pipeline():
    global retrieval_pipeline
    if retrieval_pipeline is None:
        retrieval_pipeline = RetrievalPipeline()
    return retrieval_pipeline


@app.get("/")
async def root():
    return {"message": "Optimization RAG System API", "status": "running"}


@app.get("/health")
async def health_check():
    try:
        get_pipeline()
        return {"status": "healthy", "pipeline_ready": True}
    except Exception:
        return {"status": "degraded", "pipeline_ready": False}


@app.post("/query", response_model=QueryResponse)
async def query_optimization(request: QueryRequest):
    start_time = datetime.now(timezone.utc)
    pipeline = get_pipeline()
    
    results = pipeline.retrieve(request.query, request.top_k, request.use_reranking)
    
    if request.provider_filter and "string" not in request.provider_filter:
        results = [r for r in results if r['metadata']['provider'].lower() in 
                  [p.lower() for p in request.provider_filter]]
    
    formatted_results = [
        QueryResult(
            content=result['content'],
            source=result['metadata']['source'],
            provider=result['metadata']['provider'],
            url=result['metadata']['url'],
            confidence_score=result.get('similarity_score', 0.0),
            rerank_score=result.get('rerank_score')
        ) for result in results
    ]
    
    processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
    
    return QueryResponse(
        query=request.query,
        results=formatted_results,
        total_results=len(formatted_results),
        processing_time_ms=round(processing_time, 2)
    )


@app.get("/stats", response_model=SystemStats)
async def get_system_stats():
    stats_file = "data/ingestion_stats.json"
    if os.path.exists(stats_file):
        with open(stats_file, 'r') as f:
            stats = json.load(f)
    else:
        stats = {'total_chunks': 0, 'embedding_model': 'text-embedding-3-small', 'provider_breakdown': {}}
    
    return SystemStats(
        total_documents=stats.get('total_documents_scraped', 0),
        total_chunks=stats.get('total_chunks', 0),
        embedding_model=stats.get('embedding_model', 'unknown'),
        providers=list(stats.get('provider_breakdown', {}).keys()),
        vector_db_type='pgvector'
    )


@app.post("/rebuild", response_model=RebuildResponse)
async def rebuild_database(background_tasks: BackgroundTasks):
    task_id = f"rebuild_{int(datetime.now(timezone.utc).timestamp())}"
    background_tasks.add_task(rebuild_task, task_id)
    return RebuildResponse(status="accepted", message="Database rebuild initiated", task_id=task_id)


def rebuild_task(task_id: str):
    print(f"Rebuild task {task_id} started (placeholder)")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
