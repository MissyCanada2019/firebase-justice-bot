/**
 * Analytics Module for SmartDispute.ai
 * 
 * This module handles Google Analytics integration and custom event tracking
 */

// Initialize Google Analytics
function initGoogleAnalytics(trackingId) {
  if (!trackingId) {
    console.warn('Google Analytics tracking ID not provided');
    return;
  }
  
  // Load Google Analytics script
  const script = document.createElement('script');
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${trackingId}`;
  document.head.appendChild(script);
  
  // Initialize Google Analytics
  window.dataLayer = window.dataLayer || [];
  function gtag() { dataLayer.push(arguments); }
  gtag('js', new Date());
  gtag('config', trackingId);
  
  // Store the gtag function globally
  window.gtag = gtag;
  
  console.log('Google Analytics initialized');
}

// Track a custom event
function trackEvent(eventName, eventParams = {}) {
  if (!window.gtag) {
    console.warn('Google Analytics not initialized');
    return;
  }
  
  // Track the event
  window.gtag('event', eventName, eventParams);
  console.log(`Event tracked: ${eventName}`, eventParams);
}

// Track a page view
function trackPageView(pagePath) {
  if (!window.gtag) {
    console.warn('Google Analytics not initialized');
    return;
  }
  
  // Track the page view
  window.gtag('config', window.GOOGLE_ANALYTICS_ID, {
    'page_path': pagePath || window.location.pathname
  });
  console.log(`Page view tracked: ${pagePath || window.location.pathname}`);
}

// Track a form submission
function trackFormSubmission(formName, formData = {}) {
  trackEvent('form_submission', {
    'form_name': formName,
    ...formData
  });
}

// Track a document upload
function trackDocumentUpload(documentType, fileSize) {
  trackEvent('document_upload', {
    'document_type': documentType,
    'file_size': fileSize
  });
}

// Track a login
function trackLogin(loginMethod) {
  trackEvent('login', {
    'method': loginMethod
  });
}

// Track a signup
function trackSignup(signupMethod) {
  trackEvent('signup', {
    'method': signupMethod
  });
}

// Track a payment
function trackPayment(amount, paymentMethod) {
  trackEvent('payment', {
    'amount': amount,
    'payment_method': paymentMethod
  });
}

// Export the functions
window.Analytics = {
  initGoogleAnalytics,
  trackEvent,
  trackPageView,
  trackFormSubmission,
  trackDocumentUpload,
  trackLogin,
  trackSignup,
  trackPayment
};

// Initialize analytics when the page loads
document.addEventListener('DOMContentLoaded', function() {
  // The tracking ID should be set in the window object by the server
  if (window.GOOGLE_ANALYTICS_ID) {
    initGoogleAnalytics(window.GOOGLE_ANALYTICS_ID);
    
    // Track the initial page view
    trackPageView();
    
    // Track subsequent page views (for single-page applications)
    window.addEventListener('popstate', function() {
      trackPageView();
    });
  }
});
