"""
Process PDF files into text chunks for embedding
"""
import json
from pathlib import Path
from typing import List, Dict
import PyPDF2


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract text from a PDF file"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                text += f"\n--- Page {page_num + 1} ---\n{page_text}"
            return text
    except Exception as e:
        print(f"❌ Error reading {pdf_path.name}: {e}")
        return ""


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks"""
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        
        # Try to break at sentence boundary
        if end < text_length:
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            break_point = max(last_period, last_newline)
            
            if break_point > chunk_size * 0.5:  # Only break if we're past halfway
                chunk = chunk[:break_point + 1]
                end = start + break_point + 1
        
        chunks.append(chunk.strip())
        start = end - overlap
    
    return chunks


def process_pdfs():
    """Process all PDFs in data/raw/ directory"""
    
    # Paths
    raw_dir = Path("data/raw")
    output_file = Path("data/processed/pdfs_processed.json")
    
    # Create output directory
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Find all PDFs
    pdf_files = list(raw_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ No PDF files found in data/raw/")
        return
    
    print(f"📚 Found {len(pdf_files)} PDF files")
    
    all_chunks = []
    
    for pdf_file in pdf_files:
        print(f"\n📄 Processing: {pdf_file.name}...")
        
        # Extract text
        text = extract_text_from_pdf(pdf_file)
        
        if not text:
            print(f"⚠️  No text extracted from {pdf_file.name}")
            continue
        
        print(f"   Extracted {len(text)} characters")
        
        # Chunk text
        chunks = chunk_text(text, chunk_size=1000, overlap=200)
        print(f"   Created {len(chunks)} chunks")
        
        # Add to processed list
        for idx, chunk in enumerate(chunks):
            all_chunks.append({
                "id": f"{pdf_file.stem}_chunk_{idx}",
                "text": chunk,
                "metadata": {
                    "source": pdf_file.name,
                    "type": "guideline",
                    "chunk_index": idx,
                    "total_chunks": len(chunks)
                }
            })
    
    # Save processed data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Processed {len(pdf_files)} PDFs into {len(all_chunks)} chunks")
    print(f"💾 Saved to {output_file}")
    
    # Show sample
    if all_chunks:
        print("\n📋 Sample Chunk (first 300 chars):")
        print(all_chunks[0]['text'][:300] + "...")
        print(f"\n📊 Metadata: {all_chunks[0]['metadata']}")


if __name__ == "__main__":
    process_pdfs()
