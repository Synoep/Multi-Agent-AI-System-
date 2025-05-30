import json
from utils.logger import setup_logger

class JSONAgent:
    """
    Agent responsible for processing JSON data.
    """
    
    def __init__(self, memory_store):
        """
        Initialize the JSON agent.
        
        Args:
            memory_store: The shared memory store
        """
        self.memory = memory_store
        self.logger = setup_logger(name="json_agent")
        
        # Define target schemas for different intents
        self.schemas = {
            "invoice": {
                "required": ["customer", "invoice_number", "total"],
                "optional": ["items", "date", "due_date", "payment_terms"]
            },
            "rfq": {
                "required": ["customer", "items"],
                "optional": ["deadline", "delivery_address", "contact_person"]
            },
            "data_exchange": {
                "required": [],  # Generic schema, no specific requirements
                "optional": []
            }
        }
    
    def process(self, input_data, intent):
        """
        Process JSON input data.
        
        Args:
            input_data (str): The JSON input data
            intent (str): The classified intent
            
        Returns:
            dict: Processing result with extracted data and validation
        """
        self.logger.info(f"Processing JSON data with intent: {intent}")
        
        try:
            # Parse JSON
            json_data = json.loads(input_data)
            
            # Extract key fields based on intent
            extracted_data = self._extract_fields(json_data, intent)
            
            # Validate against schema
            validation_result = self._validate_schema(json_data, intent)
            
            # Detect anomalies
            anomalies = self._detect_anomalies(json_data, intent)
            
            result = {
                "extracted_data": extracted_data,
                "validation": validation_result,
                "anomalies": anomalies
            }
            
            self.logger.info("JSON processing completed successfully")
            return result
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON: {str(e)}")
            return {
                "error": "Invalid JSON format",
                "details": str(e)
            }
        except Exception as e:
            self.logger.error(f"Error processing JSON: {str(e)}")
            return {
                "error": "Error processing JSON",
                "details": str(e)
            }
    
    def _extract_fields(self, json_data, intent):
        """
        Extract relevant fields based on intent.
        
        Args:
            json_data (dict): The parsed JSON data
            intent (str): The classified intent
            
        Returns:
            dict: Extracted fields
        """
        extracted_data = {}
        
        # Common fields to extract for any intent
        common_fields = ["id", "customer", "date", "reference", "description", "total"]
        for field in common_fields:
            if field in json_data:
                extracted_data[field] = json_data[field]
        
        # Intent-specific extraction
        if intent == "invoice":
            invoice_fields = ["invoice_number", "due_date", "items", "subtotal", "tax", "total"]
            for field in invoice_fields:
                if field in json_data:
                    extracted_data[field] = json_data[field]
                    
            # Calculate total if not present but items are
            if "total" not in extracted_data and "items" in extracted_data:
                total = sum(item.get("price", 0) * item.get("quantity", 1) for item in extracted_data["items"])
                extracted_data["calculated_total"] = total
                
        elif intent == "rfq":
            rfq_fields = ["items", "deadline", "delivery_address", "contact_person"]
            for field in rfq_fields:
                if field in json_data:
                    extracted_data[field] = json_data[field]
        
        return extracted_data
    
    def _validate_schema(self, json_data, intent):
        """
        Validate JSON data against the schema for the given intent.
        
        Args:
            json_data (dict): The parsed JSON data
            intent (str): The classified intent
            
        Returns:
            dict: Validation result
        """
        # Get schema for this intent, or use data_exchange as fallback
        schema = self.schemas.get(intent, self.schemas["data_exchange"])
        
        missing_required = []
        for field in schema["required"]:
            if field not in json_data:
                missing_required.append(field)
        
        return {
            "valid": len(missing_required) == 0,
            "missing_required": missing_required,
            "optional_present": [field for field in schema["optional"] if field in json_data]
        }
    
    def _detect_anomalies(self, json_data, intent):
        """
        Detect anomalies in the JSON data.
        
        Args:
            json_data (dict): The parsed JSON data
            intent (str): The classified intent
            
        Returns:
            list: Detected anomalies
        """
        anomalies = []
        
        # Check for empty or null values in any field
        for key, value in json_data.items():
            if value is None or (isinstance(value, str) and value.strip() == ""):
                anomalies.append(f"Empty value for field: {key}")
        
        # Intent-specific anomaly detection
        if intent == "invoice":
            # Check if total matches sum of items
            if "total" in json_data and "items" in json_data:
                calculated_total = sum(item.get("price", 0) * item.get("quantity", 1) for item in json_data["items"])
                if abs(json_data["total"] - calculated_total) > 0.01:  # Allow small floating point differences
                    anomalies.append(f"Total ({json_data['total']}) doesn't match sum of items ({calculated_total})")
            
            # Check for future dates in invoice
            if "date" in json_data:
                # In a real implementation, we would check if date is in the future
                pass
        
        return anomalies