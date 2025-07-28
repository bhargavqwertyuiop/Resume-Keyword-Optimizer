import os
import re
from typing import Optional
from pathlib import Path

# Document processing
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

class FileProcessor:
    """Handles reading and processing various file formats for resumes"""
    
    @staticmethod
    def extract_text_from_file(file_path: str) -> Optional[str]:
        """Extract text from various file formats"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.txt':
            return FileProcessor._read_txt(file_path)
        elif file_extension == '.pdf':
            return FileProcessor._read_pdf(file_path)
        elif file_extension in ['.docx', '.doc']:
            return FileProcessor._read_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    @staticmethod
    def _read_txt(file_path: str) -> str:
        """Read text from a plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
    
    @staticmethod
    def _read_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        if not PDF_AVAILABLE:
            raise ImportError("PyPDF2 is required to read PDF files. Install with: pip install PyPDF2")
        
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise ValueError(f"Error reading PDF file: {str(e)}")
    
    @staticmethod
    def _read_docx(file_path: str) -> str:
        """Extract text from DOCX file"""
        if not DOCX_AVAILABLE:
            raise ImportError("python-docx is required to read DOCX files. Install with: pip install python-docx")
        
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise ValueError(f"Error reading DOCX file: {str(e)}")
    
    @staticmethod
    def clean_extracted_text(text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Remove page numbers and headers/footers (common patterns)
        text = re.sub(r'Page \d+ of \d+', '', text)
        text = re.sub(r'^\d+$', '', text, flags=re.MULTILINE)
        
        # Remove email headers if present
        text = re.sub(r'From:.*?Subject:.*?\n', '', text, flags=re.DOTALL)
        
        return text.strip()
    
    @staticmethod
    def validate_resume_content(text: str) -> bool:
        """Basic validation to check if content looks like a resume"""
        text_lower = text.lower()
        
        # Check for common resume sections
        resume_indicators = [
            'experience', 'education', 'skills', 'work', 'employment',
            'university', 'college', 'degree', 'certification', 'resume',
            'cv', 'curriculum vitae'
        ]
        
        indicator_count = sum(1 for indicator in resume_indicators if indicator in text_lower)
        
        # Check minimum length and indicator presence
        if len(text.split()) < 50:  # Too short to be a resume
            return False
        
        if indicator_count < 2:  # Should have at least 2 resume indicators
            return False
        
        return True
    
    @staticmethod
    def extract_contact_info(text: str) -> dict:
        """Extract contact information from resume text"""
        contact_info = {
            'email': None,
            'phone': None,
            'linkedin': None,
            'github': None
        }
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info['email'] = email_match.group()
        
        # Phone pattern (various formats)
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # 123-456-7890 or 123.456.7890
            r'\(\d{3}\)\s*\d{3}[-.]?\d{4}\b',  # (123) 456-7890
            r'\b\d{10}\b'  # 1234567890
        ]
        
        for pattern in phone_patterns:
            phone_match = re.search(pattern, text)
            if phone_match:
                contact_info['phone'] = phone_match.group()
                break
        
        # LinkedIn profile
        linkedin_pattern = r'linkedin\.com/in/[\w\-]+'
        linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_match:
            contact_info['linkedin'] = linkedin_match.group()
        
        # GitHub profile
        github_pattern = r'github\.com/[\w\-]+'
        github_match = re.search(github_pattern, text, re.IGNORECASE)
        if github_match:
            contact_info['github'] = github_match.group()
        
        return contact_info