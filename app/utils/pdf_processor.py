"""
PDF processing utilities for extracting text from PDF files.
"""
import logging
from pathlib import Path
from typing import Optional

try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)


class PDFProcessor:
    """
    Extract text from PDF files.
    Handles multi-page PDFs and error recovery.
    """
    
    @staticmethod
    def extract_text(file_path: Path) -> str:
        """
        Extract all text from a PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text from all pages
            
        Raises:
            ValueError: If PDF cannot be read
        """
        try:
            reader = PdfReader(str(file_path))
            
            if len(reader.pages) == 0:
                raise ValueError("PDF has no pages")
            
            # Extract text from all pages
            text_parts = []
            for page_num, page in enumerate(reader.pages):
                try:
                    text = page.extract_text()
                    if text.strip():
                        text_parts.append(text)
                except Exception as e:
                    logger.warning(f"Failed to extract page {page_num}: {e}")
                    continue
            
            if not text_parts:
                raise ValueError("No text could be extracted from PDF")
            
            full_text = "\n\n".join(text_parts)
            
            logger.info(
                f"Extracted {len(full_text)} characters from "
                f"{len(reader.pages)} pages"
            )
            
            return full_text
            
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            raise ValueError(f"Failed to process PDF: {e}")
    
    @staticmethod
    def extract_text_from_bytes(pdf_bytes: bytes) -> str:
        """
        Extract text from PDF bytes (for uploaded files).
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            Extracted text
        """
        import io
        
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            reader = PdfReader(pdf_file)
            
            text_parts = []
            for page in reader.pages:
                try:
                    text = page.extract_text()
                    if text.strip():
                        text_parts.append(text)
                except Exception as e:
                    logger.warning(f"Failed to extract page: {e}")
                    continue
            
            if not text_parts:
                raise ValueError("No text could be extracted from PDF")
            
            return "\n\n".join(text_parts)
            
        except Exception as e:
            logger.error(f"PDF extraction from bytes failed: {e}")
            raise ValueError(f"Failed to process PDF: {e}")


# Global instance
pdf_processor = PDFProcessor()
