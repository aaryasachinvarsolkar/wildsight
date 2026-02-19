import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getAnalytics } from "firebase/analytics";

// Config hardcoded as temporary fix for blank screen / .env load issue
const firebaseConfig = {
    apiKey: "AIzaSyA5oRLaw5CalRQbxCGacRf6FbV7MhbX4lA",
    authDomain: "wildsight-1efbc.firebaseapp.com",
    projectId: "wildsight-1efbc",
    storageBucket: "wildsight-1efbc.firebasestorage.app",
    messagingSenderId: "217008383696",
    appId: "1:217008383696:web:5198f302446f6b785020d5",
    measurementId: "G-65WZWFPCEK"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const analytics = typeof window !== 'undefined' ? getAnalytics(app) : null;

export { auth, analytics };
export default app;
