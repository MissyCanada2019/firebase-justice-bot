/**
 * SmartDispute.ai - File Upload Functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the upload area
    initializeUpload();
    
    // Set up form submission
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleUploadFormSubmit);
    }
    
    // Set up case category selection behavior
    setupCategorySelection();
});

/**
 * Initialize the file upload functionality
 */
function initializeUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const fileList = document.getElementById('fileList');
    
    if (!uploadArea || !fileInput) return;
    
    // Handle drag and drop events
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('highlight');
    });
    
    uploadArea.addEventListener('dragleave', function() {
        uploadArea.classList.remove('highlight');
    });
    
    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('highlight');
        
        if (e.dataTransfer.files.length) {
            handleFiles(e.dataTransfer.files);
        }
    });
    
    // Handle click to upload
    uploadArea.addEventListener('click', function() {
        fileInput.click();
    });
    
    fileInput.addEventListener('change', function() {
        if (this.files.length) {
            handleFiles(this.files);
        }
    });
    
    // Handle file selection
    function handleFiles(files) {
        if (!fileList) return;
        
        // Clear file list if it's the first upload
        if (fileInput.files.length === 0) {
            fileList.innerHTML = '';
        }
        
        // Create a new FileList object since we can't modify the original
        const dataTransfer = new DataTransfer();
        
        // Add existing files
        for (let i = 0; i < fileInput.files.length; i++) {
            dataTransfer.items.add(fileInput.files[i]);
        }
        
        // Add new files
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const extension = file.name.split('.').pop().toLowerCase();
            
            // Check if file type is allowed
            const allowedExtensions = ['pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'];
            if (!allowedExtensions.includes(extension)) {
                showAlert(`File type .${extension} is not supported. Please upload PDF, images, or Word documents.`, 'danger');
                continue;
            }
            
            // Check file size (16MB max)
            if (file.size > 16 * 1024 * 1024) {
                showAlert(`File ${file.name} is too large. Maximum file size is 16MB.`, 'danger');
                continue;
            }
            
            // Add to data transfer object
            dataTransfer.items.add(file);
            
            // Create file list item
            createFileListItem(file);
        }
        
        // Update the file input
        fileInput.files = dataTransfer.files;
        
        // Show or hide the upload area instructions
        const instructions = uploadArea.querySelector('.upload-instructions');
        if (instructions) {
            instructions.style.display = fileInput.files.length ? 'none' : 'block';
        }
        
        // Enable the submit button if files are selected
        const submitButton = document.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = fileInput.files.length === 0;
        }
    }
    
    /**
     * Create a file list item
     * @param {File} file - The file to create an item for
     */
    function createFileListItem(file) {
        const item = document.createElement('div');
        item.className = 'file-item d-flex align-items-center p-2 mb-2 bg-dark rounded';
        
        // Determine file icon based on type
        let fileIcon = 'file-text';
        const extension = file.name.split('.').pop().toLowerCase();
        if (['jpg', 'jpeg', 'png'].includes(extension)) {
            fileIcon = 'image';
        } else if (extension === 'pdf') {
            fileIcon = 'file-pdf';
        } else if (['doc', 'docx'].includes(extension)) {
            fileIcon = 'file-word';
        }
        
        // Format file size
        const sizeInKB = file.size / 1024;
        let formattedSize = sizeInKB < 1024 ? 
            `${Math.round(sizeInKB * 10) / 10} KB` : 
            `${Math.round(sizeInKB / 102.4) / 10} MB`;
        
        item.innerHTML = `
            <div class="me-3">
                <i class="feather-${fileIcon} text-primary fs-4"></i>
            </div>
            <div class="flex-grow-1">
                <div class="text-truncate" style="max-width: 200px;" title="${file.name}">${file.name}</div>
                <small class="text-muted">${formattedSize}</small>
            </div>
            <button type="button" class="btn btn-sm btn-danger remove-file" data-filename="${file.name}">
                <i class="feather-x"></i>
            </button>
        `;
        
        // Add remove file event
        const removeButton = item.querySelector('.remove-file');
        removeButton.addEventListener('click', function() {
            removeFile(file.name);
            item.remove();
        });
        
        fileList.appendChild(item);
    }
    
    /**
     * Remove a file from the file input
     * @param {string} filename - Name of the file to remove
     */
    function removeFile(filename) {
        const dt = new DataTransfer();
        const files = fileInput.files;
        
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            if (file.name !== filename) {
                dt.items.add(file);
            }
        }
        
        fileInput.files = dt.files;
        
        // Show upload instructions if no files
        const instructions = uploadArea.querySelector('.upload-instructions');
        if (instructions) {
            instructions.style.display = fileInput.files.length ? 'none' : 'block';
        }
        
        // Disable submit button if no files
        const submitButton = document.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = fileInput.files.length === 0;
        }
    }
}

/**
 * Handle the upload form submission
 * @param {Event} e - Form submit event
 */
function handleUploadFormSubmit(e) {
    e.preventDefault();
    
    // Get form elements
    const titleInput = document.getElementById('caseTitle');
    const categorySelect = document.getElementById('caseCategory');
    const fileInput = document.getElementById('fileInput');
    
    // Validate form
    if (!titleInput.value.trim()) {
        showAlert('Please enter a case title.', 'danger');
        titleInput.focus();
        return;
    }
    
    if (!categorySelect.value) {
        showAlert('Please select a case category.', 'danger');
        categorySelect.focus();
        return;
    }
    
    if (fileInput.files.length === 0) {
        showAlert('Please upload at least one file.', 'danger');
        return;
    }
    
    // Show loading state
    const submitButton = document.querySelector('button[type="submit"]');
    const originalButtonText = submitButton.innerHTML;
    submitButton.disabled = true;
    submitButton.innerHTML = `
        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        Uploading...
    `;
    
    // Submit the form
    document.getElementById('uploadForm').submit();
}

/**
 * Display an alert message
 * @param {string} message - The message to display
 * @param {string} type - The alert type (success, danger, etc.)
 */
function showAlert(message, type = 'success') {
    const alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertContainer.appendChild(alert);
    
    // Auto dismiss after 5 seconds
    if (type === 'success') {
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 150);
        }, 5000);
    }
}

/**
 * Set up the case category selection behavior
 */
function setupCategorySelection() {
    const categorySelect = document.getElementById('caseCategory');
    const categoryInfo = document.getElementById('categoryInfo');
    
    if (!categorySelect || !categoryInfo) return;
    
    // Category descriptions
    const categories = {
        'landlord-tenant': {
            title: 'Landlord-Tenant Disputes',
            icon: 'home',
            description: 'Issues like evictions, maintenance problems, illegal rent increases, or landlord harassment.',
            examples: 'Mold in apartment, invalid eviction notice, rent deposit disputes.'
        },
        'credit': {
            title: 'Credit Report Errors',
            icon: 'credit-card',
            description: 'Disputes with credit bureaus about incorrect information on your credit report.',
            examples: 'Wrong accounts listed, incorrect payment history, identity theft issues.'
        },
        'human-rights': {
            title: 'Human Rights Complaints',
            icon: 'shield',
            description: 'Discrimination based on protected grounds like race, gender, disability, etc.',
            examples: 'Workplace discrimination, housing discrimination, service refusal.'
        },
        'small-claims': {
            title: 'Small Claims Court',
            icon: 'file-text',
            description: 'Civil disputes involving money or property up to $35,000 in value.',
            examples: 'Unpaid debts, property damage, breach of contract, consumer issues.'
        },
        'child-protection': {
            title: 'Child Protection',
            icon: 'users',
            description: 'Issues with Children\'s Aid Society (CAS) or child welfare agencies.',
            examples: 'Responding to CAS allegations, access to children in care, supervision orders.'
        },
        'police-misconduct': {
            title: 'Police Misconduct',
            icon: 'alert-circle',
            description: 'Complaints about police behavior or treatment.',
            examples: 'Excessive force, illegal search, improper detention, discrimination.'
        }
    };
    
    // Update info when category changes
    categorySelect.addEventListener('change', function() {
        const selectedCategory = this.value;
        
        if (selectedCategory && categories[selectedCategory]) {
            const category = categories[selectedCategory];
            
            categoryInfo.innerHTML = `
                <div class="card bg-dark border-0 shadow-sm mt-3">
                    <div class="card-body">
                        <h5 class="d-flex align-items-center">
                            <i class="feather-${category.icon} text-primary me-2"></i>
                            ${category.title}
                        </h5>
                        <p>${category.description}</p>
                        <div class="small text-muted">
                            <strong>Examples:</strong> ${category.examples}
                        </div>
                    </div>
                </div>
            `;
            categoryInfo.style.display = 'block';
        } else {
            categoryInfo.style.display = 'none';
        }
    });
}
