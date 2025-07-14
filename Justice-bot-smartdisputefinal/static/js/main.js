/* SmartDispute.ai Main JavaScript */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize document upload functionality
    initializeFileUpload();
    
    // Initialize chat functionality
    initializeChat();
    
    // Initialize theme toggle
    initializeThemeToggle();
});

// File upload functionality
function initializeFileUpload() {
    const uploadArea = document.querySelector('.upload-area');
    const fileInput = document.querySelector('#file-input');
    
    if (!uploadArea || !fileInput) return;
    
    // Handle drag and drop events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    // Handle dragover and dragleave for visual feedback
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => {
            uploadArea.classList.add('dragover');
        }, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => {
            uploadArea.classList.remove('dragover');
        }, false);
    });
    
    // Handle drop event
    uploadArea.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            fileInput.files = files;
            updateFileList(files);
        }
    }
    
    // Handle click on upload area
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });
    
    // Handle file selection
    fileInput.addEventListener('change', (e) => {
        updateFileList(e.target.files);
    });
    
    // Update file list display
    function updateFileList(files) {
        const fileList = document.querySelector('#file-list');
        if (!fileList) return;
        
        fileList.innerHTML = '';
        
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const item = document.createElement('div');
            item.className = 'file-item d-flex align-items-center mb-2 p-2 border rounded';
            
            // Icon based on file type
            let icon = 'file-text';
            if (file.type.includes('image')) {
                icon = 'image';
            } else if (file.type.includes('pdf')) {
                icon = 'file-text';
            } else if (file.type.includes('word')) {
                icon = 'file';
            }
            
            item.innerHTML = `
                <div class="me-3"><i class="feather-${icon}"></i></div>
                <div class="flex-grow-1">
                    <div class="fw-bold">${file.name}</div>
                    <div class="small text-muted">${formatFileSize(file.size)}</div>
                </div>
            `;
            
            fileList.appendChild(item);
        }
        
        // Show the submit button if there are files
        const submitBtn = document.querySelector('#submit-files');
        if (submitBtn) {
            submitBtn.style.display = files.length > 0 ? 'block' : 'none';
        }
    }
    
    // Format file size in KB, MB, etc.
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Chat functionality
function initializeChat() {
    const chatForm = document.querySelector('#chat-form');
    const chatInput = document.querySelector('#chat-input');
    const chatMessages = document.querySelector('#chat-messages');
    
    if (!chatForm || !chatInput || !chatMessages) return;
    
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const message = chatInput.value.trim();
        if (message === '') return;
        
        // Add user message to chat
        addMessage(message, 'user');
        
        // Clear input
        chatInput.value = '';
        
        // Get response from server
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                case_id: chatForm.dataset.caseId || null
            })
        })
        .then(response => response.json())
        .then(data => {
            // Add AI response to chat
            if (data.response) {
                addMessage(data.response, 'ai');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage('Sorry, there was an error processing your request. Please try again.', 'ai error');
        });
    });
    
    function addMessage(text, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${type} mb-3 p-3 rounded`;
        
        // If this is an AI message, we'll format any markdown-like elements
        if (type === 'ai') {
            // Simple formatting for links, bold, italics, etc.
            text = text
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
                .replace(/`(.*?)`/g, '<code>$1</code>')
                .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
            
            // Add paragraphs
            text = text.split('\n\n').map(p => `<p>${p}</p>`).join('');
            
            messageDiv.innerHTML = text;
        } else {
            messageDiv.textContent = text;
        }
        
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// For analyze page
document.addEventListener('DOMContentLoaded', function() {
    // Initialize merit score visualization if exists
    const meritScore = document.querySelector('#merit-score');
    if (meritScore) {
        const score = parseFloat(meritScore.dataset.score);
        let scoreClass = 'low';
        
        if (score >= 0.7) {
            scoreClass = 'high';
        } else if (score >= 0.4) {
            scoreClass = 'medium';
        }
        
        meritScore.classList.add(scoreClass);
        animateScore(meritScore, score);
    }
    
    function animateScore(element, targetScore) {
        let currentScore = 0;
        const duration = 1000; // ms
        const interval = 20; // ms
        const steps = duration / interval;
        const increment = targetScore / steps;
        
        const timer = setInterval(() => {
            currentScore += increment;
            if (currentScore >= targetScore) {
                clearInterval(timer);
                element.textContent = Math.round(targetScore * 100) + '%';
            } else {
                element.textContent = Math.round(currentScore * 100) + '%';
            }
        }, interval);
    }
});

function initializeThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    
    // Only proceed if theme toggle exists
    if (!themeToggle) {
        console.log('Theme toggle not found, skipping initialization');
        return;
    }
    
    const html = document.documentElement;
    const lightIcon = themeToggle.querySelector('.light-icon');
    const darkIcon = themeToggle.querySelector('.dark-icon');
    
    // Check saved theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        html.setAttribute('data-bs-theme', savedTheme);
        if (lightIcon && darkIcon) {
            updateIcons(savedTheme === 'light');
        }
    }
    
    themeToggle.addEventListener('click', () => {
        const isLight = html.getAttribute('data-bs-theme') === 'light';
        const newTheme = isLight ? 'dark' : 'light';
        
        html.setAttribute('data-bs-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        if (lightIcon && darkIcon) {
            updateIcons(!isLight);
        }
    });
    
    function updateIcons(isLight) {
        if (lightIcon && darkIcon) {
            lightIcon.style.display = isLight ? 'none' : 'inline';
            darkIcon.style.display = isLight ? 'inline' : 'none';
        }
    }
}
