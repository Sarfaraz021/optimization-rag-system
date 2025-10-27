import os
from typing import List, Dict
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from sentence_transformers import CrossEncoder
from langsmith import traceable
import numpy as np

load_dotenv()

# Configuration
EMBEDDING_MODEL = "text-embedding-3-small"
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L6-v2"
CONNECTION = "postgresql+psycopg://langchain:langchain@localhost:6024/langchain"
COLLECTION_NAME = "cloud_cost_optimization"


class RetrievalPipeline:
    """
    Two-stage retrieval pipeline with semantic search and cross-encoder reranking.
    """
    
    def __init__(self):
        """Initialize embeddings, vector store, and reranker model."""
        print("Initializing Retrieval Pipeline...")
        
        self.embeddings = OpenAIEmbeddings(
            model=EMBEDDING_MODEL,
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        
        self.vector_store = PGVector(
            embeddings=self.embeddings,
            collection_name=COLLECTION_NAME,
            connection=CONNECTION,
            use_jsonb=True,
        )
        
        print(f"Loading reranker model: {RERANKER_MODEL}")
        self.reranker = CrossEncoder(RERANKER_MODEL)
        
        print("Pipeline initialized successfully.\n")
    
    @traceable(name="semantic_search")
    def semantic_search(self, query: str, k: int = 20) -> List[Dict]:
        """
        Stage 1: Retrieve candidate documents using semantic similarity.
        
        Args:
            query: Search query string
            k: Number of candidates to retrieve
            
        Returns:
            List of candidate documents with similarity scores and metadata
        """
        results = self.vector_store.similarity_search_with_score(query, k=k)
        
        candidates = []
        for doc, score in results:
            candidates.append({
                'content': doc.page_content,
                'metadata': doc.metadata,
                'similarity_score': float(score)
            })
        
        return candidates
    
    @traceable(name="rerank")
    def rerank(self, query: str, candidates: List[Dict], top_k: int = 5) -> List[Dict]:
        """
        Stage 2: Rerank candidates using cross-encoder model.
        
        Args:
            query: Original search query
            candidates: Candidate documents from semantic search
            top_k: Number of top results to return
            
        Returns:
            Reranked list of top-k documents with scores
        """
        pairs = [(query, candidate['content']) for candidate in candidates]
        rerank_scores = self.reranker.predict(pairs)
        
        for candidate, score in zip(candidates, rerank_scores):
            candidate['rerank_score'] = float(score)
        
        reranked = sorted(candidates, key=lambda x: x['rerank_score'], reverse=True)
        return reranked[:top_k]
    
    @traceable(name="retrieve")
    def retrieve(self, query: str, top_k: int = 5, use_reranking: bool = True) -> List[Dict]:
        """
        Execute full retrieval pipeline.
        
        Args:
            query: Search query
            top_k: Number of results to return
            use_reranking: Enable/disable reranking stage
            
        Returns:
            Top-k relevant documents with scores and metadata
        """
        candidates = self.semantic_search(query, k=20)
        
        if not use_reranking:
            return candidates[:top_k]
        
        return self.rerank(query, candidates, top_k=top_k)


class RetrievalEvaluator:
    """Evaluation metrics for retrieval quality assessment."""
    
    def __init__(self, pipeline: RetrievalPipeline):
        self.pipeline = pipeline
    
    @traceable(name="recall_at_k")
    def recall_at_k(self, query: str, relevant_doc_ids: List[str], k: int = 5) -> float:
        """
        Calculate Recall@K: proportion of relevant documents retrieved in top-k results.
        
        Args:
            query: Search query
            relevant_doc_ids: Ground truth relevant document IDs
            k: Number of top results to evaluate
            
        Returns:
            Recall@K score between 0.0 and 1.0
        """
        results = self.pipeline.retrieve(query, top_k=k)
        retrieved_ids = [str(doc['metadata'].get('id', '')) for doc in results]
        
        relevant_retrieved = len(set(retrieved_ids) & set(relevant_doc_ids))
        total_relevant = len(relevant_doc_ids)
        
        return relevant_retrieved / total_relevant if total_relevant > 0 else 0.0
    
    @traceable(name="mean_reciprocal_rank")
    def mean_reciprocal_rank(self, query: str, relevant_doc_ids: List[str]) -> float:
        """
        Calculate MRR: reciprocal of rank position of first relevant document.
        
        Args:
            query: Search query
            relevant_doc_ids: Ground truth relevant document IDs
            
        Returns:
            MRR score between 0.0 and 1.0
        """
        results = self.pipeline.retrieve(query, top_k=20)
        
        for rank, doc in enumerate(results, start=1):
            doc_id = str(doc['metadata'].get('id', ''))
            if doc_id in relevant_doc_ids:
                return 1.0 / rank
        
        return 0.0
    
    def evaluate_queries(self, test_queries: List[Dict]) -> Dict:
        """
        Evaluate multiple queries and compute aggregate metrics.
        
        Args:
            test_queries: List of dicts with 'query' and 'relevant_ids' keys
            
        Returns:
            Dictionary containing average metrics and statistics
        """
        recall_scores = []
        mrr_scores = []
        
        print("Evaluating queries...\n")
        
        for i, test in enumerate(test_queries, 1):
            query = test['query']
            relevant_ids = test['relevant_ids']
            
            recall = self.recall_at_k(query, relevant_ids, k=5)
            mrr = self.mean_reciprocal_rank(query, relevant_ids)
            
            recall_scores.append(recall)
            mrr_scores.append(mrr)
            
            print(f"Query {i}: {query}")
            print(f"  Recall@5: {recall:.3f}")
            print(f"  MRR: {mrr:.3f}\n")
        
        results = {
            'avg_recall_at_5': np.mean(recall_scores),
            'avg_mrr': np.mean(mrr_scores),
            'num_queries': len(test_queries)
        }
        
        print("-" * 60)
        print("EVALUATION SUMMARY")
        print("-" * 60)
        print(f"Average Recall@5: {results['avg_recall_at_5']:.3f}")
        print(f"Average MRR: {results['avg_mrr']:.3f}")
        print(f"Queries Evaluated: {results['num_queries']}")
        print("-" * 60)
        
        return results


# def demo_retrieval():
#     """Demonstrate retrieval pipeline with sample queries."""
#     print("\n" + "=" * 60)
#     print("RETRIEVAL PIPELINE DEMONSTRATION")
#     print("=" * 60 + "\n")
    
#     pipeline = RetrievalPipeline()
    
#     sample_queries = [
#         "Reduce Azure Blob storage cost with lifecycle policies",
#         "Save money using AWS S3 Intelligent Tiering",
#         "What are Azure Spot VM savings compared to pay-as-you-go?",
#         "Optimize Google BigQuery storage cost",
#         "Give rightsizing recommendations for EC2 compute"
#     ]
    
#     for i, query in enumerate(sample_queries, 1):
#         print(f"\n{'=' * 60}")
#         print(f"Query {i}: {query}")
#         print('=' * 60)
        
#         results = pipeline.retrieve(query, top_k=3)
        
#         for j, result in enumerate(results, 1):
#             print(f"\nResult {j}:")
#             print(f"  Source: {result['metadata']['source']}")
#             print(f"  Provider: {result['metadata']['provider']}")
#             print(f"  Rerank Score: {result['rerank_score']:.4f}")
#             print(f"  Preview: {result['content'][:200]}...")
#             print(f"  URL: {result['metadata']['url']}")


# if __name__ == "__main__":
#     demo_retrieval()