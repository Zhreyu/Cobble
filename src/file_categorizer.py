"""
File Categorization Logic for File Sorter App

This module handles the intelligent categorization of files using the Groq API
and implements the multi-agent approach for file sorting.
"""

import os
import json
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from src.groq_agent import GroqAgent
from src.backup_system import BackupSystem


class FileCategorizer:
    """
    Manages the categorization and sorting of files using a multi-agent approach.
    """
    
    def __init__(self, groq_agent=None, backup_system=None):
        """
        Initialize the file categorizer.
        
        Args:
            groq_agent (GroqAgent, optional): Instance of GroqAgent for API calls
            backup_system (BackupSystem, optional): Instance of BackupSystem for backups
        """
        self.groq_agent = groq_agent or GroqAgent()
        self.backup_system = backup_system or BackupSystem()
        self.custom_rules = []
        self.last_backup_id = None
        
    def scan_directory(self, directory_path):
        """
        Scan a directory for files to categorize.
        
        Args:
            directory_path (str): Path to the directory to scan
            
        Returns:
            list: List of file paths found in the directory
        """
        directory = Path(directory_path)
        if not directory.exists() or not directory.is_dir():
            raise ValueError(f"Invalid directory path: {directory_path}")
        
        # Get all files in the directory (non-recursive)
        files = [str(f) for f in directory.glob('*') if f.is_file()]
        
        print(f"Found {len(files)} files in {directory_path}")
        return files
    
    def categorize_files(self, directory_path, batch_size=50, create_backup=True):
        """
        Categorize files in a directory using the Groq API.
        
        Args:
            directory_path (str): Path to the directory containing files to categorize
            batch_size (int, optional): Number of files to process in each batch
            create_backup (bool, optional): Whether to create a backup before categorizing
            
        Returns:
            dict: Categorization results
        """
        # Create backup if requested
        if create_backup:
            self.last_backup_id = self.backup_system.create_backup(directory_path)
            print(f"Created backup with ID: {self.last_backup_id}")
        
        # Scan directory for files
        files = self.scan_directory(directory_path)
        if not files:
            return {"categories": [], "uncategorized": [], "explanation": "No files found in directory."}
        
        # Process files in batches to avoid API limits
        batches = [files[i:i + batch_size] for i in range(0, len(files), batch_size)]
        all_results = []
        
        # Process each batch
        for i, batch in enumerate(batches):
            print(f"Processing batch {i+1}/{len(batches)} ({len(batch)} files)...")
            batch_result = self.groq_agent.categorize_files(batch)
            all_results.append(batch_result)
        
        # Merge results from all batches
        merged_results = self._merge_categorization_results(all_results)
        
        # Apply custom rules if any
        if self.custom_rules:
            merged_results = self._apply_custom_rules(merged_results, files)
        
        return merged_results
    
    def sort_files(self, directory_path, categorization_results):
        """
        Sort files according to categorization results.
        
        Args:
            directory_path (str): Path to the directory containing files to sort
            categorization_results (dict): Results from categorize_files method
            
        Returns:
            dict: Summary of sorting operation
        """
        directory = Path(directory_path)
        summary = {"moved": 0, "skipped": 0, "errors": 0, "categories": {}}
        
        # Process each category
        for category in categorization_results.get("categories", []):
            category_name = category.get("name", "Unknown")
            folder_name = category.get("suggested_folder", category_name.lower().replace(" ", "_"))
            target_dir = directory / folder_name
            
            # Create target directory if it doesn't exist
            os.makedirs(target_dir, exist_ok=True)
            
            # Track files in this category
            summary["categories"][category_name] = {
                "folder": str(target_dir),
                "files_moved": 0,
                "files": []
            }
            
            # Move files to target directory
            for filename in category.get("files", []):
                source_path = directory / filename
                target_path = target_dir / filename
                
                try:
                    if source_path.exists():
                        # Skip if file already exists in target
                        if target_path.exists():
                            print(f"Skipping {filename} - already exists in target directory")
                            summary["skipped"] += 1
                            continue
                        
                        # Move the file
                        shutil.move(str(source_path), str(target_path))
                        summary["moved"] += 1
                        summary["categories"][category_name]["files_moved"] += 1
                        summary["categories"][category_name]["files"].append(filename)
                        print(f"Moved {filename} to {folder_name}/")
                    else:
                        print(f"Skipping {filename} - file not found")
                        summary["skipped"] += 1
                except Exception as e:
                    print(f"Error moving {filename}: {e}")
                    summary["errors"] += 1
        
        return summary
    
    def add_custom_rule(self, rule):
        """
        Add a custom categorization rule.
        
        Args:
            rule (dict): Rule definition with name, pattern, and target_folder
            
        Returns:
            bool: True if rule was added successfully
        """
        if not isinstance(rule, dict):
            return False
        
        required_fields = ["name", "pattern", "target_folder"]
        if not all(field in rule for field in required_fields):
            return False
        
        self.custom_rules.append(rule)
        return True
    
    def remove_custom_rule(self, rule_name):
        """
        Remove a custom rule by name.
        
        Args:
            rule_name (str): Name of the rule to remove
            
        Returns:
            bool: True if rule was removed, False if not found
        """
        initial_count = len(self.custom_rules)
        self.custom_rules = [r for r in self.custom_rules if r.get("name") != rule_name]
        return len(self.custom_rules) < initial_count
    
    def get_custom_rules(self):
        """
        Get all custom rules.
        
        Returns:
            list: List of custom rules
        """
        return self.custom_rules
    
    def revert_to_original(self, directory_path, backup_id=None):
        """
        Revert files to their original organization using a backup.
        
        Args:
            directory_path (str): Path to the directory to revert
            backup_id (str, optional): Specific backup ID to use, or latest if None
            
        Returns:
            bool: True if reversion was successful
        """
        # Use specified backup ID or the last one created
        backup_id = backup_id or self.last_backup_id
        
        if not backup_id:
            print("No backup ID specified and no recent backup found.")
            return False
        
        # Restore from backup
        return self.backup_system.restore_backup(backup_id)
    
    def _merge_categorization_results(self, results_list):
        """
        Merge categorization results from multiple batches.
        
        Args:
            results_list (list): List of categorization results from different batches
            
        Returns:
            dict: Merged categorization results
        """
        if not results_list:
            return {"categories": [], "uncategorized": [], "explanation": "No results to merge."}
        
        # Initialize merged results
        merged = {
            "categories": [],
            "uncategorized": [],
            "explanation": "Merged results from multiple batches."
        }
        
        # Track categories by name for merging
        categories_by_name = {}
        
        # Process each result set
        for result in results_list:
            # Process categories
            for category in result.get("categories", []):
                name = category.get("name")
                if name in categories_by_name:
                    # Merge with existing category
                    existing = categories_by_name[name]
                    existing["files"].extend(category.get("files", []))
                    # Remove duplicates
                    existing["files"] = list(set(existing["files"]))
                else:
                    # Add new category
                    categories_by_name[name] = category
            
            # Add uncategorized files
            merged["uncategorized"].extend(result.get("uncategorized", []))
        
        # Remove duplicates from uncategorized
        merged["uncategorized"] = list(set(merged["uncategorized"]))
        
        # Convert categories dictionary back to list
        merged["categories"] = list(categories_by_name.values())
        
        return merged
    
    def _apply_custom_rules(self, categorization_results, all_files):
        """
        Apply custom rules to categorization results.
        
        Args:
            categorization_results (dict): Original categorization results
            all_files (list): List of all files being categorized
            
        Returns:
            dict: Updated categorization results after applying custom rules
        """
        if not self.custom_rules:
            return categorization_results
        
        # Create a copy of the results to modify
        results = {
            "categories": categorization_results.get("categories", []).copy(),
            "uncategorized": categorization_results.get("uncategorized", []).copy(),
            "explanation": categorization_results.get("explanation", "") + " Custom rules applied."
        }
        
        # Track files that have been categorized
        categorized_files = set()
        for category in results["categories"]:
            for filename in category.get("files", []):
                categorized_files.add(os.path.basename(filename))
        
        # Apply each custom rule
        for rule in self.custom_rules:
            rule_name = rule.get("name", "Unnamed Rule")
            pattern = rule.get("pattern", "")
            target_folder = rule.get("target_folder", "custom")
            
            # Find or create the target category
            target_category = None
            for category in results["categories"]:
                if category.get("name") == rule_name:
                    target_category = category
                    break
            
            if target_category is None:
                target_category = {
                    "name": rule_name,
                    "description": rule.get("description", f"Files matching pattern: {pattern}"),
                    "files": [],
                    "suggested_folder": target_folder
                }
                results["categories"].append(target_category)
            
            # Apply the rule to uncategorized files and all files not yet categorized
            newly_categorized = []
            
            # Check uncategorized files first
            for filename in results["uncategorized"]:
                base_filename = os.path.basename(filename)
                if self._matches_pattern(base_filename, pattern):
                    target_category["files"].append(filename)
                    newly_categorized.append(filename)
                    categorized_files.add(base_filename)
            
            # Remove newly categorized files from uncategorized list
            results["uncategorized"] = [f for f in results["uncategorized"] if f not in newly_categorized]
            
            # Check all files that haven't been categorized yet
            for filepath in all_files:
                filename = os.path.basename(filepath)
                if filename not in categorized_files and self._matches_pattern(filename, pattern):
                    target_category["files"].append(filepath)
                    categorized_files.add(filename)
        
        return results
    
    def _matches_pattern(self, filename, pattern):
        """
        Check if a filename matches a pattern.
        
        Args:
            filename (str): Filename to check
            pattern (str): Pattern to match against
            
        Returns:
            bool: True if filename matches pattern
        """
        # Handle extension patterns (e.g., ".pdf")
        if pattern.startswith("."):
            return filename.lower().endswith(pattern.lower())
        
        # Handle wildcard patterns (e.g., "*.jpg")
        if pattern.startswith("*"):
            suffix = pattern[1:]
            return filename.lower().endswith(suffix.lower())
        
        # Handle prefix patterns (e.g., "report_*")
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            return filename.lower().startswith(prefix.lower())
        
        # Handle contains patterns (e.g., "contains:invoice")
        if pattern.startswith("contains:"):
            substring = pattern[9:]
            return substring.lower() in filename.lower()
        
        # Handle regex patterns (not implemented in this version)
        
        # Default: exact match
        return filename.lower() == pattern.lower()


# Test function
def test_file_categorizer():
    """Test the file categorizer functionality."""
    from src.groq_agent import GroqAgent
    from src.backup_system import BackupSystem
    
    # Create test directory and files
    test_dir = Path("/home/ubuntu/file_sorter_app/tests/test_files")
    os.makedirs(test_dir, exist_ok=True)
    
    # Create some test files
    test_files = [
        "document1.pdf", "document2.pdf", "image1.jpg", "image2.png",
        "spreadsheet.xlsx", "presentation.pptx", "notes.txt", "script.py"
    ]
    
    for filename in test_files:
        with open(test_dir / filename, 'w') as f:
            f.write(f"Test content for {filename}")
    
    print(f"Created test directory with {len(test_files)} files at {test_dir}")
    
    # Initialize components
    groq_agent = GroqAgent()
    backup_system = BackupSystem()
    categorizer = FileCategorizer(groq_agent, backup_system)
    
    # Add a custom rule
    categorizer.add_custom_rule({
        "name": "Python Files",
        "description": "Python script files",
        "pattern": ".py",
        "target_folder": "python_scripts"
    })
    
    print("File categorizer initialized with custom rule for Python files.")
    print(f"Custom rules: {categorizer.get_custom_rules()}")
    
    # Scan directory
    files = categorizer.scan_directory(str(test_dir))
    print(f"Scanned directory, found {len(files)} files.")
    
    print("File categorizer test completed successfully.")
    return categorizer, test_dir


if __name__ == "__main__":
    test_file_categorizer()
