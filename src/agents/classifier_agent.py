import json
import re
from utils.logger import setup_logger

class ClassifierAgent:
    """
    Agent responsible for classifying input data format and intent.
    """
    
    def __init__(self, memory_store):
        """
        Initialize the classifier agent.
        
        Args:
            memory_store: The shared memory store
        """
        self.memory = memory_store
        self.logger = setup_logger(name="classifier_agent")
        
    def classify(self, input_data):
        """
        Classify the input data format and intent.
        
        Args:
            input_data (str): The input data to classify
            
        Returns:
            dict: Classification result with format and intent
        """
        self.logger.info("Classifying input data")
        
        # Determine format
        format_type = self._determine_format(input_data)
        
        # Determine intent based on format and content
        intent = self._determine_intent(input_data, format_type)
        
        result = {
            "format": format_type,
            "intent": intent
        }
        
        self.logger.info(f"Classification result: {result}")
        return result
    
    def _determine_format(self, input_data):
        """
        Determine the format of the input data.
        
        Args:
            input_data (str): The input data
            
        Returns:
            str: The determined format (json, email, pdf, or unknown)
        """
        # Check if it's JSON
        try:
            # Try to parse as JSON
            json.loads(input_data)
            return "json"
        except (json.JSONDecodeError, TypeError):
            pass
        
        # Check if it's an email
        email_patterns = [
            r"From:\s+.*@.*\..+",
            r"To:\s+.*@.*\..+",
            r"Subject:",
            r".*@.*\..+\s+wrote:"
        ]
        
        email_indicators = sum(1 for pattern in email_patterns if re.search(pattern, input_data, re.IGNORECASE))
        if email_indicators >= 2:  # If at least 2 email patterns match
            return "email"
        
        # In a real system, we would check for PDF here
        # For now, we'll just use a placeholder
        if input_data.startswith("%PDF-"):
            return "pdf"
        
        # Default to unknown
        return "unknown"
    
    def _determine_intent(self, input_data, format_type):
        """
        Determine the intent of the input data.
        
        Args:
            input_data (str): The input data
            format_type (str): The format of the input data
            
        Returns:
            str: The determined intent
        """
        # Intent keywords
        intent_keywords = {
            "invoice": ["invoice", "payment", "bill", "amount due", "paid", "charge"],
            "rfq": ["quote", "quotation", "rfq", "request for quote", "pricing"],
            "complaint": ["complaint", "issue", "problem", "dissatisfied", "unhappy", "disappointed"],
            "regulation": ["regulation", "compliance", "law", "legal", "requirement", "standard"]
        }
        
        # Count occurrences of intent keywords
        intent_scores = {intent: 0 for intent in intent_keywords}
        
        for intent, keywords in intent_keywords.items():
            for keyword in keywords:
                intent_scores[intent] += len(re.findall(r'\b' + keyword + r'\b', input_data, re.IGNORECASE))
        
        # Get the intent with the highest score
        max_score = max(intent_scores.values())
        if max_score > 0:
            # Get all intents with the max score
            max_intents = [intent for intent, score in intent_scores.items() if score == max_score]
            return max_intents[0]  # Return the first one if there are ties
        
        # Default intents based on format if no keywords matched
        format_default_intents = {
            "json": "data_exchange",
            "email": "inquiry",
            "pdf": "document"
        }
        
        return format_default_intents.get(format_type, "unknown")