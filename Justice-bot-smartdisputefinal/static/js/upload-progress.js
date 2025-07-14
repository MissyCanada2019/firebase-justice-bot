/**
 * Upload progress tracking for SmartDispute.ai
 * This script adds progress tracking and form enhancements to the file upload process
 */

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('uploadForm');
    const progressBar = document.querySelector('.progress-bar');
    const submitButton = document.getElementById('submit-files');
    const fileInput = document.getElementById('simpleFileInput');
    
    if (form && fileInput && progressBar) {
        // Update progress bar when file is selected
        fileInput.addEventListener('change', function() {
            if (fileInput.files.length > 0) {
                progressBar.style.width = '50%';
                progressBar.setAttribute('aria-valuenow', 50);
                
                // Show file count in a small badge
                let fileCountDisplay = document.getElementById('fileCountDisplay');
                if (!fileCountDisplay) {
                    fileCountDisplay = document.createElement('span');
                    fileCountDisplay.id = 'fileCountDisplay';
                    fileCountDisplay.className = 'badge bg-primary ms-2';
                    
                    // Try to find the label, if not found, create near the input
                    const label = document.querySelector('label[for="simpleFileInput"]');
                    if (label) {
                        label.appendChild(fileCountDisplay);
                    } else {
                        // Fallback: insert after the file input
                        fileInput.parentNode.insertBefore(fileCountDisplay, fileInput.nextSibling);
                    }
                }
                fileCountDisplay.textContent = fileInput.files.length + ' file(s) selected';
            } else {
                progressBar.style.width = '0%';
                progressBar.setAttribute('aria-valuenow', 0);
                
                // Remove file count badge if exists
                const fileCountDisplay = document.getElementById('fileCountDisplay');
                if (fileCountDisplay) {
                    fileCountDisplay.remove();
                }
            }
        });
        
        // Handle form submission
        form.addEventListener('submit', function(e) {
            // Check file size - warn if too large
            let totalSize = 0;
            for (let i = 0; i < fileInput.files.length; i++) {
                totalSize += fileInput.files[i].size;
            }
            
            // 250MB in bytes
            const maxSize = 250 * 1024 * 1024;
            
            if (totalSize > maxSize) {
                e.preventDefault();
                alert('Total file size exceeds 250MB limit. Please reduce the size or number of files.');
                return;
            }
            
            // Update UI to show progress
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Uploading...';
            progressBar.style.width = '75%';
            progressBar.setAttribute('aria-valuenow', 75);
            
            // Clear localStorage for this form to prevent duplicated submissions
            const formKey = `smartdispute_form_${form.id || form.name || window.location.pathname}`;
            localStorage.removeItem(formKey);
            
            // Add a "busy" overlay to prevent double clicks
            const overlay = document.createElement('div');
            overlay.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center';
            overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
            overlay.style.zIndex = '9999';
            
            const spinner = document.createElement('div');
            spinner.className = 'spinner-border text-primary';
            spinner.style.width = '3rem';
            spinner.style.height = '3rem';
            spinner.setAttribute('role', 'status');
            
            const spinnerText = document.createElement('span');
            spinnerText.className = 'visually-hidden';
            spinnerText.textContent = 'Loading...';
            
            spinner.appendChild(spinnerText);
            overlay.appendChild(spinner);
            
            // Append overlay after submission is complete to ensure the form is actually submitted
            setTimeout(() => {
                document.body.appendChild(overlay);
            }, 100);
            
            // The form will be submitted normally
        });
    }
});