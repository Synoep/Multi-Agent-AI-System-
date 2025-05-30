import re
from utils.logger import setup_logger

class EmailAgent:
    """
    Agent responsible for processing email content.
    """
    
    def __init__(self, memory_store):
        """
        Initialize the email agent.
        
        Args:
            memory_store: The shared memory store
        """
        self.memory = memory_store
        self.logger = setup_logger(name="email_agent")
    
    def process(self, email_content, intent):
        """
        Process email content.
        
        Args:
            email_content (str): The email content
            intent (str): The classified intent
            
        Returns:
            dict: Processing result with extracted information
        """
        self.logger.info(f"Processing email with intent: {intent}")
        
        try:
            # Extract email metadata
            metadata = self._extract_metadata(email_content)
            
            # Extract content sections
            sections = self._extract_sections(email_content)
            
            # Determine urgency
            urgency = self._determine_urgency(email_content, intent)
            
            # Extract entities based on intent
            entities = self._extract_entities(email_content, intent)
            
            # Format for CRM-style usage
            crm_format = self._format_for_crm(metadata, sections, urgency, entities, intent)
            
            result = {
                "metadata": metadata,
                "urgency": urgency,
                "entities": entities,
                "crm_format": crm_format
            }
            
            self.logger.info("Email processing completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing email: {str(e)}")
            return {
                "error": "Error processing email",
                "details": str(e)
            }
    
    def _extract_metadata(self, email_content):
        """
        Extract metadata from email content.
        
        Args:
            email_content (str): The email content
            
        Returns:
            dict: Extracted metadata
        """
        metadata = {}
        
        # Extract sender
        sender_match = re.search(r"From:\s+([^<\n]+)(?:<([^>]+)>)?", email_content)
        if sender_match:
            sender_name = sender_match.group(1).strip()
            sender_email = sender_match.group(2) if sender_match.group(2) else sender_match.group(1).strip()
            metadata["sender_name"] = sender_name
            metadata["sender_email"] = sender_email
        
        # Extract recipient
        recipient_match = re.search(r"To:\s+([^<\n]+)(?:<([^>]+)>)?", email_content)
        if recipient_match:
            recipient_name = recipient_match.group(1).strip()
            recipient_email = recipient_match.group(2) if recipient_match.group(2) else recipient_match.group(1).strip()
            metadata["recipient_name"] = recipient_name
            metadata["recipient_email"] = recipient_email
        
        # Extract subject
        subject_match = re.search(r"Subject:\s+(.+)(?:\n|$)", email_content)
        if subject_match:
            metadata["subject"] = subject_match.group(1).strip()
        
        # Extract date
        date_match = re.search(r"Date:\s+(.+)(?:\n|$)", email_content)
        if date_match:
            metadata["date"] = date_match.group(1).strip()
        
        return metadata
    
    def _extract_sections(self, email_content):
        """
        Extract content sections from email.
        
        Args:
            email_content (str): The email content
            
        Returns:
            dict: Extracted sections
        """
        # Remove headers to get the body
        body_pattern = r"(?:From:.+\n)(?:To:.+\n)?(?:Subject:.+\n)(?:Date:.+\n)?(.*)"
        body_match = re.search(body_pattern, email_content, re.DOTALL)
        
        body = body_match.group(1).strip() if body_match else email_content
        
        # Split into greeting, main content, and signature
        sections = {}
        
        # Extract greeting
        greeting_pattern = r"^((?:Dear|Hello|Hi|Good morning|Good afternoon|Good evening)[^,\n]*,?)"
        greeting_match = re.search(greeting_pattern, body, re.IGNORECASE | re.MULTILINE)
        if greeting_match:
            sections["greeting"] = greeting_match.group(1).strip()
            body = body[len(greeting_match.group(0)):].strip()
        
        # Extract signature
        signature_patterns = [
            r"(?:Regards|Sincerely|Best regards|Thanks|Thank you|Cheers),?\s*\n+(.*?)$",
            r"--\s*\n+(.*?)$"
        ]
        
        for pattern in signature_patterns:
            signature_match = re.search(pattern, body, re.IGNORECASE | re.DOTALL)
            if signature_match:
                sections["signature"] = signature_match.group(1).strip()
                body = body[:body.rfind(signature_match.group(0))].strip()
                break
        
        # Remaining content is the main body
        sections["body"] = body.strip()
        
        return sections
    
    def _determine_urgency(self, email_content, intent):
        """
        Determine the urgency of the email.
        
        Args:
            email_content (str): The email content
            intent (str): The classified intent
            
        Returns:
            str: Urgency level (high, medium, low)
        """
        # Urgency indicators
        urgency_indicators = {
            "high": ["urgent", "asap", "immediately", "critical", "emergency", "deadline", "important", "priority"],
            "medium": ["soon", "timely", "prompt", "attention", "please respond", "by tomorrow", "by next week"],
            "low": ["when you can", "at your convenience", "no rush", "fyi", "for your reference"]
        }
        
        # Count urgency indicators
        urgency_scores = {"high": 0, "medium": 0, "low": 0}
        
        for level, indicators in urgency_indicators.items():
            for indicator in indicators:
                urgency_scores[level] += len(re.findall(r'\b' + indicator + r'\b', email_content, re.IGNORECASE))
        
        # Intent-based urgency modifier
        if intent == "complaint":
            urgency_scores["high"] += 1
        elif intent == "rfq":
            urgency_scores["medium"] += 1
        
        # Determine urgency level
        if urgency_scores["high"] > 0:
            return "high"
        elif urgency_scores["medium"] > 0:
            return "medium"
        else:
            return "low"
    
    def _extract_entities(self, email_content, intent):
        """
        Extract entities based on intent.
        
        Args:
            email_content (str): The email content
            intent (str): The classified intent
            
        Returns:
            dict: Extracted entities
        """
        entities = {}
        
        # Extract common entities
        
        # Extract names
        name_pattern = r"(?:(?:my|I am|name is|this is)\s+)([A-Z][a-z]+(?: [A-Z][a-z]+)*)"
        name_match = re.search(name_pattern, email_content)
        if name_match:
            entities["person_name"] = name_match.group(1)
        
        # Extract company names
        company_pattern = r"(?:(?:from|at|with|company)\s+)([A-Z][a-zA-Z0-9\s&]+(?:Inc|LLC|Ltd|Corp|Corporation|Company)?)"
        company_match = re.search(company_pattern, email_content)
        if company_match:
            entities["company"] = company_match.group(1).strip()
        
        # Extract phone numbers
        phone_pattern = r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
        phone_match = re.search(phone_pattern, email_content)
        if phone_match:
            entities["phone"] = phone_match.group(0)
        
        # Intent-specific extraction
        if intent == "rfq":
            # Extract product mentions
            products = re.findall(r"(\d+)\s+(?:units of|pieces of|)?\s*([a-zA-Z0-9\s\-]+?)(?:\.|\n|,|\s+for|\s+at|\s+with)", email_content)
            if products:
                entities["products"] = [{"quantity": p[0], "name": p[1].strip()} for p in products]
            
            # Extract timeframe
            timeframe_pattern = r"(?:within|by|before)\s+(?:the\s+)?(?:next|coming)?\s*(\d+\s+(?:days?|weeks?|months?)|[a-zA-Z]+day|[a-zA-Z]+\s+\d+(?:st|nd|rd|th)?)"
            timeframe_match = re.search(timeframe_pattern, email_content, re.IGNORECASE)
            if timeframe_match:
                entities["timeframe"] = timeframe_match.group(1)
        
        elif intent == "complaint":
            # Extract issue description
            issue_pattern = r"(?:issue|problem|complaint|error|mistake|defective|broken|damaged|faulty)\s+(?:with|about|regarding)?\s+([^.!?\n]+)"
            issue_match = re.search(issue_pattern, email_content, re.IGNORECASE)
            if issue_match:
                entities["issue"] = issue_match.group(1).strip()
            
            # Extract order reference
            order_pattern = r"(?:order|invoice|transaction|reference)\s+(?:number|#|id|code)?\s*[:#]?\s*([a-zA-Z0-9\-]+)"
            order_match = re.search(order_pattern, email_content, re.IGNORECASE)
            if order_match:
                entities["order_reference"] = order_match.group(1).strip()
        
        return entities
    
    def _format_for_crm(self, metadata, sections, urgency, entities, intent):
        """
        Format extracted information for CRM-style usage.
        
        Args:
            metadata (dict): Email metadata
            sections (dict): Email content sections
            urgency (str): Determined urgency
            entities (dict): Extracted entities
            intent (str): Classified intent
            
        Returns:
            dict: Formatted information for CRM
        """
        crm_format = {
            "contact": {
                "name": metadata.get("sender_name", "Unknown"),
                "email": metadata.get("sender_email", "Unknown"),
                "company": entities.get("company", "Unknown"),
                "phone": entities.get("phone", "Unknown")
            },
            "interaction": {
                "type": "email",
                "direction": "inbound",
                "date": metadata.get("date", "Unknown"),
                "subject": metadata.get("subject", "Unknown"),
                "intent": intent,
                "urgency": urgency
            },
            "content_summary": sections.get("body", "")[:100] + "..." if len(sections.get("body", "")) > 100 else sections.get("body", ""),
            "next_steps": self._suggest_next_steps(intent, urgency)
        }
        
        # Add intent-specific fields
        if intent == "rfq":
            crm_format["rfq_details"] = {
                "products": entities.get("products", []),
                "timeframe": entities.get("timeframe", "Not specified")
            }
        elif intent == "complaint":
            crm_format["complaint_details"] = {
                "issue": entities.get("issue", "Not specified"),
                "order_reference": entities.get("order_reference", "Not specified")
            }
        
        return crm_format
    
    def _suggest_next_steps(self, intent, urgency):
        """
        Suggest next steps based on intent and urgency.
        
        Args:
            intent (str): The classified intent
            urgency (str): The determined urgency
            
        Returns:
            list: Suggested next steps
        """
        next_steps = []
        
        if intent == "rfq":
            next_steps.append("Prepare quotation for requested items")
            if urgency == "high":
                next_steps.append("Contact customer within 4 business hours")
            elif urgency == "medium":
                next_steps.append("Contact customer within 1 business day")
            else:
                next_steps.append("Contact customer within 2 business days")
        
        elif intent == "complaint":
            next_steps.append("Investigate the reported issue")
            if urgency == "high":
                next_steps.append("Contact customer within 2 business hours")
                next_steps.append("Escalate to support manager")
            elif urgency == "medium":
                next_steps.append("Contact customer within 8 business hours")
            else:
                next_steps.append("Contact customer within 1 business day")
        
        elif intent == "inquiry":
            if urgency == "high":
                next_steps.append("Respond within 1 business day")
            else:
                next_steps.append("Respond within 2 business days")
        
        return next_steps