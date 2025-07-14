/**
 * SmartDispute.ai - AI Chat Interface
 */

document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chatForm');
    const messageInput = document.getElementById('messageInput');
    const chatMessages = document.getElementById('chatMessages');
    const sessionIdInput = document.getElementById('sessionId');
    
    if (!chatForm || !messageInput || !chatMessages || !sessionIdInput) return;
    
    // Scroll chat to bottom
    scrollChatToBottom();
    
    // Handle form submission
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const message = messageInput.value.trim();
        const sessionId = sessionIdInput.value;
        
        if (!message) return;
        
        // Display user message
        appendMessage(message, true);
        
        // Clear input
        messageInput.value = '';
        
        // Show loading indicator
        appendLoadingMessage();
        
        // Send message to server
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Remove loading indicator
            removeLoadingMessage();
            
            // Display AI response
            appendMessage(data.response, false);
            
            // Scroll to bottom
            scrollChatToBottom();
        })
        .catch(error => {
            console.error('Error:', error);
            
            // Remove loading indicator
            removeLoadingMessage();
            
            // Display error message
            appendErrorMessage();
            
            // Scroll to bottom
            scrollChatToBottom();
        });
        
        // Scroll to bottom
        scrollChatToBottom();
    });
    
    // Auto-resize input field
    messageInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
    
    // Handle case selection for context
    const caseSelect = document.getElementById('caseSelect');
    if (caseSelect) {
        caseSelect.addEventListener('change', function() {
            const caseId = this.value;
            if (caseId) {
                window.location.href = `/chat?case_id=${caseId}`;
            } else {
                window.location.href = '/chat';
            }
        });
    }
});

/**
 * Append a message to the chat
 * @param {string} message - Message content
 * @param {boolean} isUser - Whether the message is from the user
 */
function appendMessage(message, isUser) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = isUser ? 'chat-message user-message' : 'chat-message ai-message';
    
    // Process message text (convert URLs to links, etc.)
    const processedMessage = processMessageText(message);
    
    messageDiv.innerHTML = processedMessage;
    
    // Add to chat container
    chatMessages.appendChild(messageDiv);
    
    // Initialize legal references if this is an AI message
    if (!isUser) {
        // Use a small delay to ensure the DOM is updated
        setTimeout(() => {
            initLegalReferences();
        }, 100);
    }
    
    // Scroll to bottom
    scrollChatToBottom();
}

/**
 * Process message text for display
 * @param {string} text - Raw message text
 * @return {string} Processed HTML
 */
function processMessageText(text) {
    try {
        // Check if the text is already HTML by looking for common HTML tags
        const containsHTML = /<\/?[a-z][\s\S]*>/i.test(text);
        
        // If it doesn't contain HTML, process it as text
        if (!containsHTML) {
            // Convert URLs to clickable links
            const urlRegex = /(https?:\/\/[^\s]+)/g;
            text = text.replace(urlRegex, url => `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`);
            
            // Convert markdown-style links [text](url)
            const markdownLinkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
            text = text.replace(markdownLinkRegex, (match, linkText, url) => 
                `<a href="${url}" target="_blank" rel="noopener noreferrer">${linkText}</a>`
            );
            
            // Handle line breaks
            text = text.replace(/\n/g, '<br>');
        }
        
        return text;
    } catch (error) {
        console.error("Error processing message text:", error);
        return text; // Return original text if there was an error
    }
}

/**
 * Initialize legal reference tooltips and handlers
 * This function initializes tooltips and click handlers for inline legal references
 */
function initLegalReferences() {
    // Initialize Bootstrap tooltips for legal references
    const legalReferences = document.querySelectorAll('.legal-reference-inline');
    if (legalReferences.length > 0) {
        legalReferences.forEach(ref => {
            // Handle clicks on reference markers
            ref.addEventListener('click', function(e) {
                e.preventDefault();
                const refId = this.getAttribute('data-reference-id');
                if (refId) {
                    // Scroll to the reference in the footnotes
                    const targetRef = document.getElementById(refId);
                    if (targetRef) {
                        targetRef.scrollIntoView({ behavior: 'smooth' });
                        // Highlight the reference briefly
                        targetRef.classList.add('reference-highlight');
                        setTimeout(() => {
                            targetRef.classList.remove('reference-highlight');
                        }, 2000);
                    }
                }
            });
            
            // Initialize tooltip if available
            if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
                new bootstrap.Tooltip(ref);
            }
        });
        
        // Add CSS for reference highlights if it doesn't exist
        if (!document.getElementById('legal-reference-styles')) {
            const styleSheet = document.createElement('style');
            styleSheet.id = 'legal-reference-styles';
            styleSheet.textContent = `
                .legal-reference-inline {
                    color: var(--bs-primary);
                    cursor: pointer;
                    text-decoration: underline dotted;
                }
                .reference-marker {
                    font-size: 0.7em;
                    color: var(--bs-primary);
                }
                .reference-highlight {
                    background-color: rgba(0, 123, 255, 0.2);
                    transition: background-color 0.5s ease;
                }
                .legal-reference-tooltip {
                    max-width: 300px;
                }
            `;
            document.head.appendChild(styleSheet);
        }
    }
}

/**
 * Append a loading message
 */
function appendLoadingMessage() {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'chat-message ai-message loading-message';
    loadingDiv.innerHTML = `
        <div class="d-flex align-items-center">
            <div class="spinner-grow spinner-grow-sm me-2" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <div class="spinner-grow spinner-grow-sm me-2" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <div class="spinner-grow spinner-grow-sm" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(loadingDiv);
    scrollChatToBottom();
}

/**
 * Remove loading message
 */
function removeLoadingMessage() {
    const loadingMessage = document.querySelector('.loading-message');
    if (loadingMessage) {
        loadingMessage.remove();
    }
}

/**
 * Append an error message
 */
function appendErrorMessage() {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'chat-message ai-message text-danger';
    errorDiv.innerHTML = 'Sorry, I encountered an error processing your request. Please try again.';
    
    chatMessages.appendChild(errorDiv);
}

/**
 * Scroll chat container to the bottom
 */
function scrollChatToBottom() {
    const chatContainer = document.querySelector('.chat-container');
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}
