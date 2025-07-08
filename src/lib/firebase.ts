import { initializeApp, getApps, getApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

// =================================================================================
// TROUBLESHOOTING GUIDE: 'auth/auth-domain-config-required'
// =================================================================================
// This error means you need to add your app's URL to Firebase's "Authorized
// Domains" list. This is a security step.
//
// === Domains to Add ===
// 1. For the live app:  studio--justicebotai.us-central1.hosted.app
// 2. For local testing: localhost
//
// === Where to Find "Authorized Domains" in the Firebase Console ===
// The location can vary. Please check these places in order:
//
// 1. Standard Location:
//    - Go to "Authentication" in the left menu.
//    - Click the "Settings" tab.
//    - Scroll down. "Authorized domains" should be listed there.
//
// 2. Identity Platform Location (if your project uses it):
//    - In the left menu's "Build" section, click on "Identity Platform" (it's
//      a separate product from Authentication).
//    - In the Identity Platform section, go to the "Settings" tab.
//    - You should find the "Authorized domains" list there.
//
// Once you find the list, click "Add domain" and add the URLs from above.
// This is a one-time setup step.
// =================================================================================

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
};

// Initialize Firebase
const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
const auth = getAuth(app);

export { app, auth };
