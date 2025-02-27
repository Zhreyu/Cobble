# Cobble 
Categorical Organization of your  Bubble by Brief Language


## Project Structure

```
AutoSort/
├── src/
│   ├── models/
│   │   └── rule.py                    # Rule data model
│   ├── context/
│   │   └── file_organizer_context.py  # Context management
│   ├── services/
│   │   └── file_organizer.py          # Core organization logic
│   └── utils/
│       └── menu.py                    # Menu handling utilities
├── main.py                            # Entry point
├── create_test.py                     # Test file generator
└── README.md                          # Documentation
```

## Requirements

- Python 3.8+
- Groq API key for AI-powered categorization

## Installation

1. Clone the repository:
```bash
git clone https://github.com/zhreyu/cobble.git
cd AutoSort
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your Groq API key:
```bash
export GROQ_API_KEY=your_api_key_here
```

## Usage

1. Run the file organizer:
```bash
python main.py /path/to/directory
```

2. Use the interactive menu to:
   - Start file organization with AI suggestions
   - Add custom organization rules
   - View and manage existing rules
   - Revert file organization if needed

### Example Rules

You can create custom rules like:
- "Put all PDFs with 'Biology' in them into Academic/Biology"
- "Move all Excel files to Business/Spreadsheets"
- "Store programming files in Code/Python"


## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Last Updated

2025-02-28


## Phase 0: Define Requirements and Architecture [DONE]

**Goal**: Establish the high-level design decisions and technology stack.

1. **High-Level Feature Breakdown**
    
    - **CLI-based file sorting** with two modes:
        1. **Auto-sort** using LLM suggestions (based on file content and/or metadata).
        2. **Manual (prompt-based) sorting** where the user can specify how to sort.
    - **Confirm changes** before performing moves, with an option to override or refine suggestions.
    - **Context-based sorting** by reading file content (e.g., for `.pdf` files, read up to ~500 words to glean context).
    - **File triaging** by labeling or tagging files with potential categories (e.g., “LectureNotes,” “Assignment,” “Personal,” “Images,” “Music,” etc.).
    - **Interactive chat** with the LLM to adjust categories mid-flow.
    - **Basic logging** to see which files were moved and where.
2. **Decide Tech Stack**
    
    - **Language(s)**:
        - Python for the CLI, LLM integration, and content parsing.
        - C# for later GUI if desired (or continue in Python if you want cross-platform GUI libraries).
    - **LLM Integration**: Ollama (local usage of Llama variants).
        - **Python wrapper** or HTTP-based (depending on how Ollama is set up).
    - **Data Storage**:
        - Use a lightweight local store or simply keep it ephemeral at first.
        - Later, you might integrate a small local database (SQLite) if needed for metadata.
3. **Architecture Overview**
    
    - **FileScanner**: Responsible for scanning a given folder and listing all files.
    - **ContentExtractor**: Retrieves partial file content (e.g., up to 500 words for PDFs/doc/docx).
    - **LLMClassifier**: Communicates with Ollama to get classification suggestions.
    - **UserInteraction**: CLI logic for prompting the user about each step.
    - **FileOrganizer**: Moves/renames files based on final decisions.

---

## Phase 1: Basic CLI Tool (Manual Sorting, No LLM) [DONE]

**Goal**: Build a minimal CLI that can scan files in a folder and move them based on user prompts.



---

## Phase 2: Integrate LLM for Auto-Suggested Labels [DONE]

**Goal**: Integrate Groq to get auto-suggested categories for files.

---

## Phase 3: Interactive Chat Refinements & Custom Prompts [DONE]

## Phase 4: Polishing and Advanced Features [TODO]


## Phase 5: Adding a Minimal GUI (Optional Early Beta

**Goal**: Start bridging from CLI to a basic GUI for improved user experience.



## Phase 6: Polishing and Advanced Features

**Goal**: Turn the prototype into a fully functional application with advanced controls and better performance.

1. **Advanced Rule System**
    
    - Add a rule editor in the GUI, where advanced users can define “if file content includes X, move to folder Y.”
    - Provide scheduling or watchers, so the app can auto-sort periodically.
2. **Performance Optimization**
    
    - Optimize PDF reading (maybe partial read or text extraction only once).
    - Cache LLM results to avoid repeated calls.
    - Consider concurrency or parallel processing if the dataset is large.
3. **Refined LLM Prompts**
    
    - Tweak system prompts to yield more accurate or domain-specific suggestions.
    - Possibly train or fine-tune an LLM (if feasible) to better recognize user’s domain-specific keywords.
4. **Cross-Platform Packaging**
    
    - Package into an executable for Windows/Mac/Linux.
    - If you’re using Python, tools like PyInstaller or Briefcase might help.
    - If you’re using C#, consider a self-contained .NET deployment.
5. **Security & Privacy Considerations**
    
    - If reading sensitive documents, ensure local LLM usage or encryption for data in transit.
    - Provide disclaimers about scanning file contents.
6. **User Documentation & Onboarding**
    
    - Provide an in-app tutorial or help pages.
    - Make sure error messages are user-friendly.

---

## Summary of the Overall Flow

1. **CLI Foundation**: Start simple—list files, move them on user command.
2. **LLM Integration**: Add content reading and classification via Ollama.
3. **Interactive Chat**: Let the user refine categories through conversation with the LLM.
4. **Basic GUI**: Wrap the CLI logic with a UI for easier usage.
5. **Refinements**: Add advanced rule systems, optimize performance, and package for wide distribution.



































