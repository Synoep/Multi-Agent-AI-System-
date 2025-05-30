import os
import tempfile
from utils.logger import setup_logger

class PDFAgent:
    """
    Agent responsible for processing PDF content.
    """
    
    def __init__(self, memory_store):
        """
        Initialize the PDF agent.
        
        Args:
            memory_store: The shared memory store
        """
        self.memory = memory_store
        self.logger = setup_logger(name="pdf_agent")
    
    def process(self, pdf_content, intent):
        """
        Process PDF content.
        
        Args:
            pdf_content (bytes): The PDF content
            intent (str): The classified intent
            
        Returns:
            dict: Processing result with extracted information
        """
        self.logger.info(f"Processing PDF with intent: {intent}")
        
        try:
            # Create temporary file to store PDF content
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
                temp_pdf.write(pdf_content)
                temp_pdf_path = temp_pdf.name
            
            # Extract text content
            text_content = self._extract_text(temp_pdf_path)
            
            # Extract metadata
            metadata = self._extract_metadata(temp_pdf_path)
            
            # Process based on intent
            processed_content = self._process_by_intent(text_content, intent)
            
            # Clean up temporary file
            os.unlink(temp_pdf_path)
            
            result = {
                "metadata": metadata,
                "processed_content": processed_content,
                "content_type": "pdf"
            }
            
            self.logger.info("PDF processing completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing PDF: {str(e)}")
            return {
                "error": "Error processing PDF",
                "details": str(e)
            }
    
    def _extract_text(self, pdf_path):
        """
        Extract text content from PDF.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            str: Extracted text content
        """
        try:
            import fitz  # PyMuPDF
            
            text_content = ""
            doc = fitz.open(pdf_path)
            
            for page in doc:
                text_content += page.get_text()
            
            doc.close()
            return text_content
            
        except ImportError:
            self.logger.warning("PyMuPDF not available, falling back to basic text extraction")
            return self._basic_text_extraction(pdf_path)
    
    def _basic_text_extraction(self, pdf_path):
        """
        Basic text extraction from PDF using pdfplumber.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            str: Extracted text content
        """
        try:
            import pdfplumber
            
            text_content = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text_content += page.extract_text() or ""
            
            return text_content
            
        except ImportError:
            self.logger.error("No PDF extraction library available")
            return ""
    
    def _extract_metadata(self, pdf_path):
        """
        Extract metadata from PDF.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            dict: Extracted metadata
        """
        try:
            import fitz  # PyMuPDF
            
            doc = fitz.open(pdf_path)
            metadata = doc.metadata
            doc.close()
            
            return {
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "subject": metadata.get("subject", ""),
                "keywords": metadata.get("keywords", ""),
                "creator": metadata.get("creator", ""),
                "producer": metadata.get("producer", ""),
                "creation_date": metadata.get("creationDate", ""),
                "modification_date": metadata.get("modDate", "")
            }
            
        except ImportError:
            self.logger.warning("PyMuPDF not available, metadata extraction limited")
            return {}
    
    def _process_by_intent(self, text_content, intent):
        """
        Process text content based on intent.
        
        Args:
            text_content (str): The extracted text content
            intent (str): The classified intent
            
        Returns:
            dict: Processed content
        """
        import re
        
        processed = {
            "intent": intent,
            "extracted_data": {}
        }
        
        if intent == "invoice":
            # Extract invoice-specific information
            processed["extracted_data"].update(self._extract_invoice_data(text_content))
            
        elif intent == "regulation":
            # Extract regulation-specific information
            processed["extracted_data"].update(self._extract_regulation_data(text_content))
            
        elif intent == "rfq":
            # Extract RFQ-specific information
            processed["extracted_data"].update(self._extract_rfq_data(text_content))
        
        return processed
    
    def _extract_invoice_data(self, text_content):
        """
        Extract invoice-specific data from text content.
        
        Args:
            text_content (str): The text content
            
        Returns:
            dict: Extracted invoice data
        """
        import re
        
        invoice_data = {}
        
        # Extract invoice number
        invoice_match = re.search(r"Invoice\s*#?\s*([A-Z0-9-]+)", text_content, re.IGNORECASE)
        if invoice_match:
            invoice_data["invoice_number"] = invoice_match.group(1)
        
        # Extract date
        date_match = re.search(r"Date:\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})", text_content)
        if date_match:
            invoice_data["date"] = date_match.group(1)
        
        # Extract amount
        amount_match = re.search(r"Total:?\s*[\$€£]?\s*([\d,]+\.?\d*)", text_content)
        if amount_match:
            invoice_data["total_amount"] = amount_match.group(1)
        
        # Extract line items
        items = []
        item_matches = re.finditer(r"(\d+)\s*x\s*([^\n]+?)\s*[\$€£]?\s*([\d,]+\.?\d*)", text_content)
        for match in item_matches:
            items.append({
                "quantity": match.group(1),
                "description": match.group(2).strip(),
                "amount": match.group(3)
            })
        
        if items:
            invoice_data["items"] = items
        
        return invoice_data
    
    def _extract_regulation_data(self, text_content):
        """
        Extract regulation-specific data from text content.
        
        Args:
            text_content (str): The text content
            
        Returns:
            dict: Extracted regulation data
        """
        regulation_data = {}
        
        # Extract regulation number/ID
        reg_match = re.search(r"Regulation\s*(?:No\.?|Number|#)?\s*([A-Z0-9-]+)", text_content, re.IGNORECASE)
        if reg_match:
            regulation_data["regulation_id"] = reg_match.group(1)
        
        # Extract effective date
        date_match = re.search(r"Effective\s*Date:\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})", text_content, re.IGNORECASE)
        if date_match:
            regulation_data["effective_date"] = date_match.group(1)
        
        # Extract key requirements
        requirements = []
        req_matches = re.finditer(r"(?:^|\n)(?:•|\*|\d+\.)\s*([^\n]+)", text_content)
        for match in req_matches:
            requirements.append(match.group(1).strip())
        
        if requirements:
            regulation_data["requirements"] = requirements
        
        return regulation_data
    
    def _extract_rfq_data(self, text_content):
        """
        Extract RFQ-specific data from text content.
        
        Args:
            text_content (str): The text content
            
        Returns:
            dict: Extracted RFQ data
        """
        rfq_data = {}
        
        # Extract RFQ number
        rfq_match = re.search(r"RFQ\s*(?:No\.?|Number|#)?\s*([A-Z0-9-]+)", text_content, re.IGNORECASE)
        if rfq_match:
            rfq_data["rfq_number"] = rfq_match.group(1)
        
        # Extract submission deadline
        deadline_match = re.search(r"(?:Submission|Due)\s*(?:Date|Deadline):\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})", text_content, re.IGNORECASE)
        if deadline_match:
            rfq_data["submission_deadline"] = deadline_match.group(1)
        
        # Extract requested items
        items = []
        item_matches = re.finditer(r"(?:^|\n)(?:•|\*|\d+\.)\s*(\d+)\s*(?:units?|pcs?|pieces?)?\s*(?:of)?\s*([^\n]+)", text_content)
        for match in item_matches:
            items.append({
                "quantity": match.group(1),
                "description": match.group(2).strip()
            })
        
        if items:
            rfq_data["requested_items"] = items
        
        return rfq_data