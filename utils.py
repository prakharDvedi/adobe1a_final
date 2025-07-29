import re
from typing import List, Dict

def clean_text(text: str) -> str:
    if not text:
        return ""
    
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    text = re.sub(r'[^\w\s\-\.\,\:\;\(\)\[\]\/\&\@\#\$\%\+\=\?\!]', '', text)
    
    return text

def is_heading_like(text: str) -> bool:
    if not text:
        return False
        
    patterns = [
        r'^[A-Z][A-Z\s&]+$',
        r'^\d+\.\s*[A-Z]',
        r'^\d+\.\d+\s*[A-Z]',
        r'^Chapter\s+\d+',
        r'^Section\s+\d+',
        r'^Appendix\s+[A-Z]',
        r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]*)*\s*$',
    ]
    
    for pattern in patterns:
        if re.match(pattern, text):
            return True
            
    if len(text) > 3 and sum(1 for c in text if c.isupper()) / len(text) > 0.7:
        return True
        
    return False

def determine_heading_level(text: str, chars: List[Dict]) -> str:
    if not text:
        return "H3"
        
    avg_size = 12
    if chars:
        sizes = [char.get('size', 12) for char in chars if char.get('size')]
        if sizes:
            avg_size = sum(sizes) / len(sizes)
    
    if re.match(r'^\d+\.\s*[A-Z]', text) or avg_size > 16 or text.isupper():
        return "H1"
    elif re.match(r'^\d+\.\d+\s*[A-Z]', text) or avg_size > 14:
        return "H2"
    else:
        return "H3"
