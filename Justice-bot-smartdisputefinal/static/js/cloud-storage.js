/**
 * Cloud Storage Integration for SmartDispute.ai
 * Handles Google Drive, OneDrive, and Dropbox file selection
 */

class CloudStorageManager {
    constructor() {
        this.selectedFiles = {
            googledrive: [],
            onedrive: [],
            dropbox: []
        };
        this.initializeHandlers();
    }

    initializeHandlers() {
        // Google Drive
        document.getElementById('googleDriveBtn')?.addEventListener('click', () => {
            this.openGoogleDrivePicker();
        });

        // OneDrive
        document.getElementById('oneDriveBtn')?.addEventListener('click', () => {
            this.openOneDrivePicker();
        });

        // Dropbox
        document.getElementById('dropboxBtn')?.addEventListener('click', () => {
            this.openDropboxPicker();
        });
    }

    async openGoogleDrivePicker() {
        try {
            // Load Google Drive API
            await this.loadGoogleDriveAPI();
            
            const picker = new google.picker.PickerBuilder()
                .addView(google.picker.ViewId.DOCS)
                .setOAuthToken(await this.getGoogleAuthToken())
                .setCallback(this.handleGoogleDriveSelection.bind(this))
                .setOrigin(window.location.protocol + '//' + window.location.host)
                .build();
            
            picker.setVisible(true);
        } catch (error) {
            console.error('Google Drive picker error:', error);
            this.showError('Failed to open Google Drive. Please ensure you are signed in.');
        }
    }

    async openOneDrivePicker() {
        try {
            // OneDrive file picker options
            const options = {
                sdk: "8.0",
                entry: {
                    oneDrive: {
                        files: {}
                    }
                },
                authentication: {},
                messaging: {
                    origin: window.location.origin,
                    channelUrl: window.location.origin + "/static/js/onedrive-picker-auth.html"
                },
                selection: {
                    mode: "multiple"
                },
                typesAndSources: {
                    mode: "files",
                    pivots: {
                        oneDrive: true,
                        recent: true
                    }
                }
            };

            OneDrive.open(options).then((files) => {
                this.handleOneDriveSelection(files);
            }).catch((error) => {
                console.error('OneDrive picker error:', error);
                this.showError('Failed to open OneDrive. Please try again.');
            });
        } catch (error) {
            console.error('OneDrive initialization error:', error);
            this.showError('OneDrive service is not available. Please try uploading files directly.');
        }
    }

    async openDropboxPicker() {
        try {
            const options = {
                success: (files) => this.handleDropboxSelection(files),
                cancel: () => console.log('Dropbox picker cancelled'),
                linkType: 'direct',
                multiselect: true,
                extensions: ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png'],
                folderselect: false,
                sizeLimit: 262144000 // 250MB
            };

            Dropbox.choose(options);
        } catch (error) {
            console.error('Dropbox picker error:', error);
            this.showError('Dropbox service is not available. Please try uploading files directly.');
        }
    }

    async loadGoogleDriveAPI() {
        return new Promise((resolve, reject) => {
            if (typeof gapi !== 'undefined') {
                gapi.load('picker', resolve);
            } else {
                // Load Google API script
                const script = document.createElement('script');
                script.src = 'https://apis.google.com/js/api.js';
                script.onload = () => {
                    gapi.load('picker', resolve);
                };
                script.onerror = reject;
                document.head.appendChild(script);
            }
        });
    }

    async getGoogleAuthToken() {
        // This would typically come from your Google OAuth integration
        // For now, we'll prompt the user to authenticate if needed
        try {
            const response = await fetch('/auth/google-token');
            const data = await response.json();
            return data.access_token;
        } catch (error) {
            throw new Error('Please sign in with Google first');
        }
    }

    handleGoogleDriveSelection(data) {
        if (data.action === google.picker.Action.PICKED) {
            this.selectedFiles.googledrive = data.docs;
            this.displaySelectedFiles('googledrive', data.docs);
        }
    }

    handleOneDriveSelection(files) {
        this.selectedFiles.onedrive = files.value;
        this.displaySelectedFiles('onedrive', files.value);
    }

    handleDropboxSelection(files) {
        this.selectedFiles.dropbox = files;
        this.displaySelectedFiles('dropbox', files);
    }

    displaySelectedFiles(provider, files) {
        const container = document.getElementById(`${provider}Files`);
        if (!container) return;

        container.style.display = 'block';
        container.innerHTML = `
            <div class="alert alert-success">
                <h6><i class="feather-check-circle me-2"></i>Selected ${files.length} file(s)</h6>
                <div class="selected-files-list">
                    ${files.map(file => `
                        <div class="d-flex justify-content-between align-items-center py-1">
                            <span class="text-truncate">${file.name || file.fileName}</span>
                            <small class="text-muted">${this.formatFileSize(file.sizeBytes || file.size)}</small>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        // Update form data
        this.updateFormWithCloudFiles(provider, files);
    }

    updateFormWithCloudFiles(provider, files) {
        // Add hidden inputs for cloud files
        const form = document.getElementById('uploadForm');
        
        // Remove existing cloud file inputs for this provider
        form.querySelectorAll(`input[name="cloud_files_${provider}[]"]`).forEach(input => {
            input.remove();
        });

        // Add new cloud file inputs
        files.forEach((file, index) => {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = `cloud_files_${provider}[]`;
            input.value = JSON.stringify({
                id: file.id,
                name: file.name || file.fileName,
                url: file.link || file.downloadUrl,
                size: file.sizeBytes || file.size,
                provider: provider
            });
            form.appendChild(input);
        });
    }

    formatFileSize(bytes) {
        if (!bytes) return 'Unknown size';
        
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        if (bytes === 0) return '0 Bytes';
        
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
    }

    showError(message) {
        // Create or update error alert
        let errorAlert = document.getElementById('cloudStorageError');
        if (!errorAlert) {
            errorAlert = document.createElement('div');
            errorAlert.id = 'cloudStorageError';
            errorAlert.className = 'alert alert-warning alert-dismissible fade show mt-3';
            document.querySelector('#uploadTabContent').appendChild(errorAlert);
        }

        errorAlert.innerHTML = `
            <i class="feather-alert-triangle me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
    }
}

// Initialize cloud storage manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CloudStorageManager();
});

// Load external APIs
function loadCloudAPIs() {
    // Load OneDrive API
    const oneDriveScript = document.createElement('script');
    oneDriveScript.src = 'https://js.live.net/v7.2/OneDrive.js';
    oneDriveScript.async = true;
    document.head.appendChild(oneDriveScript);

    // Load Dropbox API
    const dropboxScript = document.createElement('script');
    dropboxScript.src = 'https://www.dropbox.com/static/api/2/dropins.js';
    dropboxScript.setAttribute('data-app-key', 'YOUR_DROPBOX_APP_KEY'); // To be configured
    dropboxScript.async = true;
    document.head.appendChild(dropboxScript);
}

// Load APIs when page loads
document.addEventListener('DOMContentLoaded', loadCloudAPIs);