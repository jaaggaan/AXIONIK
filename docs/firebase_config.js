// ============================================================================
// SHOPPERS STOP PLATFORM — FIREBASE FIRESTORE REAL-TIME INTEGRATION
// File: firebase_config.js
// Description: Real-time sync for Captive Portal Logins, Customer Registrations,
//              Coupon Redemptions, and Customer Feedbacks.
// ============================================================================

import { initializeApp } from "firebase/app";
import { 
  getFirestore, 
  collection, 
  doc, 
  setDoc, 
  addDoc, 
  onSnapshot, 
  query, 
  orderBy, 
  serverTimestamp 
} from "firebase/firestore";

// ----------------------------------------------------------------------------
// 1. YOUR FIREBASE API KEY CONFIGURATION (Replace with your actual key details)
// ----------------------------------------------------------------------------
const firebaseConfig = {
  apiKey: "YOUR_FIREBASE_API_KEY_HERE",
  authDomain: "shoppers-stop-portal.firebaseapp.com",
  projectId: "shoppers-stop-portal",
  storageBucket: "shoppers-stop-portal.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abcdef123456"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
export const db = getFirestore(app);

// ----------------------------------------------------------------------------
// 2. REAL-TIME DATA WRITING HELPERS (Used by Mobile Portal & POS)
// ----------------------------------------------------------------------------

/**
 * Save Customer Login / Visit from Mobile Phone or Captive Portal
 */
export async function saveCustomerVisit({ username, email, phone, storeLocation, orderType = "In-Store", loyaltyTier = "Silver" }) {
  try {
    const customerRef = doc(db, "customers", email);
    await setDoc(customerRef, {
      id: `FC-${Math.floor(10000 + Math.random() * 90000)}`,
      username: username,
      email: email,
      phone: phone,
      loyaltyTier: loyaltyTier,
      storeLocation: storeLocation,
      orderType: orderType, // "In-Store" or "Online"
      lastVisitAt: serverTimestamp(),
      updatedAt: serverTimestamp()
    }, { merge: true });

    console.log("✓ Customer registered/updated in Firebase Firestore:", email);
    return true;
  } catch (error) {
    console.error("❌ Firebase Save Customer Error:", error);
    return false;
  }
}

/**
 * Record Coupon Redemption by Customer
 */
export async function recordCouponRedemption({ couponCode, customerName, customerEmail, customerPhone, orderTotal, discountSaved, storeLocation }) {
  try {
    const redemptionRef = collection(db, "coupon_redemptions");
    await addDoc(redemptionRef, {
      couponCode: couponCode.toUpperCase(),
      customerName: customerName,
      customerEmail: customerEmail,
      customerPhone: customerPhone,
      orderId: `SS-ORD-${Math.floor(90000 + Math.random() * 9999)}`,
      orderTotal: orderTotal,
      discountSaved: discountSaved,
      storeLocation: storeLocation,
      redeemedAt: new Date().toLocaleString(),
      timestamp: serverTimestamp()
    });

    console.log("✓ Coupon Redemption saved in Firebase Firestore:", couponCode);
    return true;
  } catch (error) {
    console.error("❌ Firebase Record Redemption Error:", error);
    return false;
  }
}

/**
 * Submit Customer Feedback / Store Review
 */
export async function submitCustomerFeedback({ customerName, customerEmail, customerPhone, rating, title, comment, category, storeLocation, loyaltyTier = "Silver" }) {
  try {
    const feedbackRef = collection(db, "customer_feedbacks");
    await addDoc(feedbackRef, {
      customerName: customerName,
      customerEmail: customerEmail,
      customerPhone: customerPhone,
      loyaltyTier: loyaltyTier,
      storeLocation: storeLocation,
      category: category,
      rating: Number(rating),
      title: title,
      comment: comment,
      sentiment: rating >= 4 ? "Delighted" : rating === 3 ? "Positive" : "Needs Improvement",
      verifiedPurchase: true,
      managerResponse: null,
      createdAt: serverTimestamp(),
      date: new Date().toISOString().split("T")[0],
      time: new Date().toLocaleTimeString()
    });

    console.log("✓ Customer Feedback saved in Firebase Firestore:", customerName);
    return true;
  } catch (error) {
    console.error("❌ Firebase Submit Feedback Error:", error);
    return false;
  }
}

// ----------------------------------------------------------------------------
// 3. REAL-TIME DASHBOARD LISTENERS (Pushes updates directly to UI)
// ----------------------------------------------------------------------------

/**
 * Listen to Live Customer Registrations
 */
export function listenToCustomers(onUpdate) {
  const q = query(collection(db, "customers"), orderBy("lastVisitAt", "desc"));
  return onSnapshot(q, (snapshot) => {
    const customersList = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    onUpdate(customersList);
  });
}

/**
 * Listen to Live Coupon Redemptions
 */
export function listenToRedemptions(onUpdate) {
  const q = query(collection(db, "coupon_redemptions"), orderBy("timestamp", "desc"));
  return onSnapshot(q, (snapshot) => {
    const redemptionsList = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    onUpdate(redemptionsList);
  });
}

/**
 * Listen to Live Customer Feedbacks
 */
export function listenToFeedbacks(onUpdate) {
  const q = query(collection(db, "customer_feedbacks"), orderBy("createdAt", "desc"));
  return onSnapshot(q, (snapshot) => {
    const feedbacksList = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    onUpdate(feedbacksList);
  });
}
