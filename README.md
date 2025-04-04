# Smart File Sorter - README

## Overview
Smart File Sorter is a multi-agent application that intelligently categorizes and organizes files in a selected folder. The application uses the Groq API to analyze file types and patterns, creating a logical folder structure based on file content and characteristics.

## Features
- **Intelligent File Categorization**: Uses AI to analyze and categorize files
- **Multi-Agent Architecture**: Employs multiple specialized agents for different aspects of file organization
- **Custom Rules**: Create and manage custom rules for file categorization
- **Backup System**: Automatically backs up files before sorting, allowing easy reversion
- **Dual Interfaces**: Available as both desktop application and web interface

## Installation

### Prerequisites
- Python 3.8 or higher
- Groq API key (provided: `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`)

### Option 1: Using the Installer Script (Recommended)
1. Download the application package
2. Run the installer script:
   ```
   python install.py
   ```
3. Follow the on-screen instructions

### Option 2: Manual Installation
1. Clone or download the repository
2. Install dependencies:
   ```
   pip install groq python-dotenv customtkinter flask
   ```
3. Create a `.env` file with your Groq API key:
   ```
   GROQ_API_KEY=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
   ```

## Usage

### Desktop Application
Run the desktop application with:
```
python main.py
```

### Web Interface
Run the web interface with:
```
python web_ui.py
```
Then access the application in your browser at `http://localhost:5000`

## Application Structure
- `src/backup_system.py`: Handles file backups and restoration
- `src/groq_agent.py`: Manages Groq API integration for intelligent categorization
- `src/file_categorizer.py`: Core logic for file categorization and sorting
- `src/app.py`: Desktop user interface using customtkinter
- `src/web_app.py`: Web interface using Flask
- `main.py`: Entry point for desktop application
- `web_ui.py`: Entry point for web interface
- `install.py`: Installation script

## Custom Rules
You can create custom rules to categorize files based on specific patterns:
- File extensions (e.g., `.pdf`, `.jpg`)
- Name patterns (e.g., `report_*`, `*_final`)
- Content patterns (e.g., `contains:invoice`)

## License
This project is licensed under the MIT License - see the LICENSE file for details.
