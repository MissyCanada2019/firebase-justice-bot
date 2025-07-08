'use client';

import { useState, useEffect } from 'react';

export function ClientDate() {
  const [date, setDate] = useState('');

  useEffect(() => {
    // This ensures the date is only rendered on the client, after hydration.
    setDate(new Date().toLocaleDateString());
  }, []);

  if (!date) {
    // You can return a placeholder here if you like
    return null;
  }

  return <>{date}</>;
}
