/**
 * Form auto-save functionality for SmartDispute.ai
 * This script automatically saves form input values to localStorage and restores them
 * when the user returns to the page.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get all forms with data-autosave attribute
    const forms = document.querySelectorAll('form[data-autosave]');
    
    forms.forEach(form => {
        const formId = form.getAttribute('id') || form.getAttribute('name') || window.location.pathname;
        const formKey = `smartdispute_form_${formId}`;
        const inputFields = form.querySelectorAll('input, select, textarea');
        
        // Restore saved values from localStorage
        restoreFormValues(formKey, inputFields);
        
        // Add input event listeners to save changes
        inputFields.forEach(field => {
            if (field.type !== 'submit' && field.type !== 'button' && field.type !== 'file' && field.type !== 'reset' && field.type !== 'hidden') {
                field.addEventListener('input', () => {
                    saveFormValues(formKey, inputFields);
                });
                
                // Also save on change for select elements
                if (field.tagName === 'SELECT') {
                    field.addEventListener('change', () => {
                        saveFormValues(formKey, inputFields);
                    });
                }
            }
        });
        
        // Remove saved data when form is submitted
        form.addEventListener('submit', () => {
            localStorage.removeItem(formKey);
        });
    });
    
    // Progress tracking for multi-step forms
    const progressForms = document.querySelectorAll('form[data-progress]');
    
    progressForms.forEach(form => {
        initializeProgressBar(form);
    });
});

/**
 * Save form values to localStorage
 * @param {string} formKey - Unique key for the form
 * @param {NodeList} fields - Form input fields
 */
function saveFormValues(formKey, fields) {
    const formData = {};
    
    fields.forEach(field => {
        // Skip buttons, file inputs, and hidden fields
        if (field.type !== 'submit' && field.type !== 'button' && field.type !== 'file' && field.type !== 'reset' && field.type !== 'hidden') {
            // Handle different input types
            if (field.type === 'checkbox' || field.type === 'radio') {
                formData[field.name] = field.checked;
            } else {
                formData[field.name] = field.value;
            }
        }
    });
    
    localStorage.setItem(formKey, JSON.stringify(formData));
    
    // Show "Saved" indicator
    showSavedIndicator();
}

/**
 * Restore saved form values from localStorage
 * @param {string} formKey - Unique key for the form
 * @param {NodeList} fields - Form input fields
 */
function restoreFormValues(formKey, fields) {
    const savedData = localStorage.getItem(formKey);
    
    if (savedData) {
        const formData = JSON.parse(savedData);
        
        fields.forEach(field => {
            if (field.name in formData) {
                if (field.type === 'checkbox' || field.type === 'radio') {
                    field.checked = formData[field.name];
                } else {
                    field.value = formData[field.name];
                }
            }
        });
        
        // Show restoration notice
        showRestorationNotice();
    }
}

/**
 * Show a temporary "Saved" indicator
 */
function showSavedIndicator() {
    // Check if indicator already exists
    let indicator = document.getElementById('autosave-indicator');
    
    if (!indicator) {
        // Create indicator
        indicator = document.createElement('div');
        indicator.id = 'autosave-indicator';
        indicator.className = 'autosave-indicator';
        indicator.innerHTML = '<i class="feather-check-circle me-2"></i> Draft saved';
        document.body.appendChild(indicator);
        
        // Add styling if it's not already in CSS
        if (!document.getElementById('autosave-indicator-style')) {
            const style = document.createElement('style');
            style.id = 'autosave-indicator-style';
            style.textContent = `
                .autosave-indicator {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    background-color: rgba(40, 40, 40, 0.9);
                    color: white;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-size: 14px;
                    z-index: 1050;
                    opacity: 0;
                    transition: opacity 0.3s ease;
                    display: flex;
                    align-items: center;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
                }
                .autosave-indicator.visible {
                    opacity: 1;
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    // Show indicator
    setTimeout(() => {
        indicator.classList.add('visible');
    }, 10);
    
    // Hide after 2 seconds
    setTimeout(() => {
        indicator.classList.remove('visible');
    }, 2000);
}

/**
 * Show a notice that form data has been restored
 */
function showRestorationNotice() {
    // Check if we already have the alert container
    let alertContainer = document.querySelector('.restored-form-alert-container');
    
    if (!alertContainer) {
        // Find the first form with autosave attribute
        const targetForm = document.querySelector('form[data-autosave]');
        
        if (targetForm) {
            // Create alert container
            alertContainer = document.createElement('div');
            alertContainer.className = 'restored-form-alert-container mb-3';
            
            // Create alert
            const alert = document.createElement('div');
            alert.className = 'alert alert-info alert-dismissible fade show';
            alert.setAttribute('role', 'alert');
            alert.innerHTML = `
                <i class="feather-refresh-cw me-2"></i>
                Your previously entered data has been restored.
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                <button type="button" class="btn btn-sm btn-outline-secondary ms-3 clear-saved-data">Clear saved data</button>
            `;
            
            alertContainer.appendChild(alert);
            
            // Insert alert before the form
            targetForm.parentNode.insertBefore(alertContainer, targetForm);
            
            // Add event listener to clear button
            const clearButton = alertContainer.querySelector('.clear-saved-data');
            clearButton.addEventListener('click', function() {
                const formId = targetForm.getAttribute('id') || targetForm.getAttribute('name') || window.location.pathname;
                const formKey = `smartdispute_form_${formId}`;
                
                // Clear localStorage and form
                localStorage.removeItem(formKey);
                targetForm.reset();
                
                // Remove alert
                alertContainer.remove();
            });
        }
    }
}

/**
 * Initialize progress bar for multi-step forms
 * @param {HTMLElement} form - Form element with progress tracking
 */
function initializeProgressBar(form) {
    const progressBar = form.querySelector('.progress-bar');
    const steps = form.querySelectorAll('.form-step');
    const totalSteps = steps.length;
    let currentStep = 0;
    
    // Find the currently visible step
    steps.forEach((step, index) => {
        if (!step.classList.contains('d-none')) {
            currentStep = index;
        }
    });
    
    // Update progress bar width
    if (progressBar) {
        const progressPercentage = ((currentStep + 1) / totalSteps) * 100;
        progressBar.style.width = `${progressPercentage}%`;
        progressBar.setAttribute('aria-valuenow', progressPercentage);
        
        // Also update the text if needed
        const progressText = progressBar.querySelector('.progress-text');
        if (progressText) {
            progressText.textContent = `Step ${currentStep + 1} of ${totalSteps}`;
        }
    }
    
    // Add navigation event listeners
    const nextButtons = form.querySelectorAll('.btn-next-step');
    const prevButtons = form.querySelectorAll('.btn-prev-step');
    
    nextButtons.forEach(button => {
        button.addEventListener('click', () => {
            const stepIndex = parseInt(button.getAttribute('data-step-index'));
            if (validateStep(form, stepIndex)) {
                navigateToStep(form, stepIndex + 1);
            }
        });
    });
    
    prevButtons.forEach(button => {
        button.addEventListener('click', () => {
            const stepIndex = parseInt(button.getAttribute('data-step-index'));
            navigateToStep(form, stepIndex - 1);
        });
    });
}

/**
 * Validate a specific form step before proceeding
 * @param {HTMLElement} form - Form element
 * @param {number} stepIndex - Current step index
 * @returns {boolean} - Whether the step is valid
 */
function validateStep(form, stepIndex) {
    const currentStep = form.querySelector(`.form-step[data-step="${stepIndex}"]`);
    const requiredFields = currentStep.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value) {
            isValid = false;
            field.classList.add('is-invalid');
            
            // Add invalid feedback if not present
            let feedback = field.nextElementSibling;
            if (!feedback || !feedback.classList.contains('invalid-feedback')) {
                feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                feedback.textContent = 'This field is required';
                field.parentNode.insertBefore(feedback, field.nextSibling);
            }
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

/**
 * Navigate to a specific step in a multi-step form
 * @param {HTMLElement} form - Form element
 * @param {number} targetStep - Target step index
 */
function navigateToStep(form, targetStep) {
    const steps = form.querySelectorAll('.form-step');
    const progressBar = form.querySelector('.progress-bar');
    const totalSteps = steps.length;
    
    if (targetStep >= 0 && targetStep < totalSteps) {
        // Hide all steps
        steps.forEach(step => {
            step.classList.add('d-none');
        });
        
        // Show target step
        steps[targetStep].classList.remove('d-none');
        
        // Update progress bar
        if (progressBar) {
            const progressPercentage = ((targetStep + 1) / totalSteps) * 100;
            progressBar.style.width = `${progressPercentage}%`;
            progressBar.setAttribute('aria-valuenow', progressPercentage);
            
            // Update text if present
            const progressText = progressBar.querySelector('.progress-text');
            if (progressText) {
                progressText.textContent = `Step ${targetStep + 1} of ${totalSteps}`;
            }
        }
        
        // Save the current step to form data attribute
        form.setAttribute('data-current-step', targetStep);
        
        // Save progress to localStorage
        const formId = form.getAttribute('id') || form.getAttribute('name') || window.location.pathname;
        localStorage.setItem(`smartdispute_progress_${formId}`, targetStep);
        
        // Scroll to top of form for better UX
        form.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}