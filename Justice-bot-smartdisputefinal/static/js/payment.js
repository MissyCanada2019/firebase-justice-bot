/**
 * SmartDispute.ai - Payment Processing
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize PayPal buttons if container exists
    if (document.getElementById('paypal-button-container')) {
        initializePayPal();
    }
    
    // Set up subscription form handling
    const subscriptionForm = document.getElementById('subscriptionForm');
    if (subscriptionForm) {
        subscriptionForm.addEventListener('submit', handleSubscriptionSubmit);
    }
    
    // Set up pricing toggle
    const pricingToggle = document.getElementById('pricingToggle');
    if (pricingToggle) {
        pricingToggle.addEventListener('change', togglePricingPeriod);
    }
});

/**
 * Initialize PayPal buttons
 */
function initializePayPal() {
    // Get payment details
    const amount = document.getElementById('paymentAmount').value;
    const itemName = document.getElementById('paymentItemName').value;
    const paymentType = document.getElementById('paymentType').value;
    
    // Render PayPal buttons
    paypal.Buttons({
        // Set up the transaction
        createOrder: function(data, actions) {
            return actions.order.create({
                purchase_units: [{
                    amount: {
                        value: amount
                    },
                    description: itemName
                }]
            });
        },
        
        // Finalize the transaction
        onApprove: function(data, actions) {
            return actions.order.capture().then(function(orderData) {
                // Get the transaction details
                const transaction = orderData.purchase_units[0].payments.captures[0];
                const paymentId = transaction.id;
                
                // Show success message
                const successMessage = document.getElementById('paymentSuccess');
                if (successMessage) {
                    successMessage.style.display = 'block';
                }
                
                // Hide payment buttons
                const paymentContainer = document.getElementById('paypal-button-container');
                if (paymentContainer) {
                    paymentContainer.style.display = 'none';
                }
                
                // Submit payment information to server
                if (paymentType === 'document') {
                    processDocumentPayment(paymentId);
                } else if (paymentType === 'subscription') {
                    processSubscriptionPayment(paymentId);
                }
            });
        },
        
        // Handle errors
        onError: function(err) {
            console.error('PayPal Error:', err);
            
            // Show error message
            const errorMessage = document.getElementById('paymentError');
            if (errorMessage) {
                errorMessage.textContent = 'An error occurred while processing your payment. Please try again.';
                errorMessage.style.display = 'block';
            }
        }
    }).render('#paypal-button-container');
}

/**
 * Process document payment
 * @param {string} paymentId - PayPal payment ID
 */
function processDocumentPayment(paymentId) {
    const formId = document.getElementById('formId').value;
    const form = document.getElementById('paymentForm');
    
    // Add payment ID to form
    const paymentIdInput = document.createElement('input');
    paymentIdInput.type = 'hidden';
    paymentIdInput.name = 'paypal_payment_id';
    paymentIdInput.value = paymentId;
    form.appendChild(paymentIdInput);
    
    // Submit form
    form.submit();
}

/**
 * Process subscription payment
 * @param {string} paymentId - PayPal payment ID
 */
function processSubscriptionPayment(paymentId) {
    const plan = document.getElementById('subscriptionPlan').value;
    
    // Create form data
    const formData = new FormData();
    formData.append('plan', plan);
    formData.append('payment_method', 'paypal');
    formData.append('payment_id', paymentId);
    
    // Submit to server
    fetch('/pricing', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        } else {
            return response.json();
        }
    })
    .then(data => {
        if (data && data.error) {
            throw new Error(data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        const errorMessage = document.getElementById('paymentError');
        if (errorMessage) {
            errorMessage.textContent = 'An error occurred while processing your subscription. Please contact support.';
            errorMessage.style.display = 'block';
        }
    });
}

/**
 * Handle subscription form submission
 * @param {Event} e - Form submit event
 */
function handleSubscriptionSubmit(e) {
    e.preventDefault();
    
    const plan = document.querySelector('input[name="plan"]:checked').value;
    if (!plan) {
        alert('Please select a subscription plan.');
        return;
    }
    
    // Set the selected plan and show payment options
    document.getElementById('subscriptionPlan').value = plan;
    document.getElementById('selectedPlanName').textContent = getPlanName(plan);
    document.getElementById('selectedPlanPrice').textContent = getPlanPrice(plan);
    
    // Show payment section
    document.getElementById('planSelection').style.display = 'none';
    document.getElementById('paymentSection').style.display = 'block';
    
    // Initialize PayPal for the subscription
    document.getElementById('paymentAmount').value = getPlanPrice(plan, true);
    document.getElementById('paymentItemName').value = `SmartDispute.ai ${getPlanName(plan)} Subscription`;
    document.getElementById('paymentType').value = 'subscription';
    
    // Initialize PayPal buttons
    initializePayPal();
}

/**
 * Get the name of a subscription plan
 * @param {string} plan - Plan identifier
 * @return {string} Plan name
 */
function getPlanName(plan) {
    const planNames = {
        'pay_per_doc': 'Pay-Per-Document',
        'unlimited': 'Unlimited',
        'low_income': 'Low Income Access'
    };
    
    return planNames[plan] || 'Subscription';
}

/**
 * Get the price of a subscription plan
 * @param {string} plan - Plan identifier
 * @param {boolean} rawValue - Whether to return raw value or formatted string
 * @return {string|number} Plan price
 */
function getPlanPrice(plan, rawValue = false) {
    const planPrices = {
        'pay_per_doc': 'CA$5.99 per document',
        'unlimited': 'CA$79.99 per month',
        'low_income': 'CA$25.00 per year'
    };
    
    const rawPrices = {
        'pay_per_doc': 5.99,
        'unlimited': 50.00,
        'low_income': 25.00
    };
    
    return rawValue ? rawPrices[plan] : planPrices[plan] || '';
}

/**
 * Toggle between monthly and annual pricing display
 */
function togglePricingPeriod() {
    const monthlyPrices = document.querySelectorAll('.price-monthly');
    const annualPrices = document.querySelectorAll('.price-annual');
    const isAnnual = document.getElementById('pricingToggle').checked;
    
    monthlyPrices.forEach(el => {
        el.style.display = isAnnual ? 'none' : 'block';
    });
    
    annualPrices.forEach(el => {
        el.style.display = isAnnual ? 'block' : 'none';
    });
}
