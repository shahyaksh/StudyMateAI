"""
Script to create and set up the Pinecone index for the lecture RAG system.

This script creates a Pinecone index with the correct configuration for OpenAI embeddings.
"""

import os
import sys
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# Load environment variables
load_dotenv()

# Configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "lecture-rag-index")

# OpenAI text-embedding-3-small has 1536 dimensions
EMBEDDING_DIMENSION = 1536


def create_pinecone_index():
    """Create the Pinecone index if it doesn't exist."""
    
    if not PINECONE_API_KEY:
        print("❌ Error: PINECONE_API_KEY not found in environment variables")
        print("Please set it in your .env file")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("🔧 PINECONE INDEX SETUP")
    print("="*60)
    print(f"Index name: {PINECONE_INDEX_NAME}")
    print(f"Environment: {PINECONE_ENVIRONMENT}")
    print(f"Embedding dimension: {EMBEDDING_DIMENSION}")
    print(f"Metric: cosine")
    print("="*60 + "\n")
    
    try:
        # Initialize Pinecone
        pc = Pinecone(api_key=PINECONE_API_KEY)
        
        # Check if index already exists
        existing_indexes = [index.name for index in pc.list_indexes()]
        
        if PINECONE_INDEX_NAME in existing_indexes:
            print(f"✅ Index '{PINECONE_INDEX_NAME}' already exists!")
            
            # Get index info
            index = pc.Index(PINECONE_INDEX_NAME)
            stats = index.describe_index_stats()
            
            print("\n📊 Current Index Statistics:")
            print(f"   Total vectors: {stats.total_vector_count}")
            print(f"   Dimension: {stats.dimension}")
            
            if stats.namespaces:
                print("\n   Namespaces:")
                for namespace, ns_stats in stats.namespaces.items():
                    print(f"      - {namespace}: {ns_stats.vector_count} vectors")
            else:
                print("   No namespaces yet (empty index)")
            
            print("\n⚠️  Do you want to delete and recreate the index? (y/N): ", end="")
            response = input().strip().lower()
            
            if response == 'y':
                print(f"\n🗑️  Deleting existing index '{PINECONE_INDEX_NAME}'...")
                pc.delete_index(PINECONE_INDEX_NAME)
                print("✅ Index deleted")
            else:
                print("\n✅ Keeping existing index. Exiting.")
                return
        
        # Create new index
        print(f"\n🔨 Creating new index '{PINECONE_INDEX_NAME}'...")
        
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=EMBEDDING_DIMENSION,
            metric='cosine',
            spec=ServerlessSpec(
                cloud='aws',
                region=PINECONE_ENVIRONMENT
            )
        )
        
        print("✅ Index created successfully!")
        
        # Wait for index to be ready
        print("\n⏳ Waiting for index to be ready...")
        import time
        max_wait = 60  # Maximum 60 seconds
        waited = 0
        
        while waited < max_wait:
            try:
                index = pc.Index(PINECONE_INDEX_NAME)
                stats = index.describe_index_stats()
                print("✅ Index is ready!")
                break
            except Exception:
                time.sleep(2)
                waited += 2
                print(f"   Still waiting... ({waited}s)")
        
        print("\n" + "="*60)
        print("✅ SETUP COMPLETE!")
        print("="*60)
        print("\nYour Pinecone index is ready for indexing.")
        print("\nNext steps:")
        print("1. Run: python index_papers.py")
        print("2. Run: python index_slides.py")
        print("3. Run: python index_transcripts.py")
        print("\nOr run all at once:")
        print("   python index_all.py")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main function."""
    create_pinecone_index()


if __name__ == "__main__":
    main()
