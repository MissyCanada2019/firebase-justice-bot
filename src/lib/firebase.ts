import { getApp, getApps, initializeApp } from 'firebase/app';
import { getAnalytics, isSupported } from 'firebase/analytics';
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

// Conditionally initialize Analytics only on the client side
if (typeof window !== 'undefined') {
    isSupported().then(supported => {
        if (supported) {
            getAnalytics(app);
        }
    });
}


export { app, auth };
