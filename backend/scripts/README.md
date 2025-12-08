# Backend Scripts

This directory contains utility scripts for setup, indexing, and preprocessing.

## Directory Structure

```
scripts/
├── setup/              # Setup and initialization scripts
│   ├── setup.sh        # Automated setup script
│   └── setup_pinecone.py  # Pinecone index creation
├── indexing/           # Data indexing scripts
│   ├── index_all.py    # Master script to index all content
│   ├── index_papers.py # Index research papers
│   ├── index_slides.py # Index lecture slides
│   └── index_transcripts.py  # Index transcripts
└── preprocessing/      # Data preprocessing scripts
    ├── preprocess_transcript.py  # Process raw transcripts
    └── extract_pdf_text.py       # Extract text from PDFs
```

## Usage

### Initial Setup

Run from backend root directory:

```bash
# Option 1: Use setup script
bash scripts/setup/setup.sh

# Option 2: Manual setup
python scripts/setup/setup_pinecone.py
```

### Indexing Content

Run from backend root directory:

```bash
# Index all content at once
python -m scripts.indexing.index_all

# Or index individually
python -m scripts.indexing.index_papers
python -m scripts.indexing.index_slides
python -m scripts.indexing.index_transcripts
```

### Preprocessing

Run from backend root directory:

```bash
# Preprocess transcripts
python -m scripts.preprocessing.preprocess_transcript

# Extract PDF text
python -m scripts.preprocessing.extract_pdf_text
```

## Notes

- All scripts should be run from the `backend/` root directory
- Ensure `.env` file is configured before running scripts
- Scripts use relative imports and path manipulation to access backend modules
