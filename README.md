# Cobble
Categorical Organization of your  Bubble by Brief Language

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

1. **Scan Directory & List Files**
    
    - Implement a basic Python script that:
        - Takes a folder path as an argument.
        - Lists all the files (recursively or non-recursively, based on user choice).
        - Displays them in a simple menu.
2. **Prompt User for Destination**
    
    - For each file, ask the user: “Where do you want to move this file?”
    - The user can skip, rename, or specify a subfolder (e.g., `Lectures`, `Music`, etc.).
3. **Confirm Moves**
    
    - Summarize the moves that the user requested.
    - Offer a final “Proceed? (Y/N)” step before actually moving files.
4. **Implement Move Logic**
    
    - If user says “Yes,” create the necessary subfolders and move the files.
    - Log the outcomes.
5. **Testing & Validation**
    
    - Test with a small set of folders.
    - Handle edge cases (e.g., file name collisions, read-only files).

At the end of Phase 1, you have a working CLI that manually sorts files according to user input.

---

## Phase 2: Integrate LLM for Auto-Suggested Labels

**Goal**: Use Ollama to classify files based on content or metadata, providing category suggestions automatically.

1. **LLM Setup**
    
    - Confirm Ollama is installed and accessible from Python.
    - Write a small Python function `get_llm_prediction(file_content)` that sends file content to Ollama and returns a suggested category.
2. **Content Extraction**
    
    - Implement file-content extraction for common file types:
        - **Text/Markdown**: straightforward reading.
        - **PDF**: use a library like `PyPDF2` (or similar) to read up to 500 words.
        - **Docx**: use `python-docx` or a similar library.
    - Decide if you want to limit how much you read from each file to keep performance manageable.
3. **Auto-Sort Logic**
    
    - For each file, do the following:
        1. Extract up to 500 words.
        2. Send to LLM with a prompt like:
            
            yaml
            
            Copy code
            
            `You are a file sorter. Based on the content below, suggest a category from the following set: [LectureNotes, Assignment, Personal, ...]. Content:  --- {extracted content} ---` 
            
        3. Receive a suggestion (e.g., “LectureNotes”).
        4. Display it to the user along with a confidence measure if possible.
4. **User Validation & Prompt Refinement**
    
    - After receiving the LLM suggestion, allow the user to:
        - Accept the suggestion.
        - Override the suggestion manually.
        - Provide additional context to the LLM (e.g., “Actually, this is old biology homework.”).
5. **Confirmation & Moves**
    
    - Same as in Phase 1: Summarize the final decisions before actually moving the files.
    - If user wants to tweak some categories mid-flow, they can do so.
6. **Testing & Optimization**
    
    - Test with varied file types and larger sets of data.
    - Watch out for performance bottlenecks in content extraction or LLM calls.
    - Possibly cache the extracted content or LLM outputs to avoid repeated calls if the user re-runs the process.

At the end of Phase 2, you have an _augmented CLI_ that leverages an LLM to offer auto-sorting suggestions based on file content.

---

## Phase 3: Interactive Chat Refinements & Custom Prompts [IN PROCESS]

**Goal**: Allow the user to have a conversation-like interaction with the LLM for advanced sorting logic.

1. **Contextual Chat Flow**
    
    - Instead of a single prompt–response cycle per file, maintain an ongoing conversation with the LLM.
    - The user can type instructions like: “From now on, treat anything mentioning ‘Biology’ as LectureNotes.”
2. **User Scripting or Bulk Commands**
    
    - Let users specify advanced rules mid-run, e.g., “All PDFs created between 2021-05-01 and 2021-05-30 are personal receipts.”
    - This might involve the LLM interpreting these instructions in a standardized way and applying them to the file list.
3. **Confirmation UI**
    
    - After these advanced instructions, the system can produce an updated suggestion for each file.
    - The user then can confirm or override.
4. **Caching & Metadata Management**
    
    - Possibly store user-defined rules or LLM conversation context in a local file or DB for re-use across sessions.
5. **Validation & Testing**
    
    - Test for corner cases where user instructions conflict with one another.
    - Ensure the conversation remains stable and that the LLM doesn’t forget earlier instructions (maintain context).

At the end of Phase 3, the CLI has a _robust interactive chat_ with dynamic instructions for file sorting.

---

## Phase 4: Adding a Minimal GUI (Optional Early Beta)

**Goal**: Start bridging from CLI to a basic GUI for improved user experience. (If your friend is a C# developer, you can build a .NET WPF or WinForms front-end. Or you could use Python frameworks like PySide/PyQt.)

1. **Design a Simple GUI**
    
    - A window that allows the user to select the folder path.
    - A text area or list box to display the discovered files.
    - Buttons or text fields for user inputs.
2. **Integration with CLI Logic**
    
    - Reuse the existing Python logic for scanning, LLM queries, etc.
    - Communicate with the Python backend via standard input/output or a local REST API (easiest might be to embed Python in a C# solution or vice versa, or keep them separate with a small HTTP layer).
3. **Real-time Feedback**
    
    - Display the LLM-suggested category in the UI.
    - Allow the user to manually override with a dropdown or text input.
    - Summaries and confirmations.
4. **Logging & Error Handling**
    
    - Provide a status area to log any errors (file not found, permission issues, etc.).

At the end of Phase 4, you have a _basic graphical interface_ that orchestrates your Python-based backend for file sorting.

---

## Phase 5: Polishing and Advanced Features

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
