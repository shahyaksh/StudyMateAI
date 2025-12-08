"""
Script to index research papers into Pinecone database.

This script:
1. Reads papers from the data/papers directory
2. Chunks the text into manageable pieces
3. Generates embeddings using OpenAI
4. Indexes into Pinecone 'papers' namespace with metadata
"""

import os
import sys
from pathlib import Path
from typing import List, Dict
import re
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "lecture-rag-index")

# Get the script directory
SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
PAPERS_DIR = SCRIPT_DIR / "data" / "papers"
NAMESPACE = "papers"

# Embedding configuration
EMBEDDING_MODEL = "text-embedding-3-small"  # OpenAI's latest small embedding model
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
BATCH_SIZE = 100


class PaperIndexer:
    """Indexes research papers into Pinecone."""
    
    def __init__(self):
        """Initialize the indexer with OpenAI embeddings and Pinecone client."""
        # Validate API keys
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        if not PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY not found in environment variables")
        
        # Initialize OpenAI embeddings
        print(f"🔧 Initializing OpenAI embeddings ({EMBEDDING_MODEL})...")
        self.embeddings = OpenAIEmbeddings(
            model=EMBEDDING_MODEL,
            openai_api_key=OPENAI_API_KEY
        )
        
        # Initialize Pinecone
        print(f"🔧 Connecting to Pinecone index: {PINECONE_INDEX_NAME}...")
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self.index = self.pc.Index(PINECONE_INDEX_NAME)
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        print("✅ Initialization complete!\n")
    
    def extract_paper_metadata(self, file_path: Path) -> Dict:
        """
        Extract metadata from paper file path and content.
        
        Args:
            file_path: Path to the paper file
            
        Returns:
            Dictionary with paper metadata
        """
        # Extract lecture from directory structure
        lecture_dir = file_path.parent.name
        lecture_match = re.search(r'Lecture\s+(\d+)', lecture_dir, re.IGNORECASE)
        lecture_id = lecture_match.group(0).lower().replace(" ", "_") if lecture_match else "unknown"
        
        # Extract paper name from filename
        paper_name = file_path.stem
        
        # Try to extract title from first few lines
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_lines = [f.readline().strip() for _ in range(5)]
                # Use the first non-empty line as title
                title = next((line for line in first_lines if line), paper_name)
        except Exception:
            title = paper_name
        
        return {
            "lecture_id": lecture_id,
            "paper_name": paper_name,
            "title": title,
            "source_file": str(file_path)
        }
    
    def read_paper(self, file_path: Path) -> str:
        """
        Read paper content from file.
        
        Args:
            file_path: Path to the paper file
            
        Returns:
            Paper content as string
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            return ""
    
    def chunk_paper(self, content: str, metadata: Dict) -> List[Dict]:
        """
        Chunk paper content into smaller pieces with metadata.
        
        Args:
            content: Paper content
            metadata: Paper metadata
            
        Returns:
            List of chunks with metadata
        """
        # Split into chunks
        chunks = self.text_splitter.split_text(content)
        
        # Create chunk documents with metadata
        chunk_docs = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                **metadata,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "text": chunk
            }
            chunk_docs.append(chunk_metadata)
        
        return chunk_docs
    
    def index_chunks(self, chunks: List[Dict], paper_name: str):
        """
        Index chunks into Pinecone.
        
        Args:
            chunks: List of chunk documents
            paper_name: Name of the paper (for progress display)
        """
        print(f"   📄 Indexing {len(chunks)} chunks from {paper_name}...")
        
        # Process in batches
        for i in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[i:i + BATCH_SIZE]
            
            # Extract texts for embedding
            texts = [chunk["text"] for chunk in batch]
            
            # Generate embeddings
            try:
                embeddings = self.embeddings.embed_documents(texts)
            except Exception as e:
                print(f"   ❌ Error generating embeddings: {e}")
                continue
            
            # Prepare vectors for Pinecone
            vectors = []
            for j, (chunk, embedding) in enumerate(zip(batch, embeddings)):
                vector_id = f"{chunk['paper_name']}_chunk_{chunk['chunk_index']}"
                
                # Prepare metadata (remove 'text' as it's stored separately)
                metadata = {k: v for k, v in chunk.items() if k != "text"}
                metadata["text"] = chunk["text"]  # Store text in metadata
                
                vectors.append({
                    "id": vector_id,
                    "values": embedding,
                    "metadata": metadata
                })
            
            # Upsert to Pinecone
            try:
                self.index.upsert(vectors=vectors, namespace=NAMESPACE)
            except Exception as e:
                print(f"   ❌ Error upserting to Pinecone: {e}")
                continue
        
        print(f"   ✅ Successfully indexed {len(chunks)} chunks")
    
    def index_paper(self, file_path: Path):
        """
        Index a single paper file.
        
        Args:
            file_path: Path to the paper file
        """
        print(f"\n📚 Processing: {file_path.name}")
        
        # Extract metadata
        metadata = self.extract_paper_metadata(file_path)
        
        # Read paper content
        content = self.read_paper(file_path)
        if not content:
            print(f"   ⚠️  Skipping empty file")
            return
        
        print(f"   📊 Content length: {len(content)} characters")
        
        # Chunk the paper
        chunks = self.chunk_paper(content, metadata)
        print(f"   ✂️  Created {len(chunks)} chunks")
        
        # Index chunks
        self.index_chunks(chunks, metadata["paper_name"])
    
    def index_all_papers(self):
        """Index all papers in the papers directory."""
        print("\n" + "="*60)
        print("📚 PAPER INDEXING STARTED")
        print("="*60)
        print(f"Papers directory: {PAPERS_DIR}")
        print(f"Namespace: {NAMESPACE}")
        print(f"Embedding model: {EMBEDDING_MODEL}")
        print(f"Chunk size: {CHUNK_SIZE}")
        print(f"Chunk overlap: {CHUNK_OVERLAP}")
        print("="*60 + "\n")
        
        # Convert to Path object
        papers_path = Path(PAPERS_DIR)
        
        # Check if directory exists
        if not papers_path.exists():
            print(f"❌ Papers directory does not exist: {papers_path}")
            print(f"   Please create the directory and add paper files.")
            return
        
        # Find all paper files
        paper_files = list(papers_path.rglob("*.txt"))
        paper_files.extend(papers_path.rglob("*.pdf"))
        
        if not paper_files:
            print("❌ No paper files found!")
            return
        
        print(f"Found {len(paper_files)} paper files\n")
        
        # Index each paper
        total_chunks = 0
        for file_path in tqdm(paper_files, desc="Indexing papers"):
            try:
                self.index_paper(file_path)
                # Get chunk count (approximate)
                content = self.read_paper(file_path)
                chunks = self.text_splitter.split_text(content)
                total_chunks += len(chunks)
            except Exception as e:
                print(f"❌ Error processing {file_path.name}: {e}")
                continue
        
        print("\n" + "="*60)
        print("✅ INDEXING COMPLETE!")
        print("="*60)
        print(f"Total papers indexed: {len(paper_files)}")
        print(f"Total chunks created: {total_chunks}")
        print(f"Namespace: {NAMESPACE}")
        print("="*60 + "\n")
    
    def get_index_stats(self):
        """Get statistics about the indexed papers."""
        try:
            stats = self.index.describe_index_stats()
            namespace_stats = stats.namespaces.get(NAMESPACE, {})
            
            print("\n" + "="*60)
            print("📊 INDEX STATISTICS")
            print("="*60)
            print(f"Namespace: {NAMESPACE}")
            print(f"Total vectors: {namespace_stats.get('vector_count', 0)}")
            print("="*60 + "\n")
        except Exception as e:
            print(f"❌ Error getting stats: {e}")


def main():
    """Main function to run the indexer."""
    try:
        # Create indexer
        indexer = PaperIndexer()
        
        # Index all papers
        indexer.index_all_papers()
        
        # Show stats
        indexer.get_index_stats()
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
