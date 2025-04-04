# Smart File Sorter - User Documentation

## Introduction

Smart File Sorter is an intelligent file organization application that uses AI-powered multi-agent technology to automatically categorize and sort files in a selected directory. The application leverages the Groq API to analyze file types and patterns, creating a logical folder structure based on file content and characteristics.

## Table of Contents

1. [Installation](#installation)
2. [Getting Started](#getting-started)
3. [Main Features](#main-features)
4. [Using the Application](#using-the-application)
5. [Custom Rules](#custom-rules)
6. [Reverting Changes](#reverting-changes)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

## Installation

### Prerequisites

- Python 3.8 or higher
- Groq API key (obtain from [Groq's website](https://console.groq.com))

### Installation Methods

#### Method 1: Using the Installer Script (Recommended)

1. Download the application package
2. Run the installer script:
   ```
   python install.py
   ```
3. Follow the on-screen instructions to complete the installation
4. The installer will prompt you for your Groq API key

#### Method 2: Manual Installation

1. Clone or download the repository
2. Install dependencies:
   ```
   pip install groq python-dotenv customtkinter
   ```
3. Install the package:
   ```
   pip install -e .
   ```
4. Create a `.env` file in the application directory with your Groq API key:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

## Getting Started

1. Launch the application by running:
   ```
   file-sorter
   ```
   Or if you installed manually:
   ```
   python main.py
   ```

2. If you didn't set up your API key during installation, you can pass it as a command-line argument:
   ```
   file-sorter your_groq_api_key_here
   ```

3. The main application window will appear, ready for use.

## Main Features

- **Intelligent File Categorization**: Automatically analyzes and categorizes files based on their types, names, and content patterns
- **Multi-Agent Architecture**: Uses multiple specialized agents to handle different aspects of file organization
- **Custom Rules**: Create and manage your own file categorization rules
- **Backup System**: Automatically backs up your files before sorting, allowing you to revert to the original organization
- **User-Friendly Interface**: Simple and intuitive GUI for easy file management

## Using the Application

### Main Window

The main application window consists of several sections:

1. **Directory Selection**: Choose the folder containing files you want to organize
2. **Action Buttons**: Sort Files, Revert to Original, and Custom Rules
3. **Status Section**: Shows the current operation status and progress
4. **Results Section**: Displays the results of file sorting operations
5. **Footer**: Shows the current backup ID and application version

### Sorting Files

1. Click the "Browse" button to select a directory containing files you want to organize
2. Click the "Sort Files" button to begin the categorization process
3. The application will:
   - Create a backup of the original file organization
   - Analyze the files using the Groq API
   - Create category folders based on the analysis
   - Move files to their respective category folders
4. Once complete, the results section will show a summary of the categorization

### Viewing Results

After sorting, the results section will display:
- Number of files moved, skipped, and any errors
- List of categories created with their folder names
- Sample of files in each category
- Any uncategorized files

## Custom Rules

Custom rules allow you to define your own categorization patterns for specific file types or naming conventions.

### Accessing Custom Rules

Click the "Custom Rules" button in the main window to open the Custom Rules dialog.

### Creating a Custom Rule

In the Custom Rules dialog:
1. Enter a name for your rule (e.g., "Python Files")
2. Specify the pattern to match (see pattern types below)
3. Enter the target folder name where matching files should be placed
4. Add a description (optional)
5. Click "Add Rule"

### Pattern Types

The following pattern types are supported:
- **Extension**: `.pdf`, `.jpg`, `.docx` (matches files with the specified extension)
- **Wildcard Suffix**: `*.jpg`, `*.backup` (matches files ending with the specified suffix)
- **Wildcard Prefix**: `report_*`, `backup_*` (matches files starting with the specified prefix)
- **Contains**: `contains:invoice`, `contains:report` (matches files containing the specified text)

### Getting Rule Suggestions

The application can analyze your files and suggest custom rules:
1. Select a directory in the main window
2. Open the Custom Rules dialog
3. Click "Get Rule Suggestions"
4. Review the suggested rules and add the ones you find useful

## Reverting Changes

If you're not satisfied with the categorization results, you can revert to the original file organization:

1. Click the "Revert to Original" button in the main window
2. Confirm the revert operation when prompted
3. The application will restore files to their original locations using the backup

## Troubleshooting

### API Key Issues

If you encounter errors related to the Groq API key:
1. Verify that your API key is correct
2. Check that the `.env` file exists in the application directory
3. Ensure the API key is properly formatted in the `.env` file
4. Try passing the API key directly as a command-line argument

### Application Not Starting

If the application fails to start:
1. Verify that Python 3.8 or higher is installed
2. Check that all dependencies are installed:
   ```
   pip install groq python-dotenv customtkinter
   ```
3. Try running the application from the command line to see any error messages

### Sorting Issues

If files are not being categorized as expected:
1. Ensure you have a stable internet connection for API calls
2. Check that the Groq API key is valid
3. Try using custom rules for more specific categorization

## FAQ

### Q: How does the multi-agent approach work?
A: The application uses multiple specialized agents to handle different aspects of file organization:
   - A categorization agent that analyzes file types and patterns
   - A backup agent that manages file backups and restoration
   - A rules agent that applies custom categorization rules
   - A coordination agent that orchestrates the overall process

### Q: Is my data sent to external servers?
A: The application only sends file metadata (names, extensions, sizes) to the Groq API for analysis. The actual file contents remain on your computer.

### Q: Can I customize the categorization beyond the provided options?
A: Yes, you can create custom rules with specific patterns to categorize files exactly as you need.

### Q: What happens if I close the application during sorting?
A: The application creates a backup before sorting, so you can always revert to the original organization if the process is interrupted.

### Q: Can I use this application without an internet connection?
A: The intelligent categorization requires the Groq API, which needs an internet connection. However, custom rules will still work offline once defined.

### Q: How can I contribute to the project?
A: The project is open-source under the MIT license. You can contribute by submitting pull requests on GitHub.

---

For additional support or to report issues, please visit the project repository or contact the developers.
