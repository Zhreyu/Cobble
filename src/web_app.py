"""
Web UI for File Sorter App

This module implements a web interface for the file sorting application using Flask.
"""

import os
import json
import threading
import time
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

from src.file_categorizer import FileCategorizer
from src.groq_agent import GroqAgent
from src.backup_system import BackupSystem

# Initialize Flask app
app = Flask(__name__, 
            static_folder='/home/ubuntu/file_sorter_app/web/static',
            template_folder='/home/ubuntu/file_sorter_app/web/templates')

# Initialize backend components
groq_agent = GroqAgent()
backup_system = BackupSystem()
file_categorizer = FileCategorizer(groq_agent, backup_system)

# Global variables to track state
current_directory = None
current_backup_id = None
sorting_in_progress = False
sorting_results = None
system_status = {
    "memory": "0%",
    "cpu": "0%",
    "network": "inactive"
}

# Directory for file uploads
UPLOAD_FOLDER = '/home/zhreyas/Documents/file_sorter_app/web/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files."""
    return send_from_directory(app.static_folder, path)

@app.route('/api/status')
def get_status():
    """Get the current system status."""
    global system_status
    
    # Update system status (in a real app, this would be more sophisticated)
    import psutil
    system_status = {
        "memory": f"{psutil.virtual_memory().percent}%",
        "cpu": f"{psutil.cpu_percent()}%",
        "network": "active" if sorting_in_progress else "inactive"
    }
    
    return jsonify({
        "system_status": system_status,
        "sorting_in_progress": sorting_in_progress,
        "current_directory": current_directory,
        "current_backup_id": current_backup_id
    })

@app.route('/api/upload', methods=['POST'])
def upload_files():
    """Handle file uploads."""
    global current_directory
    
    if 'files[]' not in request.files:
        return jsonify({"error": "No files part"}), 400
    
    files = request.files.getlist('files[]')
    if not files or files[0].filename == '':
        return jsonify({"error": "No files selected"}), 400
    
    # Clear upload directory
    for file in os.listdir(UPLOAD_FOLDER):
        os.remove(os.path.join(UPLOAD_FOLDER, file))
    
    # Save uploaded files
    for file in files:
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
    
    current_directory = UPLOAD_FOLDER
    
    return jsonify({
        "success": True,
        "message": f"Uploaded {len(files)} files",
        "files": [secure_filename(file.filename) for file in files]
    })

@app.route('/api/sort', methods=['POST'])
def sort_files():
    """Sort files in the current directory."""
    global sorting_in_progress, current_directory, current_backup_id, sorting_results
    
    if sorting_in_progress:
        return jsonify({"error": "Sorting already in progress"}), 400
    
    if not current_directory:
        return jsonify({"error": "No directory selected"}), 400
    
    # Start sorting in a separate thread
    sorting_in_progress = True
    threading.Thread(target=sort_files_thread).start()
    
    return jsonify({"success": True, "message": "Sorting started"})

def sort_files_thread():
    """Thread function for sorting files."""
    global sorting_in_progress, current_directory, current_backup_id, sorting_results
    
    try:
        # Scan directory
        files = file_categorizer.scan_directory(current_directory)
        if not files:
            sorting_results = {"error": "No files found in the selected directory"}
            sorting_in_progress = False
            return
        
        # Categorize files
        categorization = file_categorizer.categorize_files(current_directory)
        
        # Store backup ID
        if file_categorizer.last_backup_id:
            current_backup_id = file_categorizer.last_backup_id
        
        # Sort files
        summary = file_categorizer.sort_files(current_directory, categorization)
        
        # Store results
        sorting_results = {
            "categorization": categorization,
            "summary": summary
        }
    except Exception as e:
        sorting_results = {"error": str(e)}
    finally:
        sorting_in_progress = False

@app.route('/api/results')
def get_results():
    """Get the results of the sorting operation."""
    global sorting_results
    
    if sorting_results is None:
        return jsonify({"error": "No sorting results available"}), 404
    
    return jsonify(sorting_results)

@app.route('/api/revert', methods=['POST'])
def revert_to_original():
    """Revert files to their original organization."""
    global current_backup_id, sorting_in_progress
    
    if sorting_in_progress:
        return jsonify({"error": "Sorting in progress, cannot revert"}), 400
    
    if not current_backup_id:
        return jsonify({"error": "No backup available to restore from"}), 400
    
    # Revert to original
    success = file_categorizer.revert_to_original(None, current_backup_id)
    
    if success:
        return jsonify({"success": True, "message": f"Successfully reverted to backup {current_backup_id}"})
    else:
        return jsonify({"error": f"Failed to revert to backup {current_backup_id}"}), 500

@app.route('/api/rules', methods=['GET'])
def get_rules():
    """Get all custom rules."""
    rules = file_categorizer.get_custom_rules()
    return jsonify({"rules": rules})

@app.route('/api/rules', methods=['POST'])
def add_rule():
    """Add a custom rule."""
    data = request.json
    
    if not data or not all(key in data for key in ["name", "pattern", "target_folder"]):
        return jsonify({"error": "Missing required fields"}), 400
    
    rule = {
        "name": data["name"],
        "pattern": data["pattern"],
        "target_folder": data["target_folder"],
        "description": data.get("description", "")
    }
    
    success = file_categorizer.add_custom_rule(rule)
    
    if success:
        return jsonify({"success": True, "message": f"Rule '{rule['name']}' added successfully"})
    else:
        return jsonify({"error": "Failed to add rule"}), 500

@app.route('/api/rules/<rule_name>', methods=['DELETE'])
def delete_rule(rule_name):
    """Delete a custom rule."""
    success = file_categorizer.remove_custom_rule(rule_name)
    
    if success:
        return jsonify({"success": True, "message": f"Rule '{rule_name}' deleted successfully"})
    else:
        return jsonify({"error": f"Rule '{rule_name}' not found"}), 404

@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    """Get rule suggestions based on files in the current directory."""
    global current_directory
    
    if not current_directory:
        return jsonify({"error": "No directory selected"}), 400
    
    try:
        # Scan directory
        files = file_categorizer.scan_directory(current_directory)
        if not files:
            return jsonify({"error": "No files found in the selected directory"}), 404
        
        # Get suggestions
        suggestions = file_categorizer.groq_agent.get_custom_rule_suggestions(files)
        
        return jsonify(suggestions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def run_web_app(host='0.0.0.0', port=5000, debug=False):
    """Run the Flask web application."""
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_web_app()
