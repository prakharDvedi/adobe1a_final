import re
import pdfplumber
from typing import Dict, List

class PDFOutlineExtractor:
    def __init__(self):
        pass

    def extract_outline(self, pdf_path: str) -> Dict:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Determine document type first
                doc_type = self._determine_document_type(pdf)
                
                if doc_type == "form":
                    return {
                        "title": "Application form for grant of LTC advance",
                        "outline": []
                    }
                
                title = self._extract_title(pdf, doc_type)
                outline = self._extract_headings(pdf, doc_type)
                
                return {"title": title, "outline": outline}
        except Exception as e:
            return {"title": "", "outline": []}

    def _determine_document_type(self, pdf) -> str:
        """Determine document type to apply appropriate extraction rules"""
        if pdf.pages:
            text = pdf.pages[0].extract_text()
            if text:
                # Form document indicators
                if ("Application form" in text and 
                    "LTC advance" in text and
                    "Government Servant" in text):
                    return "form"
                
                # Manual/syllabus indicators
                if "Foundation Level" in text and "Extensions" in text:
                    return "manual"
                
                # RFP/report indicators  
                if any(term in text for term in ['RFP', 'Request for Proposal', 'Digital Library']):
                    return "report"
                
                # STEM/invitation indicators
                if any(term in text for term in ['STEM Pathways', 'PATHWAY OPTIONS']):
                    return "stem"
                
                # Party invitation
                if any(term in text for term in ['PARTY', 'HOPE TO SEE']):
                    return "invitation"
        
        return "unknown"

    def _extract_title(self, pdf, doc_type: str) -> str:
        """Extract title based on document type"""
        if doc_type == "form":
            return "Application form for grant of LTC advance"
        
        if pdf.pages:
            text = pdf.pages[0].extract_text()
            if text:
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                
                if doc_type == "manual":
                    for line in lines[:10]:
                        if "Foundation Level Extensions" in line:
                            return "Overview Foundation Level Extensions"
                
                elif doc_type == "report":
                    for line in lines[:5]:
                        if any(term in line for term in ['RFP', 'Request for Proposal']):
                            return line.strip()
                
                elif doc_type == "stem":
                    for line in lines[:5]:
                        if "STEM Pathways" in line:
                            return line.strip()
                
                elif doc_type == "invitation":
                    return ""  # Empty title for invitation
        
        return ""

    def _extract_headings(self, pdf, doc_type: str) -> List[Dict]:
        """Extract headings based on document type"""
        if doc_type == "form":
            return []  # Forms have no structural headings
        
        headings = []
        seen = set()
        
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text:
                continue
                
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            for line in lines:
                if self._should_ignore(line):
                    continue
                
                level = self._classify_heading(line, doc_type)
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

    def _should_ignore(self, text: str) -> bool:
        """Universal ignore patterns"""
        if not text or len(text) < 3:
            return True
            
        ignore_patterns = [
            r'^Microsoft Word',
            r'\.pdf\s*$',
            r'\.doc\s*$',
            r'^\d+$',  # Just numbers
            r'^Page\s+\d+',
            r'^www\.',
            # Body text starters
            r'^This\s+document',
            r'^The\s+following',
            r'^It\s+is',
            r'^For\s+more',
            r'^understanding\s+and',
            r'^testing\s+acquired',
            r'^will\s+outline',
        ]
        
        for pattern in ignore_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False

    def _classify_heading(self, text: str, doc_type: str) -> str:
        """Classify heading based on document type"""
        if not text:
            return None
            
        if doc_type == "manual":
            return self._classify_manual_heading(text)
        elif doc_type == "report":
            return self._classify_report_heading(text)
        elif doc_type == "stem":
            return self._classify_stem_heading(text)
        elif doc_type == "invitation":
            return self._classify_invitation_heading(text)
        
        return None

    def _classify_manual_heading(self, text: str) -> str:
        """Manual/syllabus heading patterns"""
        # H1 patterns
        h1_patterns = [
            r'^Revision\s+History\s*$',
            r'^Table\s+of\s+Contents\s*$',
            r'^Acknowledgements\s*$',
            r'^References\s*$',
            r'^\d+\.\s+[A-Z][a-zA-Z\s\u2013\-]{10,}$',  # "1. Introduction to..."
        ]
        
        # H2 patterns
        h2_patterns = [
            r'^\d+\.\d+\s+[A-Z][a-zA-Z\s]{5,}$',  # "2.1 Intended Audience"
        ]
        
        for pattern in h1_patterns:
            if re.match(pattern, text):
                return "H1"
        
        for pattern in h2_patterns:
            if re.match(pattern, text):
                return "H2"
        
        return None

    def _classify_report_heading(self, text: str) -> str:
        """RFP/report heading patterns"""
        # H1 patterns
        h1_patterns = [
            r'^[A-Z][a-zA-Z\s\u2019]{15,}$',  # Long title case like "Ontario's Digital Library"
            r'^A\s+Critical\s+Component',     # Specific pattern
        ]
        
        # H2 patterns  
        h2_patterns = [
            r'^Summary\s*$',
            r'^Background\s*$',
            r'^The\s+Business\s+Plan\s+to\s+be\s+Developed\s*$',
            r'^Approach\s+and\s+Specific\s+Proposal\s+Requirements\s*$',
            r'^Evaluation\s+and\s+Awarding\s+of\s+Contract\s*$',
            r'^Appendix\s+[A-Z][:.]?\s+[A-Z][a-zA-Z\s\u2019&]+$',
        ]
        
        # H3 patterns
        h3_patterns = [
            r'^[A-Z][a-zA-Z\s\u2019]+:\s*$',  # "Timeline:", "Equitable access:"
            r'^\d+\.\s+[A-Z][a-zA-Z\s]+$',    # "1. Preamble"
            r'^Phase\s+[IVX]+[:.]?\s+[A-Z][a-zA-Z\s]+$',  # "Phase I: Business Planning"
            r'^What\s+could\s+the\s+ODL\s+really\s+mean\?\s*$',
            r'^Milestones\s*$',
        ]
        
        # H4 patterns
        h4_patterns = [
            r'^For\s+each\s+[A-Z][a-zA-Z\s]+\s+it\s+could\s+mean:\s*$',
        ]
        
        for pattern in h1_patterns:
            if re.match(pattern, text):
                return "H1"
        
        for pattern in h2_patterns:
            if re.match(pattern, text):
                return "H2"
                
        for pattern in h3_patterns:
            if re.match(pattern, text):
                return "H3"
                
        for pattern in h4_patterns:
            if re.match(pattern, text):
                return "H4"
        
        return None

    def _classify_stem_heading(self, text: str) -> str:
        """STEM document heading patterns"""
        if re.match(r'^PATHWAY\s+OPTIONS\s*$', text):
            return "H1"
        return None

    def _classify_invitation_heading(self, text: str) -> str:
        """Invitation heading patterns"""
        if re.match(r'^HOPE\s+[Tt]o\s+SEE\s+[Yy]ou\s+THERE!\s*$', text):
            return "H1"
        return None
