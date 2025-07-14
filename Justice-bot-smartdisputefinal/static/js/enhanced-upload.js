/**
 * Enhanced Multi-File Upload System for SmartDispute.ai
 * Supports multiple evidence types, drag-and-drop, and cloud storage integration
 */

class EnhancedUploadManager {
    constructor() {
        this.selectedFiles = new Map();
        this.currentEvidenceType = 'supporting';
        this.maxFileSize = 250 * 1024 * 1024; // 250MB total
        this.currentTotalSize = 0;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupDragAndDrop();
        this.setupEvidenceTypeSelection();
        this.setupCloudStorageHandlers();
    }
    
    setupEventListeners() {
        const fileInput = document.getElementById('simpleFileInput');
        const dropzone = document.getElementById('uploadDropzone');
        
        console.log('Setting up event listeners...', { fileInput: !!fileInput, dropzone: !!dropzone });
        
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                console.log('File input change detected:', e.target.files.length, 'files');
                this.handleFileSelection(e);
            });
        }
        
        if (dropzone) {
            dropzone.style.cursor = 'pointer';
            
            dropzone.addEventListener('click', (e) => {
                console.log('Dropzone clicked');
                e.preventDefault();
                e.stopPropagation();
                
                if (fileInput) {
                    console.log('Triggering file input click');
                    fileInput.click();
                } else {
                    console.error('File input element not found');
                }
            });
        } else {
            console.error('Upload dropzone element not found');
        }
    }
    
    setupDragAndDrop() {
        const dropzone = document.getElementById('uploadDropzone');
        if (!dropzone) return;
        
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });
        
        dropzone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
        });
        
        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
            
            const files = Array.from(e.dataTransfer.files);
            this.processFiles(files);
        });
    }
    
    setupEvidenceTypeSelection() {
        const evidenceCards = document.querySelectorAll('.evidence-type-card');
        const evidenceTypeInput = document.getElementById('evidenceType');
        
        evidenceCards.forEach(card => {
            card.addEventListener('click', () => {
                // Remove active class from all cards
                evidenceCards.forEach(c => c.classList.remove('active'));
                
                // Add active class to clicked card
                card.classList.add('active');
                
                // Update evidence type
                this.currentEvidenceType = card.dataset.type;
                if (evidenceTypeInput) {
                    evidenceTypeInput.value = this.currentEvidenceType;
                }
                
                // Update file previews with new evidence type
                this.updateFilePreviewBadges();
            });
        });
    }
    
    setupCloudStorageHandlers() {
        // Google Drive
        const googleDriveBtn = document.getElementById('googleDriveBtn');
        if (googleDriveBtn) {
            googleDriveBtn.addEventListener('click', () => this.initializeGoogleDrive());
        }
        
        // OneDrive
        const oneDriveBtn = document.getElementById('oneDriveBtn');
        if (oneDriveBtn) {
            oneDriveBtn.addEventListener('click', () => this.initializeOneDrive());
        }
        
        // Dropbox
        const dropboxBtn = document.getElementById('dropboxBtn');
        if (dropboxBtn) {
            dropboxBtn.addEventListener('click', () => this.initializeDropbox());
        }
    }
    
    handleFileSelection(event) {
        const files = Array.from(event.target.files);
        this.processFiles(files);
    }
    
    processFiles(files) {
        const validFiles = [];
        let totalSize = this.currentTotalSize;
        
        files.forEach(file => {
            // Check file type
            if (!this.isValidFileType(file)) {
                this.showError(`File type not supported: ${file.name}`);
                return;
            }
            
            // Check size
            if (totalSize + file.size > this.maxFileSize) {
                this.showError(`Total file size would exceed 250MB limit`);
                return;
            }
            
            totalSize += file.size;
            validFiles.push(file);
        });
        
        if (validFiles.length > 0) {
            validFiles.forEach(file => this.addFileToSelection(file));
            this.updateFilePreview();
            this.currentTotalSize = totalSize;
        }
    }
    
    isValidFileType(file) {
        const allowedTypes = [
            'application/pdf',
            'image/jpeg',
            'image/jpg', 
            'image/png',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',
            'application/rtf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ];
        
        const allowedExtensions = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx', '.txt', '.rtf', '.xls', '.xlsx'];
        
        return allowedTypes.includes(file.type) || 
               allowedExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
    }
    
    addFileToSelection(file) {
        const fileId = this.generateFileId();
        const fileData = {
            id: fileId,
            file: file,
            evidenceType: this.currentEvidenceType,
            source: 'local',
            addedAt: new Date()
        };
        
        this.selectedFiles.set(fileId, fileData);
    }
    
    generateFileId() {
        return 'file_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    updateFilePreview() {
        const previewArea = document.getElementById('filePreviewArea');
        const fileList = document.getElementById('fileList');
        
        if (!previewArea || !fileList) return;
        
        if (this.selectedFiles.size === 0) {
            previewArea.style.display = 'none';
            return;
        }
        
        previewArea.style.display = 'block';
        fileList.innerHTML = '';
        
        this.selectedFiles.forEach((fileData, fileId) => {
            const fileCard = this.createFilePreviewCard(fileData);
            fileList.appendChild(fileCard);
        });
        
        this.updateFileSummary();
    }
    
    createFilePreviewCard(fileData) {
        const col = document.createElement('div');
        col.className = 'col-md-4 col-sm-6';
        
        const card = document.createElement('div');
        card.className = 'file-preview-card';
        
        const evidenceBadge = document.createElement('span');
        evidenceBadge.className = `evidence-badge ${fileData.evidenceType}`;
        evidenceBadge.textContent = this.getEvidenceTypeLabel(fileData.evidenceType);
        
        const removeBtn = document.createElement('button');
        removeBtn.className = 'file-remove-btn';
        removeBtn.innerHTML = '×';
        removeBtn.onclick = () => this.removeFile(fileData.id);
        
        const icon = document.createElement('i');
        icon.className = `${this.getFileTypeIcon(fileData.file)} file-type-icon text-center d-block`;
        
        const fileName = document.createElement('div');
        fileName.className = 'file-name text-truncate';
        fileName.textContent = fileData.file.name;
        fileName.title = fileData.file.name;
        
        const fileSize = document.createElement('div');
        fileSize.className = 'file-size text-muted small';
        fileSize.textContent = this.formatFileSize(fileData.file.size);
        
        const sourceLabel = document.createElement('div');
        sourceLabel.className = 'file-source text-muted small';
        sourceLabel.textContent = fileData.source === 'local' ? 'Local File' : fileData.source;
        
        card.appendChild(evidenceBadge);
        card.appendChild(removeBtn);
        card.appendChild(icon);
        card.appendChild(fileName);
        card.appendChild(fileSize);
        card.appendChild(sourceLabel);
        
        col.appendChild(card);
        return col;
    }
    
    getEvidenceTypeLabel(type) {
        const labels = {
            'supporting': 'Supporting',
            'opposition': 'Opposition',
            'counter': 'Counter'
        };
        return labels[type] || 'Supporting';
    }
    
    getFileTypeIcon(file) {
        const name = file.name.toLowerCase();
        
        if (name.endsWith('.pdf')) {
            return 'fas fa-file-pdf file-type-pdf';
        } else if (name.match(/\.(jpg|jpeg|png)$/)) {
            return 'fas fa-file-image file-type-image';
        } else if (name.match(/\.(doc|docx)$/)) {
            return 'fas fa-file-word file-type-doc';
        } else if (name.match(/\.(xls|xlsx)$/)) {
            return 'fas fa-file-excel file-type-excel';
        } else if (name.match(/\.(txt|rtf)$/)) {
            return 'fas fa-file-alt file-type-text';
        }
        return 'fas fa-file file-type-text';
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    removeFile(fileId) {
        const fileData = this.selectedFiles.get(fileId);
        if (fileData) {
            this.currentTotalSize -= fileData.file.size;
            this.selectedFiles.delete(fileId);
            this.updateFilePreview();
        }
    }
    
    updateFilePreviewBadges() {
        const badges = document.querySelectorAll('.evidence-badge');
        badges.forEach(badge => {
            badge.className = `evidence-badge ${this.currentEvidenceType}`;
            badge.textContent = this.getEvidenceTypeLabel(this.currentEvidenceType);
        });
    }
    
    updateFileSummary() {
        const summary = document.getElementById('fileSummary');
        const summaryContainer = document.getElementById('fileSummaryContainer');
        
        if (!summary || !summaryContainer) return;
        
        const fileCount = this.selectedFiles.size;
        
        if (fileCount === 0) {
            summaryContainer.style.display = 'none';
            return;
        }
        
        summaryContainer.style.display = 'block';
        
        const sizeUsed = this.formatFileSize(this.currentTotalSize);
        const sizeTotal = this.formatFileSize(this.maxFileSize);
        
        // Count by evidence type
        const counts = { supporting: 0, opposition: 0, counter: 0 };
        this.selectedFiles.forEach(fileData => {
            counts[fileData.evidenceType]++;
        });
        
        summary.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <span>${fileCount} file(s) selected</span>
                <span>${sizeUsed} / ${sizeTotal}</span>
            </div>
        `;
        
        // Update evidence type counts
        document.getElementById('supportingCount').textContent = counts.supporting;
        document.getElementById('oppositionCount').textContent = counts.opposition;
        document.getElementById('counterCount').textContent = counts.counter;
    }
    
    // Cloud Storage Methods
    initializeGoogleDrive() {
        this.showCloudStorageModal('Google Drive', 'googledrive');
    }
    
    initializeOneDrive() {
        this.showCloudStorageModal('OneDrive', 'onedrive');
    }
    
    initializeDropbox() {
        this.showCloudStorageModal('Dropbox', 'dropbox');
    }
    
    showCloudStorageModal(serviceName, serviceType) {
        // Create modal for cloud storage file selection
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Select Files from ${serviceName}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="text-center py-4">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                            <p class="mt-2">Connecting to ${serviceName}...</p>
                        </div>
                        <div id="cloudFilesList" style="display: none;"></div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="selectCloudFiles">Select Files</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Initialize Bootstrap modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        // Simulate cloud storage connection
        setTimeout(() => {
            this.loadCloudFiles(serviceType, modal);
        }, 2000);
        
        // Cleanup modal on hide
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }
    
    loadCloudFiles(serviceType, modal) {
        // Simulate cloud files - in real implementation, this would call the backend API
        const mockFiles = [
            { name: 'Lease_Agreement.pdf', size: 2048576, type: 'application/pdf', id: 'cloud_1' },
            { name: 'Eviction_Notice.pdf', size: 1024768, type: 'application/pdf', id: 'cloud_2' },
            { name: 'Payment_Receipt.jpg', size: 512384, type: 'image/jpeg', id: 'cloud_3' },
            { name: 'Email_Communication.docx', size: 256192, type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', id: 'cloud_4' }
        ];
        
        const loadingDiv = modal.querySelector('.text-center');
        const filesList = modal.querySelector('#cloudFilesList');
        
        loadingDiv.style.display = 'none';
        filesList.style.display = 'block';
        
        filesList.innerHTML = mockFiles.map(file => `
            <div class="cloud-file-item" data-file-id="${file.id}">
                <div class="cloud-file-icon">
                    <i class="${this.getFileTypeIconForMime(file.type)}"></i>
                </div>
                <div class="cloud-file-info">
                    <div class="cloud-file-name">${file.name}</div>
                    <div class="cloud-file-meta">${this.formatFileSize(file.size)} • ${serviceType}</div>
                </div>
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" value="${file.id}">
                </div>
            </div>
        `).join('');
        
        // Add click handlers for file selection
        filesList.querySelectorAll('.cloud-file-item').forEach(item => {
            item.addEventListener('click', (e) => {
                if (e.target.type !== 'checkbox') {
                    const checkbox = item.querySelector('input[type="checkbox"]');
                    checkbox.checked = !checkbox.checked;
                }
                item.classList.toggle('selected', item.querySelector('input[type="checkbox"]').checked);
            });
        });
        
        // Handle file selection
        modal.querySelector('#selectCloudFiles').addEventListener('click', () => {
            const selectedCheckboxes = filesList.querySelectorAll('input[type="checkbox"]:checked');
            selectedCheckboxes.forEach(checkbox => {
                const fileData = mockFiles.find(f => f.id === checkbox.value);
                if (fileData) {
                    this.addCloudFileToSelection(fileData, serviceType);
                }
            });
            
            this.updateFilePreview();
            bootstrap.Modal.getInstance(modal).hide();
        });
    }
    
    getFileTypeIconForMime(mimeType) {
        if (mimeType.includes('pdf')) return 'fas fa-file-pdf file-type-pdf';
        if (mimeType.includes('image')) return 'fas fa-file-image file-type-image';
        if (mimeType.includes('word')) return 'fas fa-file-word file-type-doc';
        if (mimeType.includes('excel') || mimeType.includes('spreadsheet')) return 'fas fa-file-excel file-type-excel';
        return 'fas fa-file file-type-text';
    }
    
    addCloudFileToSelection(fileData, serviceType) {
        const fileId = this.generateFileId();
        const file = {
            id: fileId,
            file: {
                name: fileData.name,
                size: fileData.size,
                type: fileData.type
            },
            evidenceType: this.currentEvidenceType,
            source: serviceType,
            cloudId: fileData.id,
            addedAt: new Date()
        };
        
        this.selectedFiles.set(fileId, file);
        this.currentTotalSize += fileData.size;
    }
    
    showError(message) {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white bg-danger border-0 position-fixed';
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 1050;';
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove toast after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            document.body.removeChild(toast);
        });
    }
    
    // Public method to get selected files for form submission
    getSelectedFiles() {
        return Array.from(this.selectedFiles.values());
    }
}

// Initialize the upload manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('uploadDropzone')) {
        window.uploadManager = new EnhancedUploadManager();
    }
});