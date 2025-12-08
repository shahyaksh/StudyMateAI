"""
Script to index lecture transcripts into Pinecone database.

This script:
1. Reads transcript from the data directory
2. Chunks by time segments (e.g., 60-second chunks)
3. Generates embeddings using OpenAI
4. Indexes into Pinecone 'transcript' namespace with timestamp metadata
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import re
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from tqdm import tqdm

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "lecture-rag-index")

# Get the script directory
SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
TRANSCRIPT_FILE = SCRIPT_DIR / "data" / "transcript.txt"
NAMESPACE = "transcript"

# Embedding configuration
EMBEDDING_MODEL = "text-embedding-3-small"
TIME_CHUNK_SECONDS = 60  # Chunk transcript by 60-second segments
BATCH_SIZE = 100


class TranscriptIndexer:
    """Indexes lecture transcripts into Pinecone with timestamp information."""
    
    def __init__(self):
        """Initialize the indexer with OpenAI embeddings and Pinecone client."""
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        if not PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY not found in environment variables")
        
        print(f"🔧 Initializing OpenAI embeddings ({EMBEDDING_MODEL})...")
        self.embeddings = OpenAIEmbeddings(
            model=EMBEDDING_MODEL,
            openai_api_key=OPENAI_API_KEY
        )
        
        print(f"🔧 Connecting to Pinecone index: {PINECONE_INDEX_NAME}...")
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self.index = self.pc.Index(PINECONE_INDEX_NAME)
        
        print("✅ Initialization complete!\n")
    
    def parse_timestamp(self, timestamp_str: str) -> float:
        """
        Parse timestamp string to seconds.
        
        Supports formats:
        - HH:MM:SS
        - MM:SS
        - SS
        
        Args:
            timestamp_str: Timestamp string
            
        Returns:
            Time in seconds
        """
        parts = timestamp_str.strip().split(':')
        
        if len(parts) == 3:  # HH:MM:SS
            hours, minutes, seconds = map(float, parts)
            return hours * 3600 + minutes * 60 + seconds
        elif len(parts) == 2:  # MM:SS
            minutes, seconds = map(float, parts)
            return minutes * 60 + seconds
        else:  # SS
            return float(parts[0])
    
    def parse_transcript(self, file_path: Path) -> List[Dict]:
        """
        Parse transcript file with timestamps.
        
        Expected format:
        [00:00:15] Speaker: Text here
        or
        0:15 - Text here
        
        Args:
            file_path: Path to transcript file
            
        Returns:
            List of transcript segments with timestamps
        """
        segments = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Pattern 1: [HH:MM:SS] or [MM:SS] format
            pattern1 = r'\[(\d{1,2}:\d{2}(?::\d{2})?)\]\s*(?:[\w\s]+:)?\s*(.+?)(?=\[|\Z)'
            matches1 = re.finditer(pattern1, content, re.DOTALL)
            
            for match in matches1:
                timestamp_str = match.group(1)
                text = match.group(2).strip()
                
                if text:
                    timestamp = self.parse_timestamp(timestamp_str)
                    segments.append({
                        "timestamp": timestamp,
                        "text": text
                    })
            
            # Pattern 2: MM:SS - Text format
            if not segments:
                pattern2 = r'(\d{1,2}:\d{2}(?::\d{2})?)\s*[-–]\s*(.+?)(?=\d{1,2}:\d{2}|\Z)'
                matches2 = re.finditer(pattern2, content, re.DOTALL)
                
                for match in matches2:
                    timestamp_str = match.group(1)
                    text = match.group(2).strip()
                    
                    if text:
                        timestamp = self.parse_timestamp(timestamp_str)
                        segments.append({
                            "timestamp": timestamp,
                            "text": text
                        })
            
            # If no timestamps found, chunk by sentences
            if not segments:
                print("   ⚠️  No timestamps found, chunking by sentences...")
                sentences = re.split(r'[.!?]+', content)
                current_time = 0.0
                
                for sentence in sentences:
                    sentence = sentence.strip()
                    if sentence:
                        segments.append({
                            "timestamp": current_time,
                            "text": sentence
                        })
                        # Estimate 3 seconds per sentence
                        current_time += 3.0
        
        except Exception as e:
            print(f"❌ Error parsing transcript: {e}")
        
        return segments
    
    def create_time_chunks(self, segments: List[Dict]) -> List[Dict]:
        """
        Group transcript segments into time-based chunks.
        
        Args:
            segments: List of transcript segments with timestamps
            
        Returns:
            List of time-chunked segments
        """
        if not segments:
            return []
        
        chunks = []
        current_chunk = {
            "start_time": 0.0,
            "end_time": TIME_CHUNK_SECONDS,
            "text": ""
        }
        
        for segment in segments:
            timestamp = segment["timestamp"]
            text = segment["text"]
            
            # If segment is within current chunk time window
            if timestamp < current_chunk["end_time"]:
                current_chunk["text"] += " " + text
            else:
                # Save current chunk if it has content
                if current_chunk["text"].strip():
                    chunks.append(current_chunk)
                
                # Start new chunk
                chunk_index = int(timestamp // TIME_CHUNK_SECONDS)
                current_chunk = {
                    "start_time": chunk_index * TIME_CHUNK_SECONDS,
                    "end_time": (chunk_index + 1) * TIME_CHUNK_SECONDS,
                    "text": text
                }
        
        # Add last chunk
        if current_chunk["text"].strip():
            chunks.append(current_chunk)
        
        return chunks
    
    def index_chunks(self, chunks: List[Dict], lecture_id: str = "lecture_unknown"):
        """
        Index transcript chunks into Pinecone.
        
        Args:
            chunks: List of time-chunked segments
            lecture_id: Lecture identifier
        """
        print(f"   📝 Indexing {len(chunks)} transcript chunks...")
        
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
                vector_id = f"{lecture_id}_transcript_{int(chunk['start_time'])}"
                
                metadata = {
                    "start_time": chunk["start_time"],
                    "end_time": chunk["end_time"],
                    "lecture_id": lecture_id,
                    "text": chunk["text"]
                }
                
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
    
    def index_transcript(self, file_path: Path, lecture_id: str = None):
        """
        Index a transcript file.
        
        Args:
            file_path: Path to transcript file
            lecture_id: Optional lecture identifier
        """
        print(f"\n🎙️  Processing: {file_path.name}")
        
        # Extract lecture ID from filename if not provided
        if not lecture_id:
            lecture_match = re.search(r'lecture[_\s]*(\d+)', file_path.stem, re.IGNORECASE)
            lecture_id = f"lecture_{lecture_match.group(1)}" if lecture_match else "lecture_unknown"
        
        # Parse transcript
        segments = self.parse_transcript(file_path)
        
        if not segments:
            print(f"   ⚠️  No transcript segments found")
            return
        
        print(f"   📊 Parsed {len(segments)} transcript segments")
        
        # Create time-based chunks
        chunks = self.create_time_chunks(segments)
        print(f"   ✂️  Created {len(chunks)} time chunks ({TIME_CHUNK_SECONDS}s each)")
        
        # Index chunks
        self.index_chunks(chunks, lecture_id)
    
    def index_all_transcripts(self):
        """Index all transcript files."""
        print("\n" + "="*60)
        print("🎙️  TRANSCRIPT INDEXING STARTED")
        print("="*60)
        print(f"Transcript file: {TRANSCRIPT_FILE}")
        print(f"Namespace: {NAMESPACE}")
        print(f"Embedding model: {EMBEDDING_MODEL}")
        print(f"Time chunk size: {TIME_CHUNK_SECONDS} seconds")
        print("="*60 + "\n")
        
        # Ensure TRANSCRIPT_FILE is a Path object
        transcript_path = Path(TRANSCRIPT_FILE) if not isinstance(TRANSCRIPT_FILE, Path) else TRANSCRIPT_FILE
        
        # Check if transcript file exists
        if not transcript_path.exists():
            print(f"❌ Transcript file not found: {transcript_path}")
            return
        
        # Index the transcript
        try:
            self.index_transcript(TRANSCRIPT_FILE)
        except Exception as e:
            print(f"❌ Error processing transcript: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*60)
        print("✅ INDEXING COMPLETE!")
        print("="*60 + "\n")
    
    def get_index_stats(self):
        """Get statistics about the indexed transcripts."""
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
        indexer = TranscriptIndexer()
        indexer.index_all_transcripts()
        indexer.get_index_stats()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
