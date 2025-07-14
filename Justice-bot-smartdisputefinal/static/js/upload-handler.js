/**
 * Fixed Upload Handler for SmartDispute.ai
 * Handles file selection from device files app without syntax errors
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Upload handler initializing...');
    
    // Initialize upload functionality
    initializeUpload();
    
    function initializeUpload() {
        const fileInput = document.getElementById('simpleFileInput');
        const dropzone = document.getElementById('uploadDropzone');
        const filePreviewArea = document.getElementById('filePreviewArea');
        const fileList = document.getElementById('fileList');
        
        if (!fileInput || !dropzone) {
            console.error('Required upload elements not found');
            return;
        }
        
        console.log('Upload elements found, setting up handlers...');
        
        // File input change handler
        fileInput.addEventListener('change', function(e) {
            console.log('Files selected:', e.target.files.length);
            handleFileSelection(e.target.files);
        });
        
        // Browse button click handler
        const browseBtn = document.getElementById('browseFilesBtn');
        if (browseBtn) {
            browseBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                console.log('Browse button clicked, opening file picker...');
                fileInput.value = ''; // Clear previous selection
                fileInput.click();
            });
        }
        
        // Dropzone click handler (excluding button clicks)
        dropzone.addEventListener('click', function(e) {
            // Don't trigger if clicking the button
            if (e.target.id === 'browseFilesBtn' || e.target.closest('#browseFilesBtn')) {
                return;
            }
            e.preventDefault();
            e.stopPropagation();
            console.log('Dropzone clicked, opening file picker...');
            fileInput.value = ''; // Clear previous selection
            fileInput.click();
        });
        
        // Drag and drop handlers
        dropzone.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add('border-primary');
        });
        
        dropzone.addEventListener('dragleave', function(e) {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('border-primary');
        });
        
        dropzone.addEventListener('drop', function(e) {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('border-primary');
            
            const files = e.dataTransfer.files;
            console.log('Files dropped:', files.length);
            handleFileSelection(files);
        });
        
        function handleFileSelection(files) {
            if (files.length === 0) {
                console.log('No files selected');
                return;
            }
            
            console.log('Processing', files.length, 'files...');
            
            // Store files for form submission
            window.selectedFiles = Array.from(files);
            
            // Clear previous files
            fileList.innerHTML = '';
            
            // Process each file
            Array.from(files).forEach(function(file, index) {
                console.log('Processing file:', file.name, 'Size:', file.size);
                
                // Validate file
                if (!validateFile(file)) {
                    return;
                }
                
                // Create file preview
                createFilePreview(file, index);
            });
            
            // Show preview area
            if (files.length > 0) {
                filePreviewArea.style.display = 'block';
                updateFileSummary();
                
                // Update submit button text
                const submitBtn = document.getElementById('submit-files');
                if (submitBtn) {
                    submitBtn.innerHTML = `<i class="feather-upload me-2"></i> Upload ${files.length} Document(s) and Analyze`;
                }
            }
        }
        
        function validateFile(file) {
            const maxSize = 50 * 1024 * 1024; // 50MB per file
            const allowedTypes = [
                'application/pdf',
                'image/jpeg',
                'image/jpg', 
                'image/png',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/vnd.ms-excel',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'text/plain'
            ];
            
            if (file.size > maxSize) {
                alert('File "' + file.name + '" is too large. Maximum size is 50MB.');
                return false;
            }
            
            if (!allowedTypes.includes(file.type)) {
                alert('File type not supported for "' + file.name + '". Please use PDF, Images, Word, Excel, or Text files.');
                return false;
            }
            
            return true;
        }
        
        function createFilePreview(file, index) {
            const fileCard = document.createElement('div');
            fileCard.className = 'col-md-6 mb-2';
            
            const fileSize = formatFileSize(file.size);
            const fileIcon = getFileIcon(file.type);
            
            fileCard.innerHTML = `
                <div class="card border-success">
                    <div class="card-body p-2">
                        <div class="d-flex align-items-center">
                            <i class="${fileIcon} text-success me-2"></i>
                            <div class="flex-grow-1">
                                <div class="fw-bold text-truncate" style="max-width: 200px;" title="${file.name}">
                                    ${file.name}
                                </div>
                                <small class="text-muted">${fileSize}</small>
                            </div>
                            <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeFile(${index})">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            fileList.appendChild(fileCard);
        }
        
        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }
        
        function getFileIcon(fileType) {
            if (fileType.startsWith('image/')) {
                return 'fas fa-image';
            } else if (fileType === 'application/pdf') {
                return 'fas fa-file-pdf';
            } else if (fileType.includes('word')) {
                return 'fas fa-file-word';
            } else if (fileType.includes('excel') || fileType.includes('sheet')) {
                return 'fas fa-file-excel';
            } else if (fileType === 'text/plain') {
                return 'fas fa-file-alt';
            } else {
                return 'fas fa-file';
            }
        }
        
        function updateFileSummary() {
            const selectedFiles = fileList.children.length;
            const summaryElement = document.getElementById('fileSummary');
            
            if (summaryElement) {
                summaryElement.innerHTML = `
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle me-2"></i>
                        ${selectedFiles} file(s) selected and ready for upload
                    </div>
                `;
            }
        }
        
        // Global functions for file management
        window.removeFile = function(index) {
            const fileCards = fileList.children;
            if (fileCards[index]) {
                fileCards[index].remove();
                updateFileSummary();
                
                if (fileList.children.length === 0) {
                    filePreviewArea.style.display = 'none';
                }
            }
        };
        
        window.clearAllFiles = function() {
            if (confirm('Are you sure you want to remove all selected documents?')) {
                fileList.innerHTML = '';
                filePreviewArea.style.display = 'none';
                fileInput.value = '';
                console.log('All files cleared');
            }
        };
        
        window.saveDocuments = function() {
            const rememberDocs = document.getElementById('rememberDocuments').checked;
            const autoDelete = document.getElementById('autoDeleteAfterAnalysis').checked;
            const createBackup = document.getElementById('createBackup').checked;
            
            // Store preferences in localStorage
            localStorage.setItem('smartdispute_remember_docs', rememberDocs);
            localStorage.setItem('smartdispute_auto_delete', autoDelete);
            localStorage.setItem('smartdispute_create_backup', createBackup);
            
            // Show confirmation
            const alert = document.createElement('div');
            alert.className = 'alert alert-success alert-dismissible fade show position-fixed';
            alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
            alert.innerHTML = `
                <i class="fas fa-check-circle me-2"></i>Document preferences saved successfully!
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            document.body.appendChild(alert);
            
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, 3000);
            
            console.log('Document preferences saved:', { rememberDocs, autoDelete, createBackup });
        };
        
        // Load saved preferences
        function loadSavedPreferences() {
            const rememberDocs = localStorage.getItem('smartdispute_remember_docs');
            const autoDelete = localStorage.getItem('smartdispute_auto_delete');
            const createBackup = localStorage.getItem('smartdispute_create_backup');
            
            if (rememberDocs !== null) {
                document.getElementById('rememberDocuments').checked = rememberDocs === 'true';
            }
            if (autoDelete !== null) {
                document.getElementById('autoDeleteAfterAnalysis').checked = autoDelete === 'true';
            }
            if (createBackup !== null) {
                document.getElementById('createBackup').checked = createBackup === 'true';
            }
        }
        
        // Load preferences when file preview area is shown
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                    if (filePreviewArea.style.display !== 'none') {
                        loadSavedPreferences();
                    }
                }
            });
        });
        
        observer.observe(filePreviewArea, { attributes: true });
    }
});