/**
 * Simple Upload Handler for SmartDispute.ai
 * Handles file selection and upload with evidence type categorization
 */

console.log('Simple upload handler loading...');

document.addEventListener('DOMContentLoaded', function() {
    // Get elements
    const fileInput = document.getElementById('simpleFileInput');
    const dropzone = document.getElementById('uploadDropzone');
    const browseBtn = document.getElementById('browseFilesBtn');
    const evidenceCards = document.querySelectorAll('.evidence-type-card');
    const evidenceTypeInput = document.getElementById('evidenceType');
    const filePreviewArea = document.getElementById('filePreviewArea');
    const fileList = document.getElementById('fileList');
    const uploadForm = document.getElementById('uploadForm');
    
    if (!fileInput || !dropzone) {
        console.log('Upload elements not found');
        return;
    }
    
    console.log('Upload elements found, setting up...');
    
    // Evidence type selection
    evidenceCards.forEach(card => {
        card.addEventListener('click', function() {
            console.log('Evidence card clicked, opening file browser for:', this.dataset.type);
            
            // Update evidence type
            evidenceTypeInput.value = this.dataset.type;
            
            // Update visual state
            evidenceCards.forEach(c => {
                c.classList.remove('active');
                c.style.border = '';
            });
            this.classList.add('active');
            this.style.border = '2px solid #28a745';
            
            // Trigger file browser - allow multiple selection
            fileInput.setAttribute('multiple', 'multiple');
            fileInput.click();
        });
    });
    
    // Browse button click
    if (browseBtn) {
        browseBtn.addEventListener('click', function(e) {
            console.log('Browse button clicked');
            e.preventDefault();
            fileInput.click();
        });
    }
    
    // Dropzone click
    dropzone.addEventListener('click', function(e) {
        console.log('Dropzone clicked');
        if (e.target === dropzone || e.target.closest('#uploadDropzone')) {
            fileInput.click();
        }
    });
    
    // Drag and drop
    dropzone.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.classList.add('drag-over');
    });
    
    dropzone.addEventListener('dragleave', function(e) {
        e.preventDefault();
        this.classList.remove('drag-over');
    });
    
    dropzone.addEventListener('drop', function(e) {
        e.preventDefault();
        this.classList.remove('drag-over');
        
        if (e.dataTransfer.files.length > 0) {
            console.log('Files dropped:', e.dataTransfer.files.length);
            
            // Add dropped files to our collection
            for (let i = 0; i < e.dataTransfer.files.length; i++) {
                const newFile = e.dataTransfer.files[i];
                // Check for duplicates based on name and size
                const isDuplicate = allSelectedFiles.some(existingFile => 
                    existingFile.name === newFile.name && existingFile.size === newFile.size
                );
                
                if (!isDuplicate) {
                    allSelectedFiles.push(newFile);
                }
            }
            
            // Update the file input with all selected files
            const dt = new DataTransfer();
            allSelectedFiles.forEach(file => dt.items.add(file));
            fileInput.files = dt.files;
            
            updateFilePreview();
            updateSubmitButton();
        }
    });
    
    // Store all selected files across multiple selections
    let allSelectedFiles = [];
    
    // File input change
    fileInput.addEventListener('change', function() {
        console.log('File input changed, files selected:', this.files.length);
        
        // Add new files to our collection
        for (let i = 0; i < this.files.length; i++) {
            const newFile = this.files[i];
            // Check for duplicates based on name and size
            const isDuplicate = allSelectedFiles.some(existingFile => 
                existingFile.name === newFile.name && existingFile.size === newFile.size
            );
            
            if (!isDuplicate) {
                allSelectedFiles.push(newFile);
            }
        }
        
        // Update the file input with all selected files
        const dt = new DataTransfer();
        allSelectedFiles.forEach(file => dt.items.add(file));
        this.files = dt.files;
        
        updateFilePreview();
        updateSubmitButton();
    });
    
    // Update file preview
    function updateFilePreview() {
        const files = fileInput.files;
        
        if (files.length === 0) {
            filePreviewArea.style.display = 'none';
            return;
        }
        
        console.log('Updating preview for', files.length, 'files');
        
        // Show preview area
        filePreviewArea.style.display = 'block';
        
        // Clear existing preview
        fileList.innerHTML = '';
        
        // Calculate total size
        let totalSize = 0;
        for (let i = 0; i < files.length; i++) {
            totalSize += files[i].size;
        }
        
        // Display files
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const fileElement = createFilePreview(file, i);
            fileList.appendChild(fileElement);
        }
        
        // Show summary
        const sizeInMB = (totalSize / (1024 * 1024)).toFixed(2);
        const summaryElement = document.createElement('div');
        summaryElement.className = 'col-12 mt-2';
        summaryElement.innerHTML = `
            <div class="alert alert-info">
                <strong>${files.length} files selected</strong> - Total size: ${sizeInMB} MB
                ${totalSize > 250 * 1024 * 1024 ? '<br><span class="text-danger">Warning: Total size exceeds 250MB limit</span>' : ''}
            </div>
        `;
        fileList.appendChild(summaryElement);
    }
    
    // Create file preview element
    function createFilePreview(file, index) {
        const col = document.createElement('div');
        col.className = 'col-md-6 col-lg-4';
        
        const sizeInKB = (file.size / 1024).toFixed(1);
        const fileType = getFileType(file.name);
        
        col.innerHTML = `
            <div class="card border-secondary">
                <div class="card-body p-2">
                    <div class="d-flex align-items-center">
                        <i class="fas ${getFileIcon(file.name)} fa-2x me-2 text-primary"></i>
                        <div class="flex-grow-1 min-width-0">
                            <div class="fw-bold text-truncate" title="${file.name}">${file.name}</div>
                            <small class="text-muted">${fileType} • ${sizeInKB} KB</small>
                        </div>
                        <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeFile(${index})">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        return col;
    }
    
    // Get file type
    function getFileType(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const types = {
            'pdf': 'PDF',
            'doc': 'Word',
            'docx': 'Word',
            'jpg': 'Image',
            'jpeg': 'Image',
            'png': 'Image',
            'txt': 'Text',
            'rtf': 'Rich Text',
            'xls': 'Excel',
            'xlsx': 'Excel'
        };
        return types[ext] || 'Document';
    }
    
    // Get file icon
    function getFileIcon(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const icons = {
            'pdf': 'fa-file-pdf',
            'doc': 'fa-file-word',
            'docx': 'fa-file-word',
            'jpg': 'fa-file-image',
            'jpeg': 'fa-file-image',
            'png': 'fa-file-image',
            'txt': 'fa-file-alt',
            'rtf': 'fa-file-alt',
            'xls': 'fa-file-excel',
            'xlsx': 'fa-file-excel'
        };
        return icons[ext] || 'fa-file';
    }
    
    // Global function to remove files
    window.removeFile = function(index) {
        // Remove file from our collection
        allSelectedFiles.splice(index, 1);
        
        // Update the file input
        const dt = new DataTransfer();
        allSelectedFiles.forEach(file => dt.items.add(file));
        fileInput.files = dt.files;
        
        updateFilePreview();
        updateSubmitButton();
    };
    
    // Clear all files
    window.clearAllFiles = function() {
        allSelectedFiles = [];
        fileInput.value = '';
        updateFilePreview();
        updateSubmitButton();
    };
    
    // Form submission validation
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            const files = fileInput.files;
            const caseTitle = document.getElementById('case_title').value.trim();
            const caseCategory = document.getElementById('case_category').value;
            
            if (!caseTitle) {
                e.preventDefault();
                alert('Please enter a case title');
                return;
            }
            
            if (!caseCategory) {
                e.preventDefault();
                alert('Please select a legal category');
                return;
            }
            
            if (files.length === 0) {
                e.preventDefault();
                alert('Please select at least one file to upload');
                return;
            }
            
            // Check total file size
            let totalSize = 0;
            for (let i = 0; i < files.length; i++) {
                totalSize += files[i].size;
            }
            
            if (totalSize > 250 * 1024 * 1024) {
                e.preventDefault();
                alert('Total file size exceeds 250MB limit. Please reduce the number of files or compress them.');
                return;
            }
            
            // Show loading state
            const submitBtn = uploadForm.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Uploading...';
            }
        });
    }
    
    // Update submit button based on file selection
    function updateSubmitButton() {
        const submitBtn = document.getElementById('submit-files');
        const submitBtnText = document.getElementById('submit-btn-text');
        const files = fileInput.files;
        
        if (submitBtn && submitBtnText) {
            if (files.length > 0) {
                submitBtnText.textContent = `Analyze ${files.length} File${files.length > 1 ? 's' : ''}`;
                submitBtn.className = 'btn btn-success btn-lg';
            } else {
                submitBtnText.textContent = 'Browse Files to Get Started';
                submitBtn.className = 'btn btn-charter btn-lg';
            }
        }
    }
    
    console.log('Simple upload handler ready');
});

// Add CSS for drag over effect
const style = document.createElement('style');
style.textContent = `
    .upload-dropzone.drag-over {
        border-color: #0d6efd !important;
        background-color: rgba(13, 110, 253, 0.1) !important;
    }
    
    .evidence-type-card.active {
        border-color: #28a745 !important;
        background-color: rgba(40, 167, 69, 0.1) !important;
    }
    
    .evidence-type-card {
        transition: all 0.2s ease;
    }
    
    .evidence-type-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .min-width-0 {
        min-width: 0;
    }
`;
document.head.appendChild(style);