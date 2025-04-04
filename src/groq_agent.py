"""
Groq API Integration for File Sorter App

This module handles the integration with Groq API for intelligent file categorization
using a multi-agent approach.
"""

import os
import json
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class GroqAgent:
    """
    Manages interactions with the Groq API for intelligent file categorization.
    """
    
    def __init__(self, api_key=None):
        """
        Initialize the Groq API client.
        
        Args:
            api_key (str, optional): Groq API key. If not provided, will try to get from environment.
        """
        # Use provided API key or get from environment
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        
        if not self.api_key:
            raise ValueError("Groq API key is required. Please provide it or set GROQ_API_KEY environment variable.")
        
        # Initialize Groq client
        self.client = Groq(api_key=self.api_key)
        
        # Default model
        self.model = "llama3-70b-8192"
    
    def categorize_files(self, file_list):
        """
        Categorize a list of files using Groq API.
        
        Args:
            file_list (list): List of file paths to categorize
            
        Returns:
            dict: Categorization results with suggested categories and explanations
        """
        # Extract file information
        file_info = []
        for file_path in file_list:
            path = Path(file_path)
            file_info.append({
                "name": path.name,
                "extension": path.suffix.lower(),
                "size": os.path.getsize(file_path),
                "path": str(file_path)
            })
        
        # Create prompt for Groq API
        prompt = self._create_categorization_prompt(file_info)
        
        # Call Groq API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a file organization expert that helps categorize files into logical groups."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=4000
        )
        
        # Parse and return the categorization results
        return self._parse_categorization_response(response.choices[0].message.content)
    
    def _create_categorization_prompt(self, file_info):
        """
        Create a prompt for file categorization.
        
        Args:
            file_info (list): List of dictionaries containing file information
            
        Returns:
            str: Prompt for Groq API
        """
        prompt = """
I need help categorizing the following files into logical groups. Please analyze the file names, extensions, and other information to suggest appropriate categories.

Files to categorize:
"""
        
        for file in file_info:
            prompt += f"- {file['name']} ({file['extension']}, {self._format_size(file['size'])})\n"
        
        prompt += """
Please provide your response in the following JSON format:
{
    "categories": [
        {
            "name": "Category Name",
            "description": "Brief description of this category",
            "files": ["file1.ext", "file2.ext"],
            "suggested_folder": "folder_name"
        }
    ],
    "uncategorized": ["file3.ext"],
    "explanation": "Brief explanation of your categorization logic"
}

Consider common file organization patterns like document types, media types, project-related files, etc. Be specific with category names and try to minimize the number of uncategorized files.
"""
        return prompt
    
    def _parse_categorization_response(self, response_text):
        """
        Parse the response from Groq API.
        
        Args:
            response_text (str): Response text from Groq API
            
        Returns:
            dict: Parsed categorization results
        """
        try:
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            
            # Parse JSON
            categorization = json.loads(json_str)
            return categorization
        except Exception as e:
            print(f"Error parsing categorization response: {e}")
            # Return a basic structure if parsing fails
            return {
                "categories": [],
                "uncategorized": [],
                "explanation": "Failed to parse categorization response."
            }
    
    def get_custom_rule_suggestions(self, file_list):
        """
        Generate suggestions for custom categorization rules based on file patterns.
        
        Args:
            file_list (list): List of file paths
            
        Returns:
            list: Suggested custom rules
        """
        # Extract file information
        file_info = []
        for file_path in file_list:
            path = Path(file_path)
            file_info.append({
                "name": path.name,
                "extension": path.suffix.lower(),
                "size": os.path.getsize(file_path),
                "path": str(file_path)
            })
        
        # Create prompt for Groq API
        prompt = """
Based on the following files, suggest custom rules for file organization that would be useful for the user.

Files:
"""
        
        for file in file_info:
            prompt += f"- {file['name']} ({file['extension']}, {self._format_size(file['size'])})\n"
        
        prompt += """
Please provide your response in the following JSON format:
{
    "suggested_rules": [
        {
            "name": "Rule Name",
            "description": "Description of what this rule does",
            "pattern": "Pattern to match (e.g., extension, name pattern)",
            "target_folder": "Suggested folder name"
        }
    ],
    "explanation": "Explanation of why these rules would be helpful"
}

Focus on patterns that would be useful for long-term file organization, not just for the current set of files.
"""
        
        # Call Groq API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a file organization expert that helps create custom rules for file sorting."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        # Parse and return the rule suggestions
        try:
            # Extract JSON from response
            response_text = response.choices[0].message.content
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            
            # Parse JSON
            rule_suggestions = json.loads(json_str)
            return rule_suggestions
        except Exception as e:
            print(f"Error parsing rule suggestions response: {e}")
            return {
                "suggested_rules": [],
                "explanation": "Failed to parse rule suggestions response."
            }
    
    def _format_size(self, size_bytes):
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes (int): File size in bytes
            
        Returns:
            str: Formatted file size
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"


# Test function for Groq API integration
def test_groq_integration(api_key):
    """
    Test the Groq API integration.
    
    Args:
        api_key (str): Groq API key for testing
    """
    try:
        # Initialize GroqAgent with the provided API key
        agent = GroqAgent(api_key=api_key)
        
        # Test with a simple message to verify API connection
        response = agent.client.chat.completions.create(
            model=agent.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, are you working properly?"}
            ],
            max_tokens=100
        )
        
        print("Groq API connection test successful!")
        print(f"Response: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"Error testing Groq API integration: {e}")
        return False


if __name__ == "__main__":
    # Get API key from environment or use a test key
    api_key = os.getenv("GROQ_API_KEY", "your_api_key_here")
    test_groq_integration(api_key)
