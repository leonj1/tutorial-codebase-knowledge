#!/usr/bin/env python3
"""
Script to list all available OpenAI models for the provided API key.
"""

import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

def list_openai_models():
    """List all available OpenAI models for the provided API key."""
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # Get the OpenAI API key from environment variables
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not found.")
        print("Please set your OpenAI API key using:")
        print("  export OPENAI_API_KEY=your_api_key")
        print("Or create a .env file with OPENAI_API_KEY=your_api_key")
        sys.exit(1)
    
    try:
        # Initialize the OpenAI client
        client = OpenAI(api_key=api_key)
        
        # List all available models
        models = client.models.list()
        
        # Print the models in a readable format
        print(f"\n{'=' * 60}")
        print(f"{'ID':<40} {'Created':<20}")
        print(f"{'-' * 40} {'-' * 20}")
        
        # Sort models by ID for better readability
        sorted_models = sorted(models.data, key=lambda x: x.id)
        
        for model in sorted_models:
            created_at = model.created
            # Convert timestamp to readable date if available
            created_str = f"{created_at}" if created_at else "N/A"
            print(f"{model.id:<40} {created_str:<20}")
        
        print(f"{'=' * 60}")
        print(f"Total models available: {len(models.data)}")
        
    except Exception as e:
        print(f"Error: Failed to retrieve models: {e}")
        sys.exit(1)

if __name__ == "__main__":
    list_openai_models()
