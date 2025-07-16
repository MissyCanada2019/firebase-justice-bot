
// A simple localStorage-based service for managing subscription state.
// In a real-world app, this would be backed by a server and database.

const PURCHASES_KEY = 'justiceBotPurchases';

interface Purchases {
  activeSubscription: string | null;
  singlePurchases: number;
}

function getPurchases(): Purchases {
  if (typeof window === 'undefined') {
    return { activeSubscription: null, singlePurchases: 0 };
  }
  try {
    const item = window.localStorage.getItem(PURCHASES_KEY);
    return item ? JSON.parse(item) : { activeSubscription: null, singlePurchases: 0 };
  } catch (error) {
    console.error('Error reading from localStorage', error);
    return { activeSubscription: null, singlePurchases: 0 };
  }
}

function setPurchases(purchases: Purchases) {
   if (typeof window === 'undefined') return;
  try {
    window.localStorage.setItem(PURCHASES_KEY, JSON.stringify(purchases));
  } catch (error) {
    console.error('Error writing to localStorage', error);
  }
}

export function getActiveSubscription(): string | null {
  return getPurchases().activeSubscription;
}

export function setActiveSubscription(planId: string | null) {
  const purchases = getPurchases();
  purchases.activeSubscription = planId;
  setPurchases(purchases);
}

export function addSinglePurchase() {
  const purchases = getPurchases();
  purchases.singlePurchases += 1;
  setPurchases(purchases);
}

export function hasSinglePurchase(): boolean {
  return getPurchases().singlePurchases > 0;
}

export function useSinglePurchase(): boolean {
  const purchases = getPurchases();
  if (purchases.singlePurchases > 0) {
    purchases.singlePurchases -= 1;
    setPurchases(purchases);
    return true;
  }
  return false;
}
