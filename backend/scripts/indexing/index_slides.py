"""
Script to index lecture slides into Pinecone database.

This script:
1. Reads slide content from the data/slides directory
2. Chunks the text if needed
3. Generates embeddings using OpenAI
4. Indexes into Pinecone 'slides' namespace with metadata
"""

import os
import sys
from pathlib import Path
from typing import List, Dict
import re
import json
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
SLIDES_DIR = SCRIPT_DIR / "data" / "slides"
NAMESPACE = "slides"

# Embedding configuration
EMBEDDING_MODEL = "text-embedding-3-small"
CHUNK_SIZE = 500  # Smaller chunks for slides
CHUNK_OVERLAP = 50
BATCH_SIZE = 100


class SlideIndexer:
    """Indexes lecture slides into Pinecone."""
    
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
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        print("✅ Initialization complete!\n")
    
    def parse_slide_file(self, file_path: Path) -> List[Dict]:
        """
        Parse slide file and extract individual slides.
        
        Expected format:
        - JSON: {"slides": [{"number": 1, "title": "...", "content": "..."}]}
        - Text: Slides separated by markers or numbered
        
        Args:
            file_path: Path to the slide file
            
        Returns:
            List of slide dictionaries
        """
        slides = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try JSON format first
            if file_path.suffix == '.json':
                data = json.loads(content)
                slides = data.get('slides', [])
            else:
                # Parse text format - look for slide markers
                # Common patterns: "Slide 1:", "--- Slide 1 ---", etc.
                slide_pattern = r'(?:^|\n)(?:Slide|SLIDE)\s*(\d+)[:\-\s]+(.*?)(?=(?:\n(?:Slide|SLIDE)\s*\d+)|$)'
                matches = re.finditer(slide_pattern, content, re.DOTALL | re.IGNORECASE)
                
                for match in matches:
                    slide_num = int(match.group(1))
                    slide_content = match.group(2).strip()
                    
                    # Try to extract title (first line)
                    lines = slide_content.split('\n')
                    title = lines[0].strip() if lines else f"Slide {slide_num}"
                    content_text = '\n'.join(lines[1:]).strip() if len(lines) > 1 else slide_content
                    
                    slides.append({
                        "number": slide_num,
                        "title": title,
                        "content": content_text
                    })
                
                # If no pattern matched, treat entire file as one slide
                if not slides:
                    slides.append({
                        "number": 1,
                        "title": file_path.stem,
                        "content": content
                    })
        
        except Exception as e:
            print(f"❌ Error parsing {file_path}: {e}")
        
        return slides
    
    def index_slide(self, slide: Dict, lecture_id: str, source_file: str):
        """
        Index a single slide into Pinecone.
        
        Args:
            slide: Slide dictionary with number, title, content
            lecture_id: Lecture identifier
            source_file: Source file path
        """
        slide_content = f"{slide.get('title', '')}\n\n{slide.get('content', '')}"
        
        # Generate embedding
        try:
            embedding = self.embeddings.embed_query(slide_content)
        except Exception as e:
            print(f"   ❌ Error generating embedding for slide {slide.get('number')}: {e}")
            return
        
        # Prepare metadata
        metadata = {
            "slide_number": slide.get("number", 0),
            "slide_title": slide.get("title", ""),
            "lecture_id": lecture_id,
            "source_file": source_file,
            "text": slide_content
        }
        
        # Create vector ID
        vector_id = f"{lecture_id}_slide_{slide.get('number', 0)}"
        
        # Upsert to Pinecone
        try:
            self.index.upsert(
                vectors=[{
                    "id": vector_id,
                    "values": embedding,
                    "metadata": metadata
                }],
                namespace=NAMESPACE
            )
        except Exception as e:
            print(f"   ❌ Error upserting slide {slide.get('number')}: {e}")
    
    def index_slide_file(self, file_path: Path):
        """
        Index all slides from a file.
        
        Args:
            file_path: Path to the slide file
        """
        print(f"\n📊 Processing: {file_path.name}")
        
        # Extract lecture ID from path
        lecture_dir = file_path.parent.name
        lecture_match = re.search(r'Lecture\s+(\d+)', lecture_dir, re.IGNORECASE)
        lecture_id = lecture_match.group(0).lower().replace(" ", "_") if lecture_match else "unknown"
        
        # Parse slides
        slides = self.parse_slide_file(file_path)
        
        if not slides:
            print(f"   ⚠️  No slides found in file")
            return
        
        print(f"   📄 Found {len(slides)} slides")
        
        # Index each slide
        for slide in slides:
            self.index_slide(slide, lecture_id, str(file_path))
        
        print(f"   ✅ Indexed {len(slides)} slides")
    
    def index_all_slides(self):
        """Index all slide files."""
        print("\n" + "="*60)
        print("📊 SLIDE INDEXING STARTED")
        print("="*60)
        print(f"Slides directory: {SLIDES_DIR}")
        print(f"Namespace: {NAMESPACE}")
        print(f"Embedding model: {EMBEDDING_MODEL}")
        print("="*60 + "\n")
        
        # Ensure SLIDES_DIR is a Path object
        slides_path = Path(SLIDES_DIR) if not isinstance(SLIDES_DIR, Path) else SLIDES_DIR
        
        # Check if directory exists
        if not slides_path.exists():
            print(f"❌ Slides directory does not exist: {slides_path}")
            print(f"   Please create the directory and add slide files.")
            return
        
        # Find all slide files
        slide_files = list(slides_path.rglob("*.txt"))
        slide_files.extend(slides_path.rglob("*.json"))
        
        if not slide_files:
            print("❌ No slide files found!")
            print(f"   Please add slide files to: {SLIDES_DIR}")
            return
        
        print(f"Found {len(slide_files)} slide files\n")
        
        # Index each file
        total_slides = 0
        for file_path in tqdm(slide_files, desc="Indexing slides"):
            try:
                slides = self.parse_slide_file(file_path)
                total_slides += len(slides)
                self.index_slide_file(file_path)
            except Exception as e:
                print(f"❌ Error processing {file_path.name}: {e}")
                continue
        
        print("\n" + "="*60)
        print("✅ INDEXING COMPLETE!")
        print("="*60)
        print(f"Total slide files: {len(slide_files)}")
        print(f"Total slides indexed: {total_slides}")
        print(f"Namespace: {NAMESPACE}")
        print("="*60 + "\n")
    
    def get_index_stats(self):
        """Get statistics about the indexed slides."""
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
        indexer = SlideIndexer()
        indexer.index_all_slides()
        indexer.get_index_stats()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
