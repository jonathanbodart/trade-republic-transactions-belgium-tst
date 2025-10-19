import pdfplumber
from typing import BinaryIO
import logging

logger = logging.getLogger(__name__)


class PDFParser:
    """Extracts text content from PDF files"""

    @staticmethod
    def extract_text(pdf_file: BinaryIO) -> str:
        """
        Extract all text from a PDF file

        Args:
            pdf_file: Binary file object of the PDF

        Returns:
            Extracted text content
        """
        try:
            text_content = []

            with pdfplumber.open(pdf_file) as pdf:
                logger.info(f"Processing PDF with {len(pdf.pages)} pages")

                for page_num, page in enumerate(pdf.pages, 1):
                    logger.debug(f"Extracting text from page {page_num}")
                    page_text = page.extract_text()

                    if page_text:
                        text_content.append(f"--- Page {page_num} ---\n{page_text}")

            full_text = "\n\n".join(text_content)
            logger.info(f"Extracted {len(full_text)} characters from PDF")

            return full_text

        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise

    @staticmethod
    def extract_tables(pdf_file: BinaryIO) -> list[list[list]]:
        """
        Extract tables from PDF if structured data is available

        Args:
            pdf_file: Binary file object of the PDF

        Returns:
            List of tables (each table is a list of rows)
        """
        try:
            all_tables = []

            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    if tables:
                        all_tables.extend(tables)

            logger.info(f"Extracted {len(all_tables)} tables from PDF")
            return all_tables

        except Exception as e:
            logger.error(f"Error extracting tables from PDF: {e}")
            return []
