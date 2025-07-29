import re
import pdfplumber
from typing import Dict, List

class PDFOutlineExtractor:
    def __init__(self):
        pass

    def extract_outline(self, pdf_path: str) -> Dict:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                title = self._extract_title(pdf)
                outline = self._extract_headings(pdf)
                
                return {"title": title, "outline": outline}
        except Exception as e:
            return {"title": "", "outline": []}

    def _extract_title(self, pdf) -> str:
        if not pdf.pages:
            return ""
            
        text = pdf.pages[0].extract_text()
        if not text:
            return ""
            
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        for i, line in enumerate(lines[:15]):
            if len(line) < 5:
                continue
                
            if self._is_header_footer(line):
                continue
                
            if self._has_too_many_special_chars(line):
                continue
                
            if self._looks_like_title(line):
                return line.strip()
        
        for line in lines[:10]:
            if len(line) > 10 and not self._is_header_footer(line):
                return line.strip()
                
        return ""

    def _is_header_footer(self, text: str) -> bool:
        header_footer_patterns = [
            r'^Page\s+\d+',
            r'^\d+\s*$',
            r'^www\.',
            r'@.*\.com',
            r'^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            r'^Microsoft\s+Word',
            r'\.pdf\s*$',
            r'\.doc\s*$',
        ]
        
        for pattern in header_footer_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def _has_too_many_special_chars(self, text: str) -> bool:
        special_chars = sum(1 for c in text if not c.isalnum() and c not in ' -.,()[]{}:;')
        return special_chars > len(text) * 0.3

    def _looks_like_title(self, text: str) -> bool:
        word_count = len(text.split())
        
        if not (2 <= word_count <= 15):
            return False
            
        if not text[0].isupper():
            return False
            
        if text.isupper() and len(text) > 20:
            return False
            
        body_endings = [
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'
        ]
        last_word = text.split()[-1].lower().rstrip('.,;:')
        if last_word in body_endings:
            return False
            
        return True

    def _extract_headings(self, pdf) -> List[Dict]:
        headings = []
        seen = set()
        
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text:
                continue
                
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            for line in lines:
                if self._should_ignore_line(line):
                    continue
                
                level = self._classify_generic_heading(line)
                if level:
                    line_key = line.lower().strip()
                    if line_key not in seen:
                        seen.add(line_key)
                        headings.append({
                            "level": level,
                            "text": line,
                            "page": page_num
                        })
        
        return sorted(headings, key=lambda x: x['page'])

    def _should_ignore_line(self, text: str) -> bool:
        if not text or len(text) < 3:
            return True
            
        ignore_patterns = [
            r'^Microsoft Word',
            r'\.pdf\s*$',
            r'\.doc\s*$',
            r'^\d+\s*$',
            r'^Page\s+\d+',
            r'^www\.',
            r'@.*\.com',
            r'^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # dates
            r'^[A-Z]{2,}\s+\d+',
            r'^©.*\d{4}',
            r'^\s*\|\s*',
            r'^\s*[-=_]{3,}\s*$',
        ]
        
        for pattern in ignore_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        if self._has_too_many_special_chars(text):
            return True
            
        if len(text) > 200:
            return True
            
        body_starters = [
            r'^This\s+',
            r'^The\s+following',
            r'^It\s+is',
            r'^For\s+more',
            r'^In\s+order\s+to',
            r'^Please\s+',
            r'^You\s+can',
            r'^We\s+',
            r'^If\s+you',
            r'^To\s+',
            r'^When\s+',
            r'^Where\s+',
            r'^How\s+to',
            r'^Note\s+that',
            r'^Remember\s+',
        ]
        
        for pattern in body_starters:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False

    def _classify_generic_heading(self, text: str) -> str:
        if not text:
            return None
            
        h1_patterns = [
            r'^(Chapter|Section|Part)\s+[IVX\d]+[.:]?\s+[A-Z]',
            r'^\d+\.\s+[A-Z][a-zA-Z\s]{5,}$',
            
            r'^(Introduction|Overview|Summary|Conclusion|References|Bibliography|Appendix|Index|Table\s+of\s+Contents|Acknowledgements?|Abstract|Executive\s+Summary)\s*$',
            
            r'^[A-Z][A-Z\s]{5,30}$',
            
            r'^[A-Z][a-zA-Z\s\u2013\-]{10,50}$',
        ]
        
        h2_patterns = [
            r'^\d+\.\d+\s+[A-Z][a-zA-Z\s]{3,}$',
            
            r'^[A-Z][.)]\s+[A-Z][a-zA-Z\s]{3,}$',
            
            r'^(Background|Methodology|Results|Discussion|Findings|Recommendations|Objectives|Goals|Requirements|Specifications|Details|Analysis|Implementation|Testing|Evaluation)\s*$',
            
            r'^[A-Z][a-zA-Z\s]{5,30}:\s*$',
        ]
        
        h3_patterns = [
            r'^\d+\.\d+\.\d+\s+[A-Z][a-zA-Z\s]{3,}$',
            
            r'^[•\-\*]\s+[A-Z][a-zA-Z\s]{3,}$',
            
            r'^\([a-z\d]+\)\s+[A-Z][a-zA-Z\s]{3,}$',
            
            r'^(What|How|Why|When|Where|Who)\s+[a-z][a-zA-Z\s]{5,}\??\s*$',
        ]
        
        h4_patterns = [
            r'^\d+\.\d+\.\d+\.\d+\s+[A-Z][a-zA-Z\s]{3,}$',
            
            r'^[A-Z][a-z]+\s+[A-Z][a-z]+\s*:?\s*$',
        ]
        
        for pattern in h1_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return "H1"
        
        for pattern in h2_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return "H2"
                
        for pattern in h3_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return "H3"
                
        for pattern in h4_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return "H4"
        
        return self._classify_by_heuristics(text)

    def _classify_by_heuristics(self, text: str) -> str:
        words = text.split()
        word_count = len(words)
        
        if word_count > 20:
            return None
            
        if word_count < 2:
            return None
            
        is_title_case = all(word[0].isupper() for word in words if word.isalpha())
        is_all_caps = text.isupper()
        has_numbers = any(char.isdigit() for char in text)
        
        if is_all_caps and 5 <= word_count <= 10:
            return "H1"
            
        if is_title_case and 3 <= word_count <= 8:
            if has_numbers:
                return "H2"
            else:
                return "H3"
        
        if text.endswith(':') and word_count <= 8:
            return "H3"
            
        return None
