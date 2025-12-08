"""
Master indexing script to index all content into Pinecone.

This script runs all three indexers:
1. Papers indexer
2. Slides indexer  
3. Transcripts indexer
"""

import sys
from pathlib import Path

# Add backend root to path
backend_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_root))

from scripts.indexing.index_papers import PaperIndexer
from scripts.indexing.index_slides import SlideIndexer
from scripts.indexing.index_transcripts import TranscriptIndexer


def main():
    """Run all indexers."""
    print("\n" + "="*60)
    print("🚀 MASTER INDEXING SCRIPT")
    print("="*60)
    print("This will index all content into Pinecone:")
    print("  1. Research papers → 'papers' namespace")
    print("  2. Lecture slides → 'slides' namespace")
    print("  3. Transcripts → 'transcript' namespace")
    print("="*60 + "\n")
    
    input("Press Enter to continue or Ctrl+C to cancel...")
    
    errors = []
    
    # Index papers
    print("\n" + "🔹"*30)
    print("STEP 1/3: Indexing Papers")
    print("🔹"*30 + "\n")
    try:
        paper_indexer = PaperIndexer()
        paper_indexer.index_all_papers()
        paper_indexer.get_index_stats()
    except Exception as e:
        print(f"❌ Error indexing papers: {e}")
        errors.append(("Papers", str(e)))
    
    # Index slides
    print("\n" + "🔹"*30)
    print("STEP 2/3: Indexing Slides")
    print("🔹"*30 + "\n")
    try:
        slide_indexer = SlideIndexer()
        slide_indexer.index_all_slides()
        slide_indexer.get_index_stats()
    except Exception as e:
        print(f"❌ Error indexing slides: {e}")
        errors.append(("Slides", str(e)))
    
    # Index transcripts
    print("\n" + "🔹"*30)
    print("STEP 3/3: Indexing Transcripts")
    print("🔹"*30 + "\n")
    try:
        transcript_indexer = TranscriptIndexer()
        transcript_indexer.index_all_transcripts()
        transcript_indexer.get_index_stats()
    except Exception as e:
        print(f"❌ Error indexing transcripts: {e}")
        errors.append(("Transcripts", str(e)))
    
    # Summary
    print("\n" + "="*60)
    print("🎉 INDEXING COMPLETE!")
    print("="*60)
    
    if errors:
        print("\n⚠️  Some errors occurred:")
        for component, error in errors:
            print(f"  - {component}: {error}")
    else:
        print("\n✅ All content indexed successfully!")
    
    print("\nYour Pinecone index now has three namespaces:")
    print("  📚 papers - Research paper content")
    print("  📊 slides - Lecture slide content")
    print("  🎙️  transcript - Time-stamped transcripts")
    print("\nYou can now run the agent system!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
