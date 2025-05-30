import os
import json
import mimetypes
from utils.logger import setup_logger

logger = setup_logger(name="file_utils")

def detect_file_type(file_path):
    """
    Detect the type of a file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: The detected file type (json, email, pdf, or unknown)
    """
    # Check if file exists
    if not os.path.isfile(file_path):
        logger.error(f"File not found: {file_path}")
        return "unknown"
    
    # Get file extension
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    # Check extension
    if ext == ".json":
        return "json"
    elif ext in [".eml", ".msg"]:
        return "email"
    elif ext == ".pdf":
        return "pdf"
    
    # Check MIME type
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        if mime_type == "application/json":
            return "json"
        elif mime_type in ["message/rfc822", "application/vnd.ms-outlook"]:
            return "email"
        elif mime_type == "application/pdf":
            return "pdf"
    
    # Try to detect by content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(1024)  # Read first 1KB for detection
            
            # Check if it's JSON
            try:
                json.loads(content)
                return "json"
            except json.JSONDecodeError:
                pass
            
            # Check if it's an email
            if content.startswith("From:") or content.startswith("To:") or "Subject:" in content:
                return "email"
            
            # Check if it's a PDF
            if content.startswith("%PDF-"):
                return "pdf"
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
    
    return "unknown"

def read_file(file_path):
    """
    Read a file and return its content.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: The file content, or None if an error occurred
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        return None

def write_file(file_path, content):
    """
    Write content to a file.
    
    Args:
        file_path (str): Path to the file
        content (str): Content to write
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Successfully wrote to file: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error writing to file {file_path}: {str(e)}")
        return False

def list_files(directory, extensions=None):
    """
    List files in a directory, optionally filtered by extensions.
    
    Args:
        directory (str): Directory to list files from
        extensions (list, optional): List of file extensions to include
        
    Returns:
        list: List of file paths
    """
    files = []
    
    try:
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                
                # Filter by extension if specified
                if extensions:
                    _, ext = os.path.splitext(filename)
                    if ext.lower() not in extensions:
                        continue
                
                files.append(file_path)
    except Exception as e:
        logger.error(f"Error listing files in {directory}: {str(e)}")
    
    return files