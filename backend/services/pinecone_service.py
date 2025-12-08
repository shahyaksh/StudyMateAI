"""
Pinecone service for vector database operations.
Handles embedding generation, retrieval, and namespace-specific queries.
"""

from typing import List, Dict, Optional
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
import numpy as np

from config import Config


class PineconeService:
    """Service for interacting with Pinecone vector database."""
    
    def __init__(self):
        """Initialize Pinecone client and embedding model."""
        self.config = Config
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=self.config.PINECONE_API_KEY)
        
        # Initialize both indexes
        self.papers_index_name = self.config.PINECONE_PAPERS_INDEX
        self.slides_index_name = self.config.PINECONE_SLIDES_INDEX
        
        # Initialize embedding model (OpenAI to match indexed data)
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",  # 1536 dimensions
            openai_api_key=self.config.OPENAI_API_KEY
        )
        
        # Get indexes
        self.papers_index = self.pc.Index(self.papers_index_name)
        self.slides_index = self.pc.Index(self.slides_index_name)
        
        print(f"✅ Connected to Pinecone indexes:")
        print(f"   - Papers: {self.papers_index_name}")
        print(f"   - Slides: {self.slides_index_name}")
    
    def _get_index_for_namespace(self, namespace: str):
        """Get the appropriate index based on namespace."""
        if namespace == self.config.NAMESPACE_PAPERS:
            return self.papers_index
        elif namespace == self.config.NAMESPACE_SLIDES:
            return self.slides_index
        elif namespace == self.config.NAMESPACE_TRANSCRIPT:
            # Transcripts go in slides index
            return self.slides_index
        else:
            # Default to papers index
            return self.papers_index
    
    def query_namespace(
        self,
        query: str,
        namespace: str,
        top_k: int = None,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Query a specific namespace in Pinecone.
        
        Args:
            query: Search query text
            namespace: Pinecone namespace to search
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of retrieved documents with metadata
        """
        if top_k is None:
            top_k = self.config.TOP_K_RESULTS
        
        # Get the appropriate index for this namespace
        index = self._get_index_for_namespace(namespace)
        
        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)
        
        # Query Pinecone
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            namespace=namespace,
            filter=filter_metadata,
            include_metadata=True
        )
        
        # Format results
        documents = []
        for match in results.matches:
            doc = {
                "content": match.metadata.get("text", ""),
                "score": match.score,
                "metadata": {
                    "namespace": namespace,
                    **match.metadata
                }
            }
            documents.append(doc)
        
        return documents
    
    def query_multiple_namespaces(
        self,
        query: str,
        namespaces: List[str],
        top_k_per_namespace: int = None,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Query multiple namespaces and combine results.
        
        Args:
            query: Search query text
            namespaces: List of namespaces to search
            top_k_per_namespace: Number of results per namespace
            filter_metadata: Optional metadata filters
            
        Returns:
            Combined list of documents from all namespaces
        """
        all_documents = []
        
        for namespace in namespaces:
            docs = self.query_namespace(
                query=query,
                namespace=namespace,
                top_k=top_k_per_namespace,
                filter_metadata=filter_metadata
            )
            all_documents.extend(docs)
        
        # Sort by score (descending)
        all_documents.sort(key=lambda x: x["score"], reverse=True)
        
        return all_documents
    
    def query_with_timestamp(
        self,
        query: str,
        timestamp: float,
        namespace: str = None,
        window_seconds: int = None
    ) -> List[Dict]:
        """
        Query with timestamp-based filtering for transcript namespace.
        
        Args:
            query: Search query text
            timestamp: Current video timestamp in seconds
            namespace: Namespace to search (defaults to transcript)
            window_seconds: Time window before/after timestamp
            
        Returns:
            List of documents within the time window
        """
        if namespace is None:
            namespace = self.config.NAMESPACE_TRANSCRIPT
        
        if window_seconds is None:
            window_seconds = self.config.TIMESTAMP_CONTEXT_WINDOW
        
        # Create time-based filter
        start_time = max(0, timestamp - window_seconds)
        end_time = timestamp + window_seconds
        
        filter_metadata = {
            "start_time": {"$gte": start_time},
            "end_time": {"$lte": end_time}
        }
        
        return self.query_namespace(
            query=query,
            namespace=namespace,
            filter_metadata=filter_metadata
        )
    
    def get_vectorstore(self, namespace: str) -> PineconeVectorStore:
        """
        Get a LangChain PineconeVectorStore for a specific namespace.
        
        Args:
            namespace: Pinecone namespace
            
        Returns:
            PineconeVectorStore instance
        """
        # Get the appropriate index for this namespace
        index = self._get_index_for_namespace(namespace)
        
        return PineconeVectorStore(
            index=index,
            embedding=self.embeddings,
            namespace=namespace
        )
    
    def hybrid_search(
        self,
        query: str,
        namespace: str,
        keyword_boost: float = 0.3,
        top_k: int = None
    ) -> List[Dict]:
        """
        Perform hybrid search combining semantic and keyword matching.
        
        Args:
            query: Search query
            namespace: Namespace to search
            keyword_boost: Weight for keyword matching (0-1)
            top_k: Number of results
            
        Returns:
            List of documents
        """
        # For now, just use semantic search
        # Can be enhanced with BM25 or other keyword matching
        return self.query_namespace(query, namespace, top_k)


# Singleton instance
_pinecone_service = None

def get_pinecone_service() -> PineconeService:
    """Get or create singleton PineconeService instance."""
    global _pinecone_service
    if _pinecone_service is None:
        _pinecone_service = PineconeService()
    return _pinecone_service
