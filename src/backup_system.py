"""
Backup System for File Sorter App

This module handles the backup and restoration of files to ensure users can revert
to the original file organization if needed.
"""

import os
import json
import shutil
import datetime
from pathlib import Path


class BackupSystem:
    """
    Manages file backups and restoration for the file sorter application.
    """
    
    def __init__(self, backup_dir=None):
        """
        Initialize the backup system.
        
        Args:
            backup_dir (str, optional): Directory to store backups. Defaults to app's backup directory.
        """
        if backup_dir is None:
            # Use default backup directory in the application folder
            self.backup_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "backup"
        else:
            self.backup_dir = Path(backup_dir)
            
        # Create backup directory if it doesn't exist
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self, source_dir):
        """
        Create a backup of the original file organization.
        
        Args:
            source_dir (str): Directory to backup
            
        Returns:
            str: ID of the created backup
        """
        # Generate a unique backup ID based on timestamp
        backup_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create a directory for this specific backup
        backup_path = self.backup_dir / backup_id
        os.makedirs(backup_path, exist_ok=True)
        
        # Create a metadata file to store original file paths
        metadata = {"source_dir": str(source_dir), "files": {}}
        
        # Process all files in the source directory
        source_path = Path(source_dir)
        for file_path in source_path.rglob('*'):
            if file_path.is_file():
                # Get relative path from source directory
                rel_path = file_path.relative_to(source_path)
                
                # Create destination path in backup
                dest_path = backup_path / rel_path
                
                # Create parent directories if they don't exist
                os.makedirs(dest_path.parent, exist_ok=True)
                
                # Copy the file to backup
                shutil.copy2(file_path, dest_path)
                
                # Store the original path in metadata
                metadata["files"][str(rel_path)] = {
                    "original_path": str(file_path),
                    "backup_path": str(dest_path),
                    "size": os.path.getsize(file_path),
                    "modified_time": os.path.getmtime(file_path)
                }
        
        # Save metadata
        with open(backup_path / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=4)
            
        print(f"Backup created with ID: {backup_id}")
        return backup_id
    
    def restore_backup(self, backup_id):
        """
        Restore files from a backup to their original locations.
        
        Args:
            backup_id (str): ID of the backup to restore
            
        Returns:
            bool: True if restoration was successful, False otherwise
        """
        backup_path = self.backup_dir / backup_id
        
        # Check if backup exists
        if not backup_path.exists():
            print(f"Backup with ID {backup_id} not found.")
            return False
        
        # Load metadata
        try:
            with open(backup_path / "metadata.json", 'r') as f:
                metadata = json.load(f)
        except Exception as e:
            print(f"Error loading backup metadata: {e}")
            return False
        
        # Restore each file to its original location
        source_dir = Path(metadata["source_dir"])
        for rel_path, file_info in metadata["files"].items():
            # Get original and backup paths
            original_path = Path(file_info["original_path"])
            backup_file_path = Path(file_info["backup_path"])
            
            # Create parent directories if they don't exist
            os.makedirs(original_path.parent, exist_ok=True)
            
            # Copy the file back to its original location
            try:
                shutil.copy2(backup_file_path, original_path)
            except Exception as e:
                print(f"Error restoring file {rel_path}: {e}")
        
        print(f"Backup {backup_id} restored successfully.")
        return True
    
    def list_backups(self):
        """
        List all available backups.
        
        Returns:
            list: List of backup IDs and their metadata
        """
        backups = []
        
        for backup_dir in self.backup_dir.iterdir():
            if backup_dir.is_dir():
                metadata_path = backup_dir / "metadata.json"
                if metadata_path.exists():
                    try:
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                            
                        # Count files in backup
                        file_count = len(metadata["files"])
                        
                        backups.append({
                            "id": backup_dir.name,
                            "source_dir": metadata["source_dir"],
                            "file_count": file_count,
                            "created": backup_dir.name.replace("_", " ").replace("T", " ")
                        })
                    except Exception:
                        # Skip invalid backups
                        pass
        
        return backups
    
    def delete_backup(self, backup_id):
        """
        Delete a backup.
        
        Args:
            backup_id (str): ID of the backup to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        backup_path = self.backup_dir / backup_id
        
        # Check if backup exists
        if not backup_path.exists():
            print(f"Backup with ID {backup_id} not found.")
            return False
        
        # Delete the backup directory
        try:
            shutil.rmtree(backup_path)
            print(f"Backup {backup_id} deleted successfully.")
            return True
        except Exception as e:
            print(f"Error deleting backup {backup_id}: {e}")
            return False


# Simple test function
def test_backup_system():
    """Test the backup system functionality."""
    bs = BackupSystem()
    print("Backup system initialized.")
    print(f"Backup directory: {bs.backup_dir}")
    
    # List existing backups
    backups = bs.list_backups()
    print(f"Found {len(backups)} existing backups.")
    for backup in backups:
        print(f"  - {backup['id']}: {backup['file_count']} files from {backup['source_dir']}")


if __name__ == "__main__":
    test_backup_system()
