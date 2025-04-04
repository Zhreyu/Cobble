#!/usr/bin/env python3

import sys
import os
import logging

from src.context.file_organizer_context import FileOrganizerContext
from src.services.file_organizer import SmartFileSorter  

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory")
        sys.exit(1)

    # check LLM API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY environment variable not set")
        sys.exit(1)

    sorter = SmartFileSorter(api_key=api_key)

    # Optionally load file_organizer_context.json if you still want to store rules
    context_file = "file_organizer_context.json"
    old_context_json = None
    if os.path.exists(context_file):
        try:
            with open(context_file, 'r') as f:
                file_contents = f.read().strip()
                old_context_json = file_contents
                sorter.context = FileOrganizerContext.from_json(file_contents)
        except Exception as e:
            logger.error(f"Error loading context: {str(e)}")

    sorter.run(directory)

    # Save context if changed
    new_context_json = sorter.context.to_json().strip()
    if new_context_json != (old_context_json or ""):
        with open(context_file, 'w') as f:
            f.write(new_context_json)
        logger.info("Context file updated.")
    else:
        logger.info("No changes to context; not overwriting existing JSON.")

if __name__ == "__main__":
    main()
