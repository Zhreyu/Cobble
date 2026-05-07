#!/usr/bin/env python3

import os
import logging

from src.services.file_organizer import SmartFileSorter
from src.context.file_organizer_context import FileOrganizerContext

logger = logging.getLogger(__name__)

def show_menu(sorter: SmartFileSorter, directory: str, context_file: str = "file_organizer_context.json"):
    """
    A simpler menu for organizing or reverting files, adding rules, etc.
    Call from your main.py to run the CLI.
    """
    # Load existing context if available
    if os.path.exists(context_file):
        try:
            with open(context_file, 'r') as f:
                sorter.context = FileOrganizerContext.from_json(f.read())
        except Exception as e:
            logger.error(f"Error loading context: {str(e)}")

    try:
        while True:
            print("\n========================================")
            print("           File Organizer Menu          ")
            print("========================================")
            print("1. Start sorting files")
            print("2. Add custom rule")
            print("3. View current rules")
            print("4. Exit")

            choice = input("\nEnter your choice (1-4): ")

            if choice == "1":
                preview = sorter.preview_organization(directory)
                while True:
                    sorter.display_preview(preview)
                    print("\nOptions:")
                    print("1. Proceed with sorting")
                    print("2. Refine organization")
                    print("3. Cancel")
                    
                    subchoice = input("\nEnter your choice (1-3): ")
                    if subchoice == "1":
                        sorter.organize_files(directory, preview)
                        break
                    elif subchoice == "2":
                        user_input = input("\nHow would you like to modify the organization? (e.g., 'Move PDFs to LectureNotes/PDF'): ")
                        preview = sorter.refine_preview(preview, user_input)
                    else:
                        # subchoice == '3' or invalid => cancel
                        break

            elif choice == "2":
                rule_text = input("Enter your rule (e.g., 'Put all PDFs with Biology in them into LectureNotes/Biology'): ")
                if sorter.add_custom_rule(rule_text):
                    print("✅ Rule added successfully!")
                else:
                    print("❌ Failed to add rule.")

            elif choice == "3":
                sorter.show_rules()

            elif choice == "4":
                print("\nExiting File Organizer.")
                break

            else:
                print("\n⚠️ Invalid choice. Please try again.")

            # Persist the context after each operation
            with open(context_file, 'w') as f:
                f.write(sorter.context.to_json())

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        # Always save the context on exit
        with open(context_file, 'w') as f:
            f.write(sorter.context.to_json())
