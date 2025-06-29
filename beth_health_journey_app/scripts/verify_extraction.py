import os
from pathlib import Path
import fitz  # PyMuPDF

def verify_pdf_text_extraction(pdf_folder, text_folder):
    issues = []
    pdf_files = list(Path(pdf_folder).glob("*.pdf"))
    
    for pdf_path in pdf_files:
        text_path = Path(text_folder) / f"{pdf_path.stem}.txt"
        
        # Extract text from PDF
        doc = fitz.open(pdf_path)
        pdf_text = "\n".join([page.get_text() for page in doc])
        
        # Compare with existing extraction
        if text_path.exists():
            with open(text_path, 'r') as f:
                existing_text = f.read()
            
            if pdf_text.strip() != existing_text.strip():
                issues.append({
                    'file': pdf_path.name,
                    'issue': 'Text mismatch',
                    'pdf_length': len(pdf_text),
                    'existing_length': len(existing_text)
                })
        else:
            issues.append({
                'file': pdf_path.name,
                'issue': 'Missing text file'
            })
    
    return issues
