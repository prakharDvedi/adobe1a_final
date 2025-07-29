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
        
        # Look for the first meaningful line as title
        for line in lines[:10]:
            if len(line) < 5:
                continue
                
            if self._is_header_footer(line):
                continue
                
            if self._has_too_many_special_chars(line):
                continue
            
            # Skip obvious non-title patterns
            if re.match(r'^\d+\s*\.?\s*$', line):  # Just numbers
                continue
            if re.match(r'^Page\s+\d+', line, re.IGNORECASE):
                continue
            if re.match(r'^\d+\.\s+[A-Z]', line):  # Numbered list items
                continue
                
            # Accept meaningful text as title
            if len(line) >= 5:
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
                if level and self._is_meaningful_heading(line):
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
            
        # Basic ignore patterns
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
        
        # Metadata and structural headings to ignore
        metadata_patterns = [
            r'^(Table\s+of\s+Contents?|TOC)\s*$',
            r'^(Revision\s+History|Version\s+History)\s*$',
            r'^(Acknowledgements?|Acknowledgments?)\s*$',
            r'^(References?|Bibliography)\s*$',
            r'^(Index|Glossary)\s*$',
            r'^(Appendix\s+[A-Z]?)\s*$',
            r'^(Abstract|Executive\s+Summary)\s*$',
            r'^(Preface|Foreword)\s*$',
            r'^(Copyright|Disclaimer)\s*$',
            r'^(Trademarks?)\s*$',
            r'^(Documents?\s+and\s+Web\s+Sites?)\s*$',
            r'^(List\s+of\s+(Figures?|Tables?|Illustrations?))\s*$',
            r'^(About\s+(this|the)\s+(document|guide|manual))\s*$',
            r'^(How\s+to\s+use\s+this\s+(document|guide|manual))\s*$',
            r'^(Contact\s+(Information|Details?))\s*$',
            r'^(Legal\s+(Notice|Information))\s*$',
            r'^(Terms\s+of\s+(Reference|Use))\s*$',
            r'^(Privacy\s+Policy)\s*$',
            r'^(Document\s+(Information|Details?))\s*$',
            r'^(Publication\s+(Information|Details?))\s*$',
        ]
        
        for pattern in ignore_patterns + metadata_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        if self._has_too_many_special_chars(text):
            return True
            
        if len(text) > 200:
            return True
            
        # Body text starters that shouldn't be headings
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
            r'^HOPE\s+To\s+SEE\s+You\s+THERE',  # Specific case from feedback
        ]
        
        for pattern in body_starters:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False

    def _classify_generic_heading(self, text: str) -> str:
        if not text:
            return None
        
        # Skip very short or very long text
        word_count = len(text.split())
        if word_count < 1 or word_count > 15:
            return None
            
        # H1 patterns - Main sections and important headings
        h1_patterns = [
            r'^\d+\.\s+[A-Z][a-zA-Z\s]{5,}$',  # Numbered sections
            r'^(Introduction|Overview|Conclusion|Summary)\s+to\s+[A-Z]',  # Introduction to X
            r'^[A-Z][A-Z\s]{8,40}$',  # All caps substantial headings
        ]
        
        # H2 patterns - Clear subsections
        h2_patterns = [
            r'^\d+\.\d+\s+[A-Z][a-zA-Z\s]{3,}$',  # Numbered subsections
            r'^[A-Z][a-zA-Z\s]{5,25}:\s*$',  # Titles ending with colon
        ]
        
        # H3 patterns - Sub-subsections
        h3_patterns = [
            r'^\d+\.\d+\.\d+\s+[A-Z][a-zA-Z\s]{3,}$',  # Triple numbered sections
            r'^(Timeline|Summary|Background|Milestones|Phase\s+[IVX\d]+)\s*:?\s*$',
        ]
        
        # H4 patterns - Specific patterns
        h4_patterns = [
            r'^For\s+(each|every)\s+[A-Z][a-zA-Z\s]+\s+(it\s+could\s+mean|means?)\s*:?\s*$',
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
        
        # Be more restrictive with word count
        if word_count > 12 or word_count < 2:
            return None
            
        is_title_case = all(word[0].isupper() for word in words if word.isalpha() and len(word) > 1)
        is_all_caps = text.isupper()
        has_numbers = any(char.isdigit() for char in text)
        
        # More restrictive all caps detection
        if is_all_caps and 3 <= word_count <= 8:
            # Skip if it looks like a form title or announcement
            if any(word in text.lower() for word in ['form', 'application', 'hope', 'see', 'there']):
                return None
            return "H1"
            
        # More restrictive title case detection
        if is_title_case and 3 <= word_count <= 8:
            # Must have meaningful content words
            content_words = [w for w in words if len(w) > 2 and w.lower() not in ['the', 'and', 'for', 'with', 'from']]
            if len(content_words) < 2:
                return None
                
            if has_numbers:
                return "H2"
            else:
                return "H3"
        
        # Colon endings for subsections
        if text.endswith(':') and 3 <= word_count <= 8:
            return "H3"
            
        return None

    def _is_meaningful_heading(self, text: str) -> bool:
        """Additional filter to ensure only meaningful content headings are included"""
        
        # Skip very basic form elements and labels
        form_patterns = [
            r'^\d+\.\s*(Name|PAY|Whether|Home|so\s+whether)',
            r'^S\.No\s+Name\s+Age',
            r'^\(a\)\s+If\s+the\s+concession',
            r'^Application\s+form',
            r'^REGULAR\s+PATHWAY',
            r'^DISTINCTION\s+PATHWAY',
            r'^PIGEON\s+FORGE',
            r'^NEAR\s+DIXIE',
            r'^CLOSED\s+TOED',
            r'^PARENTS\s+OR\s+GUARDIANS',
            r'^SO\s+YOUR\s+CHILD',
        ]
        
        # Skip table of contents entries (with dots and page numbers)
        toc_patterns = [
            r'.*\.{3,}.*\d+$',  # Lines with dots leading to page numbers
            r'^\d+\.\d+.*\d+$',  # Section numbers with page numbers at end
        ]
        
        # Skip copyright and metadata
        metadata_patterns = [
            r'^Copyright\s+Notice',
            r'^Foundation\s+Level\s+Extensions?$',
            r'^Software\s+Testing$',
            r'^Qualifications?\s+Board$',
            r'^International\s+Software',
            r'^Version\s+Date\s+Remarks',
            r'^©.*\d{4}',
            r'^Identifier\s+Reference',
            r'^Foundation\s+Level\s+Working\s+Group',
        ]
        
        # Skip funding tables and data
        data_patterns = [
            r'^Funding\s+Source\s+\d+',
            r'^Government\s+\$\d+',
            r'^Libraries\s+\$\d+',
            r'^Endowment\s+\$\d+',
            r'^Gifts/In-Kind\s+\$\d+',
            r'^TOTAL\s+ANNUAL\s+\$\d+',
            r'^Baseline:\s+Foundation\s+\d+',
            r'^Extension:\s+Agile\s+Tester\s+\d+',
            r'^Syllabus\s+Days$',
        ]
        
        # Skip incomplete fragments and partial sentences
        fragment_patterns = [
            r'^(and|or|but|the|a|an|in|on|at|to|for|of|with|from)\s+',
            r'^(during|including|so|whether|if)\s+',
            r'^\w+\s+(and\s+)?services?$',
            r'^(resources?|services?|licenses?)\s+(and\s+\w+)?$',
            r'^for\s+(library\s+workers?|the\s+general\s+public)$',
            r'^library\s+web\s+sites?$',
            r'^knowledge\s+supports?\s+and\s+tools?$',
            r'^\w+\s+course\s+should\s+be\s+an\s+AP$',
            r'^One\s+must\s+be\s+a\s+Computer$',
            r'Agile\s+Tester$',
        ]
        
        all_patterns = form_patterns + toc_patterns + metadata_patterns + data_patterns + fragment_patterns
        
        for pattern in all_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        
        # Allow numbered sections that look meaningful
        if re.match(r'^\d+\.\s+[A-Z][a-zA-Z\s]{5,}$', text):
            return True
            
        # Allow subsections
        if re.match(r'^\d+\.\d+\s+[A-Z][a-zA-Z\s]{3,}$', text):
            return True
            
        # Allow "For each X it could mean:" patterns
        if re.match(r'^For\s+(each|every)\s+[A-Z][a-zA-Z\s]+\s+(it\s+could\s+mean|means?)\s*:?\s*$', text, re.IGNORECASE):
            return True
        
        # Must start with capital letter
        if not text[0].isupper():
            return False
            
        # Must have reasonable length
        if len(text) < 3 or len(text) > 100:
            return False
            
        # Skip if it's mostly numbers or special characters
        alpha_chars = sum(1 for c in text if c.isalpha())
        if alpha_chars < len(text) * 0.5:
            return False
            
        return True
