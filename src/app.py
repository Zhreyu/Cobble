"""
User Interface for File Sorter App

This module implements the GUI for the file sorting application using customtkinter.
"""

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from pathlib import Path

from src.file_categorizer import FileCategorizer
from src.groq_agent import GroqAgent
from src.backup_system import BackupSystem


class FileSorterApp(ctk.CTk):
    """
    Main application window for the File Sorter App.
    """
    
    def __init__(self):
        """Initialize the application window and components."""
        super().__init__()
        
        # Initialize backend components
        self.groq_agent = GroqAgent()
        self.backup_system = BackupSystem()
        self.file_categorizer = FileCategorizer(self.groq_agent, self.backup_system)
        
        # Configure window
        self.title("Smart File Sorter")
        self.geometry("900x700")
        self.minsize(800, 600)
        
        # Set appearance mode and color theme
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # Initialize UI variables
        self.selected_directory = tk.StringVar()
        self.status_text = tk.StringVar(value="Ready")
        self.progress_value = tk.DoubleVar(value=0)
        self.current_backup_id = tk.StringVar()
        
        # Create UI components
        self._create_ui()
        
        # Track running operations
        self.running_operation = False
    
    def _create_ui(self):
        """Create the user interface components."""
        # Create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create header
        header_frame = ctk.CTkFrame(self.main_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        header_label = ctk.CTkLabel(
            header_frame, 
            text="Smart File Sorter", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        header_label.pack(pady=10)
        
        description_label = ctk.CTkLabel(
            header_frame,
            text="Organize your files intelligently using AI-powered multi-agent system",
            font=ctk.CTkFont(size=14)
        )
        description_label.pack(pady=(0, 10))
        
        # Create directory selection section
        dir_frame = ctk.CTkFrame(self.main_frame)
        dir_frame.pack(fill=tk.X, padx=10, pady=5)
        
        dir_label = ctk.CTkLabel(dir_frame, text="Select Directory:", font=ctk.CTkFont(size=16))
        dir_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        dir_select_frame = ctk.CTkFrame(dir_frame)
        dir_select_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        dir_entry = ctk.CTkEntry(dir_select_frame, textvariable=self.selected_directory)
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_button = ctk.CTkButton(
            dir_select_frame, 
            text="Browse", 
            command=self._browse_directory
        )
        browse_button.pack(side=tk.RIGHT)
        
        # Create action buttons
        action_frame = ctk.CTkFrame(self.main_frame)
        action_frame.pack(fill=tk.X, padx=10, pady=5)
        
        sort_button = ctk.CTkButton(
            action_frame,
            text="Sort Files",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=40,
            command=self._sort_files
        )
        sort_button.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
        
        revert_button = ctk.CTkButton(
            action_frame,
            text="Revert to Original",
            font=ctk.CTkFont(size=15),
            height=40,
            command=self._revert_to_original
        )
        revert_button.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
        
        custom_rules_button = ctk.CTkButton(
            action_frame,
            text="Custom Rules",
            font=ctk.CTkFont(size=15),
            height=40,
            command=self._open_custom_rules
        )
        custom_rules_button.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
        
        # Create status section
        status_frame = ctk.CTkFrame(self.main_frame)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        status_label = ctk.CTkLabel(status_frame, text="Status:", font=ctk.CTkFont(size=14))
        status_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        status_text_label = ctk.CTkLabel(status_frame, textvariable=self.status_text)
        status_text_label.pack(anchor=tk.W, padx=10, pady=(0, 5))
        
        self.progress_bar = ctk.CTkProgressBar(status_frame)
        self.progress_bar.pack(fill=tk.X, padx=10, pady=(0, 10))
        self.progress_bar.set(0)
        
        # Create results section
        results_frame = ctk.CTkFrame(self.main_frame)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        results_label = ctk.CTkLabel(results_frame, text="Results:", font=ctk.CTkFont(size=16))
        results_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        self.results_text = ctk.CTkTextbox(results_frame, font=ctk.CTkFont(size=12))
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.results_text.configure(state=tk.DISABLED)
        
        # Create footer
        footer_frame = ctk.CTkFrame(self.main_frame)
        footer_frame.pack(fill=tk.X, padx=10, pady=5)
        
        backup_label = ctk.CTkLabel(footer_frame, text="Current Backup ID:")
        backup_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        backup_id_label = ctk.CTkLabel(footer_frame, textvariable=self.current_backup_id)
        backup_id_label.pack(side=tk.LEFT, padx=0, pady=10)
        
        version_label = ctk.CTkLabel(footer_frame, text="v1.0.0")
        version_label.pack(side=tk.RIGHT, padx=10, pady=10)
    
    def _browse_directory(self):
        """Open a directory browser dialog."""
        directory = filedialog.askdirectory()
        if directory:
            self.selected_directory.set(directory)
            self._update_status(f"Selected directory: {directory}")
    
    def _sort_files(self):
        """Sort files in the selected directory."""
        directory = self.selected_directory.get()
        if not directory:
            messagebox.showerror("Error", "Please select a directory first.")
            return
        
        if self.running_operation:
            messagebox.showinfo("Operation in Progress", "Please wait for the current operation to complete.")
            return
        
        # Clear previous results
        self.results_text.configure(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        self.results_text.configure(state=tk.DISABLED)
        
        # Start sorting in a separate thread
        self.running_operation = True
        threading.Thread(target=self._sort_files_thread, args=(directory,), daemon=True).start()
    
    def _sort_files_thread(self, directory):
        """Thread function for sorting files."""
        try:
            self._update_status("Scanning directory...")
            self.progress_bar.set(0.1)
            
            # Scan directory
            files = self.file_categorizer.scan_directory(directory)
            if not files:
                self._update_status("No files found in the selected directory.")
                self.running_operation = False
                return
            
            self._update_status(f"Categorizing {len(files)} files...")
            self.progress_bar.set(0.3)
            
            # Categorize files
            categorization = self.file_categorizer.categorize_files(directory)
            self.progress_bar.set(0.7)
            
            # Store backup ID
            if self.file_categorizer.last_backup_id:
                self.current_backup_id.set(self.file_categorizer.last_backup_id)
            
            self._update_status("Sorting files...")
            
            # Sort files
            summary = self.file_categorizer.sort_files(directory, categorization)
            self.progress_bar.set(1.0)
            
            # Display results
            self._display_sorting_results(categorization, summary)
            
            self._update_status(f"Completed. Moved {summary['moved']} files into {len(summary['categories'])} categories.")
        except Exception as e:
            self._update_status(f"Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            self.running_operation = False
    
    def _revert_to_original(self):
        """Revert files to their original organization."""
        if self.running_operation:
            messagebox.showinfo("Operation in Progress", "Please wait for the current operation to complete.")
            return
        
        backup_id = self.current_backup_id.get()
        if not backup_id:
            # Check if there are any backups available
            backups = self.backup_system.list_backups()
            if not backups:
                messagebox.showerror("Error", "No backups available to restore from.")
                return
            
            # Use the most recent backup
            backup_id = backups[0]["id"]
        
        # Confirm revert operation
        if not messagebox.askyesno("Confirm Revert", "Are you sure you want to revert to the original file organization?"):
            return
        
        # Start revert in a separate thread
        self.running_operation = True
        threading.Thread(target=self._revert_thread, args=(backup_id,), daemon=True).start()
    
    def _revert_thread(self, backup_id):
        """Thread function for reverting files."""
        try:
            self._update_status(f"Reverting to backup {backup_id}...")
            self.progress_bar.set(0.3)
            
            # Revert to original
            success = self.file_categorizer.revert_to_original(None, backup_id)
            self.progress_bar.set(1.0)
            
            if success:
                self._update_status(f"Successfully reverted to original organization from backup {backup_id}.")
                
                # Display results
                self.results_text.configure(state=tk.NORMAL)
                self.results_text.delete("1.0", tk.END)
                self.results_text.insert(tk.END, f"Files have been restored to their original organization from backup {backup_id}.\n\n")
                self.results_text.insert(tk.END, "You may need to refresh your file explorer to see the changes.")
                self.results_text.configure(state=tk.DISABLED)
            else:
                self._update_status(f"Failed to revert to backup {backup_id}.")
                messagebox.showerror("Error", f"Failed to revert to backup {backup_id}.")
        except Exception as e:
            self._update_status(f"Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            self.running_operation = False
    
    def _open_custom_rules(self):
        """Open the custom rules dialog."""
        if self.running_operation:
            messagebox.showinfo("Operation in Progress", "Please wait for the current operation to complete.")
            return
        
        # Create custom rules window
        custom_rules_window = CustomRulesWindow(self, self.file_categorizer)
        custom_rules_window.grab_set()  # Make the window modal
    
    def _display_sorting_results(self, categorization, summary):
        """Display sorting results in the results text area."""
        self.results_text.configure(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        
        # Add summary
        self.results_text.insert(tk.END, f"Sorting Summary:\n")
        self.results_text.insert(tk.END, f"- Files moved: {summary['moved']}\n")
        self.results_text.insert(tk.END, f"- Files skipped: {summary['skipped']}\n")
        self.results_text.insert(tk.END, f"- Errors: {summary['errors']}\n\n")
        
        # Add categories
        self.results_text.insert(tk.END, f"Categories Created:\n")
        for category in categorization.get("categories", []):
            name = category.get("name", "Unknown")
            folder = category.get("suggested_folder", name.lower().replace(" ", "_"))
            files = category.get("files", [])
            
            self.results_text.insert(tk.END, f"- {name} ({len(files)} files) → {folder}/\n")
            
            # List first 5 files in each category
            for i, file in enumerate(files[:5]):
                filename = os.path.basename(file)
                self.results_text.insert(tk.END, f"  • {filename}\n")
            
            # Show ellipsis if there are more files
            if len(files) > 5:
                self.results_text.insert(tk.END, f"  • ... and {len(files) - 5} more\n")
            
            self.results_text.insert(tk.END, "\n")
        
        # Add uncategorized files
        uncategorized = categorization.get("uncategorized", [])
        if uncategorized:
            self.results_text.insert(tk.END, f"Uncategorized Files ({len(uncategorized)}):\n")
            for i, file in enumerate(uncategorized[:5]):
                filename = os.path.basename(file)
                self.results_text.insert(tk.END, f"- {filename}\n")
            
            # Show ellipsis if there are more files
            if len(uncategorized) > 5:
                self.results_text.insert(tk.END, f"- ... and {len(uncategorized) - 5} more\n")
        
        self.results_text.configure(state=tk.DISABLED)
    
    def _update_status(self, status):
        """Update the status text."""
        self.status_text.set(status)
        self.update_idletasks()


class CustomRulesWindow(ctk.CTkToplevel):
    """
    Window for managing custom categorization rules.
    """
    
    def __init__(self, parent, file_categorizer):
        """
        Initialize the custom rules window.
        
        Args:
            parent: Parent window
            file_categorizer: FileCategorizer instance
        """
        super().__init__(parent)
        
        self.file_categorizer = file_categorizer
        
        # Configure window
        self.title("Custom Rules")
        self.geometry("600x500")
        self.minsize(500, 400)
        
        # Initialize UI variables
        self.rule_name = tk.StringVar()
        self.rule_pattern = tk.StringVar()
        self.rule_folder = tk.StringVar()
        self.rule_description = tk.StringVar()
        
        # Create UI components
        self._create_ui()
        
        # Load existing rules
        self._load_rules()
    
    def _create_ui(self):
        """Create the user interface components."""
        # Create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create header
        header_label = ctk.CTkLabel(
            self.main_frame, 
            text="Custom Categorization Rules", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header_label.pack(pady=10)
        
        # Create rules list section
        rules_frame = ctk.CTkFrame(self.main_frame)
        rules_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        rules_label = ctk.CTkLabel(rules_frame, text="Current Rules:", font=ctk.CTkFont(size=14))
        rules_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Create scrollable frame for rules
        self.rules_list_frame = ctk.CTkScrollableFrame(rules_frame)
        self.rules_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Create add rule section
        add_rule_frame = ctk.CTkFrame(self.main_frame)
        add_rule_frame.pack(fill=tk.X, padx=10, pady=5)
        
        add_rule_label = ctk.CTkLabel(
            add_rule_frame, 
            text="Add New Rule", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        add_rule_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Rule name
        name_frame = ctk.CTkFrame(add_rule_frame)
        name_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        name_label = ctk.CTkLabel(name_frame, text="Rule Name:", width=100)
        name_label.pack(side=tk.LEFT, padx=(0, 5))
        
        name_entry = ctk.CTkEntry(name_frame, textvariable=self.rule_name)
        name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Rule pattern
        pattern_frame = ctk.CTkFrame(add_rule_frame)
        pattern_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        pattern_label = ctk.CTkLabel(pattern_frame, text="Pattern:", width=100)
        pattern_label.pack(side=tk.LEFT, padx=(0, 5))
        
        pattern_entry = ctk.CTkEntry(pattern_frame, textvariable=self.rule_pattern)
        pattern_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Rule folder
        folder_frame = ctk.CTkFrame(add_rule_frame)
        folder_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        folder_label = ctk.CTkLabel(folder_frame, text="Target Folder:", width=100)
        folder_label.pack(side=tk.LEFT, padx=(0, 5))
        
        folder_entry = ctk.CTkEntry(folder_frame, textvariable=self.rule_folder)
        folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Rule description
        desc_frame = ctk.CTkFrame(add_rule_frame)
        desc_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        desc_label = ctk.CTkLabel(desc_frame, text="Description:", width=100)
        desc_label.pack(side=tk.LEFT, padx=(0, 5))
        
        desc_entry = ctk.CTkEntry(desc_frame, textvariable=self.rule_description)
        desc_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Pattern help
        help_frame = ctk.CTkFrame(add_rule_frame)
        help_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        help_text = (
            "Pattern examples:\n"
            "- .pdf (matches files with .pdf extension)\n"
            "- *.jpg (matches files ending with .jpg)\n"
            "- report_* (matches files starting with 'report_')\n"
            "- contains:invoice (matches files containing 'invoice')"
        )
        
        help_label = ctk.CTkLabel(help_frame, text=help_text, justify=tk.LEFT)
        help_label.pack(anchor=tk.W, padx=10, pady=5)
        
        # Add button
        add_button = ctk.CTkButton(
            add_rule_frame,
            text="Add Rule",
            command=self._add_rule
        )
        add_button.pack(pady=(5, 10))
        
        # Create suggestion button
        suggest_frame = ctk.CTkFrame(self.main_frame)
        suggest_frame.pack(fill=tk.X, padx=10, pady=5)
        
        suggest_button = ctk.CTkButton(
            suggest_frame,
            text="Get Rule Suggestions",
            command=self._get_suggestions
        )
        suggest_button.pack(pady=10)
    
    def _load_rules(self):
        """Load and display existing rules."""
        # Clear existing rules display
        for widget in self.rules_list_frame.winfo_children():
            widget.destroy()
        
        # Get rules from file categorizer
        rules = self.file_categorizer.get_custom_rules()
        
        if not rules:
            no_rules_label = ctk.CTkLabel(
                self.rules_list_frame,
                text="No custom rules defined yet.",
                font=ctk.CTkFont(size=12, slant="italic")
            )
            no_rules_label.pack(pady=10)
            return
        
        # Display each rule
        for i, rule in enumerate(rules):
            rule_frame = ctk.CTkFrame(self.rules_list_frame)
            rule_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Rule header
            header_frame = ctk.CTkFrame(rule_frame)
            header_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
            
            name_label = ctk.CTkLabel(
                header_frame,
                text=rule.get("name", "Unnamed Rule"),
                font=ctk.CTkFont(size=14, weight="bold")
            )
            name_label.pack(side=tk.LEFT, padx=5)
            
            delete_button = ctk.CTkButton(
                header_frame,
                text="Delete",
                width=70,
                height=25,
                command=lambda r=rule.get("name"): self._delete_rule(r)
            )
            delete_button.pack(side=tk.RIGHT, padx=5)
            
            # Rule details
            details_frame = ctk.CTkFrame(rule_frame)
            details_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
            
            pattern_label = ctk.CTkLabel(
                details_frame,
                text=f"Pattern: {rule.get('pattern', 'None')}",
                font=ctk.CTkFont(size=12)
            )
            pattern_label.pack(anchor=tk.W, padx=5, pady=(0, 2))
            
            folder_label = ctk.CTkLabel(
                details_frame,
                text=f"Target Folder: {rule.get('target_folder', 'None')}",
                font=ctk.CTkFont(size=12)
            )
            folder_label.pack(anchor=tk.W, padx=5, pady=(0, 2))
            
            if "description" in rule:
                desc_label = ctk.CTkLabel(
                    details_frame,
                    text=f"Description: {rule.get('description')}",
                    font=ctk.CTkFont(size=12)
                )
                desc_label.pack(anchor=tk.W, padx=5, pady=(0, 2))
    
    def _add_rule(self):
        """Add a new custom rule."""
        name = self.rule_name.get().strip()
        pattern = self.rule_pattern.get().strip()
        folder = self.rule_folder.get().strip()
        description = self.rule_description.get().strip()
        
        # Validate inputs
        if not name or not pattern or not folder:
            messagebox.showerror("Error", "Rule name, pattern, and target folder are required.")
            return
        
        # Create rule
        rule = {
            "name": name,
            "pattern": pattern,
            "target_folder": folder,
            "description": description
        }
        
        # Add rule to file categorizer
        success = self.file_categorizer.add_custom_rule(rule)
        
        if success:
            # Clear inputs
            self.rule_name.set("")
            self.rule_pattern.set("")
            self.rule_folder.set("")
            self.rule_description.set("")
            
            # Reload rules display
            self._load_rules()
        else:
            messagebox.showerror("Error", "Failed to add rule. Please check the inputs.")
    
    def _delete_rule(self, rule_name):
        """Delete a custom rule."""
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the rule '{rule_name}'?"):
            success = self.file_categorizer.remove_custom_rule(rule_name)
            
            if success:
                # Reload rules display
                self._load_rules()
            else:
                messagebox.showerror("Error", f"Failed to delete rule '{rule_name}'.")
    
    def _get_suggestions(self):
        """Get rule suggestions based on selected directory."""
        directory = self.master.selected_directory.get()
        if not directory:
            messagebox.showerror("Error", "Please select a directory in the main window first.")
            return
        
        try:
            # Scan directory
            files = self.file_categorizer.scan_directory(directory)
            if not files:
                messagebox.showinfo("No Files", "No files found in the selected directory.")
                return
            
            # Get suggestions
            messagebox.showinfo("Getting Suggestions", "Analyzing files to generate rule suggestions. This may take a moment...")
            
            # This would normally be done in a separate thread, but for simplicity we'll do it here
            suggestions = self.file_categorizer.groq_agent.get_custom_rule_suggestions(files)
            
            # Display suggestions in a new window
            SuggestionWindow(self, suggestions, self.file_categorizer)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


class SuggestionWindow(ctk.CTkToplevel):
    """
    Window for displaying rule suggestions.
    """
    
    def __init__(self, parent, suggestions, file_categorizer):
        """
        Initialize the suggestion window.
        
        Args:
            parent: Parent window
            suggestions: Rule suggestions from Groq API
            file_categorizer: FileCategorizer instance
        """
        super().__init__(parent)
        
        self.suggestions = suggestions
        self.file_categorizer = file_categorizer
        
        # Configure window
        self.title("Rule Suggestions")
        self.geometry("600x500")
        self.minsize(500, 400)
        
        # Create UI components
        self._create_ui()
    
    def _create_ui(self):
        """Create the user interface components."""
        # Create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create header
        header_label = ctk.CTkLabel(
            self.main_frame, 
            text="Suggested Categorization Rules", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header_label.pack(pady=10)
        
        # Create explanation section
        if "explanation" in self.suggestions:
            explanation_frame = ctk.CTkFrame(self.main_frame)
            explanation_frame.pack(fill=tk.X, padx=10, pady=5)
            
            explanation_label = ctk.CTkLabel(
                explanation_frame,
                text="Explanation:",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            explanation_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
            
            explanation_text = ctk.CTkTextbox(explanation_frame, height=80)
            explanation_text.pack(fill=tk.X, padx=10, pady=(0, 10))
            explanation_text.insert("1.0", self.suggestions.get("explanation", "No explanation provided."))
            explanation_text.configure(state=tk.DISABLED)
        
        # Create suggestions section
        suggestions_frame = ctk.CTkFrame(self.main_frame)
        suggestions_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        suggestions_label = ctk.CTkLabel(
            suggestions_frame,
            text="Suggested Rules:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        suggestions_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Create scrollable frame for suggestions
        self.suggestions_list_frame = ctk.CTkScrollableFrame(suggestions_frame)
        self.suggestions_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Display suggestions
        suggested_rules = self.suggestions.get("suggested_rules", [])
        
        if not suggested_rules:
            no_suggestions_label = ctk.CTkLabel(
                self.suggestions_list_frame,
                text="No rule suggestions available.",
                font=ctk.CTkFont(size=12, slant="italic")
            )
            no_suggestions_label.pack(pady=10)
        else:
            for i, rule in enumerate(suggested_rules):
                rule_frame = ctk.CTkFrame(self.suggestions_list_frame)
                rule_frame.pack(fill=tk.X, padx=5, pady=5)
                
                # Rule header
                header_frame = ctk.CTkFrame(rule_frame)
                header_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
                
                name_label = ctk.CTkLabel(
                    header_frame,
                    text=rule.get("name", "Unnamed Rule"),
                    font=ctk.CTkFont(size=14, weight="bold")
                )
                name_label.pack(side=tk.LEFT, padx=5)
                
                add_button = ctk.CTkButton(
                    header_frame,
                    text="Add Rule",
                    width=70,
                    height=25,
                    command=lambda r=rule: self._add_rule(r)
                )
                add_button.pack(side=tk.RIGHT, padx=5)
                
                # Rule details
                details_frame = ctk.CTkFrame(rule_frame)
                details_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
                
                pattern_label = ctk.CTkLabel(
                    details_frame,
                    text=f"Pattern: {rule.get('pattern', 'None')}",
                    font=ctk.CTkFont(size=12)
                )
                pattern_label.pack(anchor=tk.W, padx=5, pady=(0, 2))
                
                folder_label = ctk.CTkLabel(
                    details_frame,
                    text=f"Target Folder: {rule.get('target_folder', 'None')}",
                    font=ctk.CTkFont(size=12)
                )
                folder_label.pack(anchor=tk.W, padx=5, pady=(0, 2))
                
                if "description" in rule:
                    desc_label = ctk.CTkLabel(
                        details_frame,
                        text=f"Description: {rule.get('description')}",
                        font=ctk.CTkFont(size=12)
                    )
                    desc_label.pack(anchor=tk.W, padx=5, pady=(0, 2))
    
    def _add_rule(self, rule):
        """Add a suggested rule to the file categorizer."""
        # Convert rule format if needed
        formatted_rule = {
            "name": rule.get("name", "Unnamed Rule"),
            "pattern": rule.get("pattern", ""),
            "target_folder": rule.get("target_folder", ""),
            "description": rule.get("description", "")
        }
        
        # Add rule to file categorizer
        success = self.file_categorizer.add_custom_rule(formatted_rule)
        
        if success:
            messagebox.showinfo("Success", f"Rule '{formatted_rule['name']}' added successfully.")
            
            # Reload rules in parent window
            self.master._load_rules()
        else:
            messagebox.showerror("Error", f"Failed to add rule '{formatted_rule['name']}'.")


def main():
    """Main entry point for the application."""
    app = FileSorterApp()
    app.mainloop()


if __name__ == "__main__":
    main()
