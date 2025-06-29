// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getFirestore } from "firebase/firestore";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyCn3qzndrLKMLii0qniBnP-b2cpEfoVJXQ",
  authDomain: "beth-personal-assistant.firebaseapp.com",
  projectId: "beth-personal-assistant",
  storageBucket: "beth-personal-assistant.appspot.com",
  messagingSenderId: "309066386510",
  appId: "1:309066386510:web:b72739ee34be384ad5c71f",
  measurementId: "G-BG8FRNWLJ2"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Analytics only on client side
let analytics;
if (typeof window !== 'undefined') {
  analytics = getAnalytics(app);
}

const db = getFirestore(app);

// Export what we need
export { db };