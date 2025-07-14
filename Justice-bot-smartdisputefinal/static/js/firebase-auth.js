/**
 * Firebase Authentication Integration for SmartDispute.ai
 * Using Firebase v9+ modular SDK for better performance
 */

// Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyAjd5ekT45EOPr7D-KvSZt-EPwaOk0BQUE",
    authDomain: "legallysmart.firebaseapp.com",
    projectId: "legallysmart",
    storageBucket: "legallysmart.firebasestorage.app",
    messagingSenderId: "1077200418820",
    appId: "1:1077200418820:web:aca47450b47ed258df1d51",
    measurementId: "G-3N4JD9CRXY"
};

// Firebase app and services (will be initialized when SDK loads)
let app;
let auth;
let analytics;

class FirebaseAuthManager {
    constructor() {
        this.user = null;
        this.initializeFirebase();
    }

    async initializeFirebase() {
        try {
            // Wait for Firebase SDK to load
            await this.loadFirebaseSDK();
            
            // Initialize Firebase using v9+ modular SDK
            const { initializeApp, getAuth, onAuthStateChanged, getAnalytics } = window.firebaseModules;
            
            app = initializeApp(firebaseConfig);
            auth = getAuth(app);
            
            // Initialize Analytics if available
            try {
                analytics = getAnalytics(app);
            } catch (e) {
                console.log('Analytics not available:', e.message);
            }

            // Set up auth state listener
            onAuthStateChanged(auth, (user) => {
                this.handleAuthStateChange(user);
            });

            console.log('Firebase initialized successfully');
        } catch (error) {
            console.error('Firebase initialization error:', error);
        }
    }

    async loadFirebaseSDK() {
        return new Promise((resolve, reject) => {
            // Check if Firebase v9+ is already loaded
            if (window.firebase && window.firebase.initializeApp) {
                resolve();
                return;
            }

            // Load Firebase v9+ modular SDK
            const script = document.createElement('script');
            script.type = 'module';
            script.innerHTML = `
                import { initializeApp } from 'https://www.gstatic.com/firebasejs/9.23.0/firebase-app.js';
                import { getAuth, GoogleAuthProvider, signInWithPopup, signOut, onAuthStateChanged } from 'https://www.gstatic.com/firebasejs/9.23.0/firebase-auth.js';
                import { getAnalytics, logEvent } from 'https://www.gstatic.com/firebasejs/9.23.0/firebase-analytics.js';
                
                // Make Firebase functions available globally
                window.firebaseModules = {
                    initializeApp,
                    getAuth,
                    GoogleAuthProvider,
                    signInWithPopup,
                    signOut,
                    onAuthStateChanged,
                    getAnalytics,
                    logEvent
                };
                
                // Signal that Firebase is loaded
                window.dispatchEvent(new Event('firebaseLoaded'));
            `;
            
            // Listen for Firebase loaded event
            window.addEventListener('firebaseLoaded', resolve, { once: true });
            
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    async signInWithGoogle() {
        try {
            const provider = new firebase.auth.GoogleAuthProvider();
            provider.addScope('email');
            provider.addScope('profile');
            
            const result = await auth.signInWithPopup(provider);
            const user = result.user;
            const idToken = await user.getIdToken();

            // Send to backend for session creation
            const response = await fetch('/auth/firebase-login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    idToken: idToken
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.showSuccess('Successfully signed in with Google');
                window.location.href = data.redirect_url || '/dashboard';
            } else {
                throw new Error(data.error || 'Authentication failed');
            }

        } catch (error) {
            console.error('Google sign-in error:', error);
            this.showError(error.message || 'Failed to sign in with Google');
        }
    }

    async signOut() {
        try {
            await auth.signOut();
            
            // Notify backend
            await fetch('/auth/firebase-logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            this.showSuccess('Successfully signed out');
            window.location.href = '/';

        } catch (error) {
            console.error('Sign out error:', error);
            this.showError('Failed to sign out');
        }
    }

    handleAuthStateChange(user) {
        this.user = user;
        
        if (user) {
            console.log('User signed in:', user.email);
            this.updateUIForSignedInUser(user);
            
            // Track authentication event
            if (analytics) {
                analytics.logEvent('login', {
                    method: 'google'
                });
            }
        } else {
            console.log('User signed out');
            this.updateUIForSignedOutUser();
        }
    }

    updateUIForSignedInUser(user) {
        // Update any UI elements for signed-in state
        const authStatus = document.getElementById('authStatus');
        if (authStatus) {
            authStatus.style.display = 'block';
            authStatus.innerHTML = `
                <div class="alert alert-success">
                    <i class="feather-check-circle me-2"></i>
                    Signed in as ${user.displayName || user.email}
                </div>
            `;
        }

        // Hide login buttons, show logout
        document.querySelectorAll('.google-signin-btn, .social-btn').forEach(btn => {
            btn.style.display = 'none';
        });
    }

    updateUIForSignedOutUser() {
        // Update any UI elements for signed-out state
        const authStatus = document.getElementById('authStatus');
        if (authStatus) {
            authStatus.style.display = 'none';
        }

        // Show login buttons
        document.querySelectorAll('.google-signin-btn, .social-btn').forEach(btn => {
            btn.style.display = 'block';
        });
    }

    showSuccess(message) {
        this.showMessage(message, 'success');
    }

    showError(message) {
        this.showMessage(message, 'danger');
    }

    showMessage(message, type) {
        const authStatus = document.getElementById('authStatus');
        if (authStatus) {
            authStatus.style.display = 'block';
            authStatus.innerHTML = `
                <div class="alert alert-${type} alert-dismissible fade show">
                    <i class="feather-${type === 'success' ? 'check-circle' : 'alert-triangle'} me-2"></i>
                    ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
        }
    }
}

// Initialize Firebase Auth Manager
let firebaseAuthManager;

document.addEventListener('DOMContentLoaded', () => {
    firebaseAuthManager = new FirebaseAuthManager();
    
    // Set up Google sign-in button handlers
    document.querySelectorAll('#googleSignInBtn, .google-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            firebaseAuthManager.signInWithGoogle();
        });
    });

    // Set up logout button handlers
    document.querySelectorAll('[data-action="logout"]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            firebaseAuthManager.signOut();
        });
    });
});