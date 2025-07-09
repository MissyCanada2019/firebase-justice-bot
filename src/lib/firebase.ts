import { getApp, getApps, initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

const firebaseConfig = {
  apiKey: "AIzaSyCg2ZAL_nPz1TOIzQY8DOLID_zd7vpMHLg",
  authDomain: "justicebotai.firebaseapp.com",
  projectId: "justicebotai",
  storageBucket: "justicebotai.firebasestorage.app",
  messagingSenderId: "259991262013",
  appId: "1:259991262013:web:32a1e42fa3484e9a676b54",
  measurementId: "G-GN30KPMDCH"
};


// Initialize Firebase
const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
const auth = getAuth(app);

// Analytics initialization has been temporarily removed to ensure stable deployment.
// It can be re-enabled later if needed, but requires careful client-side handling.

export { app, auth };
