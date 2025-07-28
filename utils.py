import re
from typing import List, Dict

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # Remove common PDF artifacts
    text = re.sub(r'[^\w\s\-\.\,\:\;\(\)\[\]\/\&\@\#\$\%\+\=\?\!]', '', text)
    
    return text

def is_heading_like(text: str) -> bool:
    """Check if text looks like a heading"""
    if not text:
        return False
        
    # Common heading patterns
    patterns = [
        r'^[A-Z][A-Z\s&]+$',  # ALL CAPS
        r'^\d+\.\s*[A-Z]',    # 1. Title
        r'^\d+\.\d+\s*[A-Z]', # 1.1 Title
        r'^Chapter\s+\d+',    # Chapter X
        r'^Section\s+\d+',    # Section X
        r'^Appendix\s+[A-Z]', # Appendix A
        r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]*)*\s*$',  # Title Case
    ]
    
    for pattern in patterns:
        if re.match(pattern, text):
            return True
            
    # Check if mostly uppercase
    if len(text) > 3 and sum(1 for c in text if c.isupper()) / len(text) > 0.7:
        return True
        
    return False

def determine_heading_level(text: str, chars: List[Dict]) -> str:
    """Determine heading level based on text and formatting"""
    if not text:
        return "H3"
        
    # Calculate average font size
    avg_size = 12  # default
    if chars:
        sizes = [char.get('size', 12) for char in chars if char.get('size')]
        if sizes:
            avg_size = sum(sizes) / len(sizes)
    
    # Level determination based on patterns and font size
    if re.match(r'^\d+\.\s*[A-Z]', text) or avg_size > 16 or text.isupper():
        return "H1"
    elif re.match(r'^\d+\.\d+\s*[A-Z]', text) or avg_size > 14:
        return "H2"
    else:
        return "H3"
