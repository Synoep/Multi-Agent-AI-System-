import os
from dotenv import load_dotenv
from agents.classifier_agent import ClassifierAgent
from agents.json_agent import JSONAgent
from agents.email_agent import EmailAgent
from memory.memory_store import MemoryStore
from utils.logger import setup_logger

# Load environment variables
load_dotenv()

# Setup logger
logger = setup_logger()

def process_input(input_data, conversation_id=None):
    """
    Process input data through the multi-agent system.
    
    Args:
        input_data (str): The input data to process
        conversation_id (str, optional): Conversation ID for continuing a thread
        
    Returns:
        dict: The processing results
    """
    # Initialize shared memory
    memory = MemoryStore()
    
    # Initialize agents
    classifier = ClassifierAgent(memory)
    json_agent = JSONAgent(memory)
    email_agent = EmailAgent(memory)
    
    # If conversation_id is provided, load previous context
    if conversation_id:
        memory.load_conversation(conversation_id)
    else:
        # Generate a new conversation ID
        conversation_id = memory.create_conversation()
    
    logger.info(f"Processing input with conversation ID: {conversation_id}")
    
    # Classify the input
    classification = classifier.classify(input_data)
    
    # Store classification in memory
    memory.add_entry({
        "step": "classification",
        "format": classification["format"],
        "intent": classification["intent"],
        "conversation_id": conversation_id
    })
    
    # Route to appropriate agent based on classification
    if classification["format"] == "json":
        result = json_agent.process(input_data, classification["intent"])
    elif classification["format"] == "email":
        result = email_agent.process(input_data, classification["intent"])
    else:
        # For now, we don't have a PDF agent implemented
        result = {
            "error": "Unsupported format",
            "format": classification["format"]
        }
    
    # Store result in memory
    memory.add_entry({
        "step": "processing",
        "result": result,
        "conversation_id": conversation_id
    })
    
    # Return the combined result with conversation_id for traceability
    return {
        "conversation_id": conversation_id,
        "classification": classification,
        "result": result,
        "memory": memory.get_conversation(conversation_id)
    }

if __name__ == "__main__":
    # Simple demo
    print("Multi-Agent AI System")
    print("=====================")
    print("1. Process JSON")
    print("2. Process Email")
    
    choice = input("\nSelect an option (1-2): ")
    
    if choice == "1":
        sample_json = """
        {
            "customer": "Acme Corp",
            "order_id": "ORD-12345",
            "items": [
                {"product": "Widget A", "quantity": 5, "price": 10.99},
                {"product": "Widget B", "quantity": 3, "price": 15.99}
            ],
            "total": 129.92
        }
        """
        result = process_input(sample_json)
    elif choice == "2":
        sample_email = """
        From: john.doe@example.com
        To: sales@company.com
        Subject: Request for Quotation - Office Supplies
        
        Hello,
        
        We are interested in purchasing office supplies for our new branch.
        Could you please provide a quotation for the following items:
        
        - 20 ergonomic chairs
        - 10 height-adjustable desks
        - 15 desk lamps
        
        We would appreciate a response within the next week.
        
        Best regards,
        John Doe
        Procurement Manager
        Acme Corp
        """
        result = process_input(sample_email)
    else:
        print("Invalid option selected.")
        exit(1)
    
    # Print the result in a nicely formatted way
    print("\nProcessing Result:")
    print(f"Conversation ID: {result['conversation_id']}")
    print(f"Classified as: {result['classification']['format']} - {result['classification']['intent']}")
    print("\nExtracted Information:")
    for key, value in result['result'].items():
        print(f"  {key}: {value}")
    
    print("\nMemory Trail:")
    for entry in result['memory']:
        print(f"  Step: {entry.get('step')} - {entry.get('timestamp')}")