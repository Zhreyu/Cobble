// Main JavaScript for COBBLE File Sorter Web UI

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const searchInput = document.getElementById('search-input');
    const uploadBtn = document.getElementById('upload-btn');
    const fileUpload = document.getElementById('file-upload');
    const sortBtn = document.getElementById('sort-btn');
    const revertBtn = document.getElementById('revert-btn');
    const rulesBtn = document.getElementById('rules-btn');
    const resultsContent = document.getElementById('results-content');
    const backupId = document.getElementById('backup-id');
    const statusIndicator = document.getElementById('status-indicator');
    const memoryStatus = document.getElementById('memory-status');
    const cpuStatus = document.getElementById('cpu-status');
    const networkStatus = document.getElementById('network-status');
    
    // Modal Elements
    const rulesModal = document.getElementById('rules-modal');
    const suggestionsModal = document.getElementById('suggestions-modal');
    const rulesList = document.getElementById('rules-list');
    const suggestionsList = document.getElementById('suggestions-list');
    const suggestionsExplanation = document.getElementById('suggestions-explanation');
    const closeBtns = document.querySelectorAll('.close');
    
    // Form Elements
    const ruleName = document.getElementById('rule-name');
    const rulePattern = document.getElementById('rule-pattern');
    const ruleFolder = document.getElementById('rule-folder');
    const ruleDescription = document.getElementById('rule-description');
    const addRuleBtn = document.getElementById('add-rule-btn');
    const getSuggestionsBtn = document.getElementById('get-suggestions-btn');
    
    // State
    let sortingInProgress = false;
    let filesUploaded = false;
    let currentFiles = [];
    
    // Initialize
    updateStatus();
    loadRules();
    
    // Event Listeners
    uploadBtn.addEventListener('click', function() {
        fileUpload.click();
    });
    
    fileUpload.addEventListener('change', function() {
        if (fileUpload.files.length > 0) {
            uploadFiles(fileUpload.files);
        }
    });
    
    sortBtn.addEventListener('click', function() {
        if (!filesUploaded) {
            showMessage('Please upload files first', 'error');
            return;
        }
        
        if (sortingInProgress) {
            showMessage('Sorting already in progress', 'error');
            return;
        }
        
        sortFiles();
    });
    
    revertBtn.addEventListener('click', function() {
        if (sortingInProgress) {
            showMessage('Cannot revert while sorting is in progress', 'error');
            return;
        }
        
        revertToOriginal();
    });
    
    rulesBtn.addEventListener('click', function() {
        loadRules();
        rulesModal.style.display = 'block';
    });
    
    addRuleBtn.addEventListener('click', function() {
        addRule();
    });
    
    getSuggestionsBtn.addEventListener('click', function() {
        if (!filesUploaded) {
            showMessage('Please upload files first', 'error');
            return;
        }
        
        getRuleSuggestions();
    });
    
    // Close modals
    closeBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            rulesModal.style.display = 'none';
            suggestionsModal.style.display = 'none';
        });
    });
    
    window.addEventListener('click', function(event) {
        if (event.target === rulesModal) {
            rulesModal.style.display = 'none';
        }
        if (event.target === suggestionsModal) {
            suggestionsModal.style.display = 'none';
        }
    });
    
    // Search functionality
    searchInput.addEventListener('input', function() {
        const searchTerm = searchInput.value.toLowerCase();
        const fileItems = document.querySelectorAll('.file-item');
        
        fileItems.forEach(function(item) {
            const fileName = item.textContent.toLowerCase();
            if (fileName.includes(searchTerm)) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    });
    
    // Functions
    function updateStatus() {
        fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                memoryStatus.textContent = data.system_status.memory;
                cpuStatus.textContent = data.system_status.cpu;
                networkStatus.textContent = data.system_status.network;
                
                if (data.current_backup_id) {
                    backupId.textContent = data.current_backup_id;
                }
                
                sortingInProgress = data.sorting_in_progress;
                
                if (sortingInProgress) {
                    statusIndicator.classList.add('active');
                    sortBtn.disabled = true;
                    revertBtn.disabled = true;
                } else {
                    statusIndicator.classList.remove('active');
                    sortBtn.disabled = false;
                    revertBtn.disabled = false;
                }
                
                // If sorting was in progress and now it's done, get results
                if (sortingInProgress === false && resultsContent.querySelector('.loading')) {
                    getResults();
                }
            })
            .catch(error => {
                console.error('Error fetching status:', error);
            });
        
        // Update status every 2 seconds
        setTimeout(updateStatus, 2000);
    }
    
    function uploadFiles(files) {
        const formData = new FormData();
        
        for (let i = 0; i < files.length; i++) {
            formData.append('files[]', files[i]);
        }
        
        // Show loading
        resultsContent.innerHTML = '<div class="loading"></div>';
        
        fetch('/api/upload', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    filesUploaded = true;
                    currentFiles = data.files;
                    showMessage(`Uploaded ${data.files.length} files`, 'success');
                    
                    // Display uploaded files
                    displayUploadedFiles(data.files);
                } else {
                    showMessage(data.error, 'error');
                }
            })
            .catch(error => {
                console.error('Error uploading files:', error);
                showMessage('Error uploading files', 'error');
            });
    }
    
    function displayUploadedFiles(files) {
        resultsContent.innerHTML = '';
        
        const category = document.createElement('div');
        category.className = 'category';
        
        const header = document.createElement('div');
        header.className = 'category-header';
        
        const name = document.createElement('div');
        name.className = 'category-name';
        name.textContent = 'Uploaded Files';
        
        const count = document.createElement('div');
        count.className = 'category-count';
        count.textContent = `${files.length} files`;
        
        header.appendChild(name);
        header.appendChild(count);
        
        const fileList = document.createElement('div');
        fileList.className = 'file-list';
        
        files.forEach(file => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            
            const icon = document.createElement('i');
            icon.className = `fas fa-file file-icon ${getFileIconClass(file)}`;
            
            const fileName = document.createElement('span');
            fileName.textContent = file;
            
            fileItem.appendChild(icon);
            fileItem.appendChild(fileName);
            fileList.appendChild(fileItem);
        });
        
        category.appendChild(header);
        category.appendChild(fileList);
        resultsContent.appendChild(category);
    }
    
    function getFileIconClass(fileName) {
        const extension = fileName.split('.').pop().toLowerCase();
        
        const iconMap = {
            // Documents
            'pdf': 'document',
            'doc': 'document',
            'docx': 'document',
            'txt': 'document',
            'rtf': 'document',
            
            // Images
            'jpg': 'image',
            'jpeg': 'image',
            'png': 'image',
            'gif': 'image',
            'bmp': 'image',
            'svg': 'image',
            
            // Videos
            'mp4': 'video',
            'avi': 'video',
            'mov': 'video',
            'wmv': 'video',
            'mkv': 'video',
            
            // Audio
            'mp3': 'audio',
            'wav': 'audio',
            'ogg': 'audio',
            'flac': 'audio',
            
            // Archives
            'zip': 'archive',
            'rar': 'archive',
            'tar': 'archive',
            'gz': 'archive',
            '7z': 'archive',
            
            // Code
            'py': 'code',
            'js': 'code',
            'html': 'code',
            'css': 'code',
            'java': 'code',
            'cpp': 'code',
            'c': 'code',
            'php': 'code',
            'json': 'code',
            'xml': 'code'
        };
        
        return iconMap[extension] || 'unknown';
    }
    
    function sortFiles() {
        // Show loading
        resultsContent.innerHTML = '<div class="loading"></div>';
        sortingInProgress = true;
        
        fetch('/api/sort', {
            method: 'POST'
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage('Sorting started', 'success');
                } else {
                    showMessage(data.error, 'error');
                    resultsContent.innerHTML = '<div class="placeholder-text">Error starting sorting process</div>';
                }
            })
            .catch(error => {
                console.error('Error starting sort:', error);
                showMessage('Error starting sorting process', 'error');
                resultsContent.innerHTML = '<div class="placeholder-text">Error starting sorting process</div>';
            });
    }
    
    function getResults() {
        fetch('/api/results')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showMessage(data.error, 'error');
                    resultsContent.innerHTML = '<div class="placeholder-text">Error retrieving results</div>';
                    return;
                }
                
                displayResults(data);
            })
            .catch(error => {
                console.error('Error getting results:', error);
                showMessage('Error retrieving results', 'error');
                resultsContent.innerHTML = '<div class="placeholder-text">Error retrieving results</div>';
            });
    }
    
    function displayResults(data) {
        resultsContent.innerHTML = '';
        
        // Summary
        const summary = document.createElement('div');
        summary.className = 'summary';
        summary.innerHTML = `
            <p>Files moved: ${data.summary.moved}</p>
            <p>Files skipped: ${data.summary.skipped}</p>
            <p>Errors: ${data.summary.errors}</p>
        `;
        resultsContent.appendChild(summary);
        
        // Categories
        data.categorization.categories.forEach(category => {
            const categoryDiv = document.createElement('div');
            categoryDiv.className = 'category';
            
            const header = document.createElement('div');
            header.className = 'category-header';
            
            const name = document.createElement('div');
            name.className = 'category-name';
            name.textContent = category.name;
            
            const count = document.createElement('div');
            count.className = 'category-count';
            count.textContent = `${category.files.length} files → ${category.suggested_folder}`;
            
            header.appendChild(name);
            header.appendChild(count);
            
            const fileList = document.createElement('div');
            fileList.className = 'file-list';
            
            category.files.forEach(file => {
                const fileName = file.split('/').pop();
                
                const fileItem = document.createElement('div');
                fileItem.className = 'file-item';
                
                const icon = document.createElement('i');
                icon.className = `fas fa-file file-icon ${getFileIconClass(fileName)}`;
                
                const fileNameSpan = document.createElement('span');
                fileNameSpan.textContent = fileName;
                
                fileItem.appendChild(icon);
                fileItem.appendChild(fileNameSpan);
                fileList.appendChild(fileItem);
            });
            
            categoryDiv.appendChild(header);
            categoryDiv.appendChild(fileList);
            resultsContent.appendChild(categoryDiv);
        });
        
        // Uncategorized files
        if (data.categorization.uncategorized && data.categorization.uncategorized.length > 0) {
            const uncategorizedDiv = document.createElement('div');
            uncategorizedDiv.className = 'category';
            
            const header = document.createElement('div');
            header.className = 'category-header';
            
            const name = document.createElement('div');
            name.className = 'category-name';
            name.textContent = 'Uncategorized';
            
            const count = document.createElement('div');
            count.className = 'category-count';
            count.textContent = `${data.categorization.uncategorized.length} files`;
            
            header.appendChild(name);
            header.appendChild(count);
            
            const fileList = document.createElement('div');
            fileList.className = 'file-list';
            
            data.categorization.uncategorized.forEach(file => {
                const fileName = file.split('/').pop();
                
                const fileItem = document.createElement('div');
                fileItem.className = 'file-item';
                
                const icon = document.createElement('i');
                icon.className = `fas fa-file file-icon unknown`;
                
                const fileNameSpan = document.createElement('span');
                fileNameSpan.textContent = fileName;
                
                fileItem.appendChild(icon);
                fileItem.appendChild(fileNameSpan);
                fileList.appendChild(fileItem);
            });
            
            uncategorizedDiv.appendChild(header);
            uncategorizedDiv.appendChild(fileList);
            resultsContent.appendChild(uncategorizedDiv);
        }
    }
    
    function revertToOriginal() {
        if (!backupId.textContent || backupId.textContent === 'None') {
            showMessage('No backup available to restore from', 'error');
            return;
        }
        
        // Confirm revert
        if (!confirm('Are you sure you want to revert to the original file organization?')) {
            return;
        }
        
        // Show loading
        resultsContent.innerHTML = '<div class="loading"></div>';
        
        fetch('/api/revert', {
            method: 'POST'
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage(data.message, 'success');
                    resultsContent.innerHTML = '<div class="placeholder-text">Files have been restored to their original organization</div>';
                } else {
                    showMessage(data.error, 'error');
                    resultsContent.innerHTML = '<div class="placeholder-text">Error reverting to original organization</div>';
                }
            })
            .catch(error => {
                console.error('Error reverting:', error);
                showMessage('Error reverting to original organization', 'error');
                resultsContent.innerHTML = '<div class="placeholder-text">Error reverting to original organization</div>';
            });
    }
    
    function loadRules() {
        fetch('/api/rules')
            .then(response => response.json())
            .then(data => {
                displayRules(data.rules);
            })
            .catch(error => {
                console.error('Error loading rules:', error);
                showMessage('Error loading rules', 'error');
            });
    }
    
    function displayRules(rules) {
        rulesList.innerHTML = '';
        
        if (!rules || rules.length === 0) {
            rulesList.innerHTML = '<div class="placeholder-text">No custom rules defined yet</div>';
            return;
        }
        
        rules.forEach(rule => {
            const ruleItem = document.createElement('div');
            ruleItem.className = 'rule-item';
            
            const header = document.createElement('div');
            header.className = 'rule-header';
            
            const name = document.createElement('div');
            name.className = 'rule-name';
            name.textContent = rule.name;
            
            const deleteBtn = document.createElement('div');
            deleteBtn.className = 'delete-rule';
            deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
            deleteBtn.addEventListener('click', function() {
                deleteRule(rule.name);
            });
            
            header.appendChild(name);
            header.appendChild(deleteBtn);
            
            const details = document.createElement('div');
            details.className = 'rule-details';
            
            details.innerHTML = `
                <div class="rule-detail">Pattern: ${rule.pattern}</div>
                <div class="rule-detail">Target Folder: ${rule.target_folder}</div>
                ${rule.description ? `<div class="rule-detail">Description: ${rule.description}</div>` : ''}
            `;
            
            ruleItem.appendChild(header);
            ruleItem.appendChild(details);
            rulesList.appendChild(ruleItem);
        });
    }
    
    function addRule() {
        const name = ruleName.value.trim();
        const pattern = rulePattern.value.trim();
        const folder = ruleFolder.value.trim();
        const description = ruleDescription.value.trim();
        
        if (!name || !pattern || !folder) {
            showMessage('Rule name, pattern, and target folder are required', 'error');
            return;
        }
        
        const rule = {
            name: name,
            pattern: pattern,
            target_folder: folder,
            description: description
        };
        
        fetch('/api/rules', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(rule)
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage(data.message, 'success');
                    
                    // Clear form
                    ruleName.value = '';
                    rulePattern.value = '';
                    ruleFolder.value = '';
                    ruleDescription.value = '';
                    
                    // Reload rules
                    loadRules();
                } else {
                    showMessage(data.error, 'error');
                }
            })
            .catch(error => {
                console.error('Error adding rule:', error);
                showMessage('Error adding rule', 'error');
            });
    }
    
    function deleteRule(ruleName) {
        if (!confirm(`Are you sure you want to delete the rule '${ruleName}'?`)) {
            return;
        }
        
        fetch(`/api/rules/${encodeURIComponent(ruleName)}`, {
            method: 'DELETE'
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage(data.message, 'success');
                    
                    // Reload rules
                    loadRules();
                } else {
                    showMessage(data.error, 'error');
                }
            })
            .catch(error => {
                console.error('Error deleting rule:', error);
                showMessage('Error deleting rule', 'error');
            });
    }
    
    function getRuleSuggestions() {
        // Show loading in suggestions modal
        suggestionsModal.style.display = 'block';
        suggestionsList.innerHTML = '<div class="loading"></div>';
        suggestionsExplanation.innerHTML = '';
        
        fetch('/api/suggestions')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showMessage(data.error, 'error');
                    suggestionsList.innerHTML = '<div class="placeholder-text">Error getting suggestions</div>';
                    return;
                }
                
                displaySuggestions(data);
            })
            .catch(error => {
                console.error('Error getting suggestions:', error);
                showMessage('Error getting suggestions', 'error');
                suggestionsList.innerHTML = '<div class="placeholder-text">Error getting suggestions</div>';
            });
    }
    
    function displaySuggestions(data) {
        suggestionsList.innerHTML = '';
        
        if (data.explanation) {
            suggestionsExplanation.textContent = data.explanation;
        }
        
        if (!data.suggested_rules || data.suggested_rules.length === 0) {
            suggestionsList.innerHTML = '<div class="placeholder-text">No rule suggestions available</div>';
            return;
        }
        
        data.suggested_rules.forEach(rule => {
            const suggestionItem = document.createElement('div');
            suggestionItem.className = 'suggestion-item';
            
            const header = document.createElement('div');
            header.className = 'suggestion-header';
            
            const name = document.createElement('div');
            name.className = 'suggestion-name';
            name.textContent = rule.name;
            
            const addBtn = document.createElement('div');
            addBtn.className = 'add-suggestion';
            addBtn.innerHTML = '<i class="fas fa-plus"></i> Add';
            addBtn.addEventListener('click', function() {
                addSuggestion(rule);
            });
            
            header.appendChild(name);
            header.appendChild(addBtn);
            
            const details = document.createElement('div');
            details.className = 'rule-details';
            
            details.innerHTML = `
                <div class="rule-detail">Pattern: ${rule.pattern}</div>
                <div class="rule-detail">Target Folder: ${rule.target_folder}</div>
                ${rule.description ? `<div class="rule-detail">Description: ${rule.description}</div>` : ''}
            `;
            
            suggestionItem.appendChild(header);
            suggestionItem.appendChild(details);
            suggestionsList.appendChild(suggestionItem);
        });
    }
    
    function addSuggestion(rule) {
        fetch('/api/rules', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(rule)
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage(data.message, 'success');
                    
                    // Reload rules
                    loadRules();
                } else {
                    showMessage(data.error, 'error');
                }
            })
            .catch(error => {
                console.error('Error adding suggestion:', error);
                showMessage('Error adding suggestion', 'error');
            });
    }
    
    function showMessage(message, type) {
        // Create message element
        const messageElement = document.createElement('div');
        messageElement.className = `message ${type}`;
        messageElement.textContent = message;
        
        // Add to body
        document.body.appendChild(messageElement);
        
        // Remove after 3 seconds
        setTimeout(function() {
            messageElement.classList.add('fade-out');
            setTimeout(function() {
                document.body.removeChild(messageElement);
            }, 500);
        }, 3000);
    }
});
