#!/usr/bin/env python3
"""
Function to extract text from PowerPoint PDFs slide-wise.
Each page in the PDF corresponds to one slide.
"""

import os
from typing import List, Dict, Optional
from pathlib import Path

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False


def extract_text_with_pypdf2(pdf_path: str) -> List[Dict[str, any]]:
    """
    Extract text from PDF using PyPDF2 (page by page).
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        List of dictionaries with 'slide_number' and 'text' keys
    """
    slides = []
    
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        total_pages = len(pdf_reader.pages)
        
        for page_num in range(total_pages):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            
            slides.append({
                'slide_number': page_num + 1,
                'text': text.strip(),
                'page_number': page_num + 1
            })
    
    return slides


def extract_text_with_pdfplumber(pdf_path: str) -> List[Dict[str, any]]:
    """
    Extract text from PDF using pdfplumber (better text extraction quality).
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        List of dictionaries with 'slide_number' and 'text' keys
    """
    slides = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            print(f"Page {page_num}:") 
            print(text)
            print("-"*100)
            slides.append({
                'slide_number': page_num,
                'text': text.strip() if text else '',
                'page_number': page_num
            })
    
    return slides


def extract_text_slidewise(
    pdf_path: str,
    use_pdfplumber: bool = True
) -> List[Dict[str, any]]:
    """
    Extract text from PowerPoint PDF slide-wise.
    Each page in the PDF corresponds to one slide.
    
    Args:
        pdf_path: Path to the PDF file
        use_pdfplumber: If True, use pdfplumber (better quality), 
                       otherwise use PyPDF2. Falls back to PyPDF2 if pdfplumber not available.
        
    Returns:
        List of dictionaries, each containing:
            - slide_number: int (1-indexed)
            - text: str (extracted text from the slide)
            - page_number: int (same as slide_number for PDFs)
    
    Raises:
        FileNotFoundError: If PDF file doesn't exist
        ValueError: If no PDF library is available
    """
    # Check if file exists
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    # Try to use pdfplumber if requested and available
    if use_pdfplumber and HAS_PDFPLUMBER:
        return extract_text_with_pdfplumber(pdf_path)
    
    # Fall back to PyPDF2
    if HAS_PYPDF2:
        return extract_text_with_pypdf2(pdf_path)
    
    # If neither library is available
    raise ValueError(
        "No PDF library available. Please install PyPDF2 or pdfplumber:\n"
        "  pip install PyPDF2\n"
        "  # or for better quality:\n"
        "  pip install pdfplumber"
    )


def extract_text_slidewise_to_dict(pdf_path: str, use_pdfplumber: bool = True) -> Dict[int, str]:
    """
    Extract text from PowerPoint PDF slide-wise and return as a dictionary.
    
    Args:
        pdf_path: Path to the PDF file
        use_pdfplumber: If True, use pdfplumber, otherwise use PyPDF2
        
    Returns:
        Dictionary mapping slide_number (int) to text (str)
    """
    slides = extract_text_slidewise(pdf_path, use_pdfplumber)
    return {slide['slide_number']: slide['text'] for slide in slides}


def extract_text_slidewise_to_list(pdf_path: str, use_pdfplumber: bool = True) -> List[str]:
    """
    Extract text from PowerPoint PDF slide-wise and return as a list of strings.
    
    Args:
        pdf_path: Path to the PDF file
        use_pdfplumber: If True, use pdfplumber, otherwise use PyPDF2
        
    Returns:
        List of text strings, one per slide (ordered by slide number)
    """
    slides = extract_text_slidewise(pdf_path, use_pdfplumber)
    return [slide['text'] for slide in slides]


def extract_all_pdfs_from_directory(
    directory_path: str,
    use_pdfplumber: bool = True
) -> Dict[str, List[Dict[str, any]]]:
    """
    Extract text from all PDF files in a directory.
    
    Args:
        directory_path: Path to directory containing PDF files
        use_pdfplumber: If True, use pdfplumber, otherwise use PyPDF2
        
    Returns:
        Dictionary mapping PDF filename to list of slide dictionaries
    """
    pdf_dir = Path(directory_path)
    if not pdf_dir.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")
    
    results = {}
    
    for pdf_file in pdf_dir.glob('*.pdf'):
        try:
            slides = extract_text_slidewise(str(pdf_file), use_pdfplumber)
            results[pdf_file.name] = slides
            print(f"✓ Extracted {len(slides)} slides from {pdf_file.name}")
        except Exception as e:
            print(f"✗ Error processing {pdf_file.name}: {str(e)}")
            results[pdf_file.name] = []
    
    return results


if __name__ == "__main__":
    # Example usage
    import sys
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pdfs_dir = os.path.join(script_dir, 'data', 'pdfs')
    
    # If a specific PDF is provided as argument, extract from that
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        if not os.path.isabs(pdf_path):
            pdf_path = os.path.join(pdfs_dir, pdf_path)
    else:
        # Default: extract from all PDFs in the directory
        print(f"Extracting text from all PDFs in: {pdfs_dir}\n")
        results = extract_all_pdfs_from_directory(pdfs_dir)
        
        # Print summary
        for filename, slides in results.items():
            print(f"\n{'='*60}")
            print(f"File: {filename}")
            print(f"Total slides: {len(slides)}")
            print(f"{'='*60}")
            
            # Print first 3 slides as example
            for slide in slides[:3]:
                print(f"\nSlide {slide['slide_number']}:")
                print(f"{'-'*60}")
                text_preview = slide['text'][:200] + "..." if len(slide['text']) > 200 else slide['text']
                print(text_preview)
        
        sys.exit(0)
    
    # Extract from single PDF
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    print(f"Extracting text from: {pdf_path}\n")
    slides = extract_text_slidewise(pdf_path)
    
    print(f"Total slides: {len(slides)}\n")
    print(f"{'='*60}")
    
    # Print all slides
    for slide in slides:
        print(f"\nSlide {slide['slide_number']}:")
        print(f"{'-'*60}")
        print(slide['text'])
        print()

