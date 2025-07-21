"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/hooks/use-auth";
import { getFirestore, collection, query, where, getDocs } from "firebase/firestore";

export default function CaseHistoryPage() {
  const { user } = useAuth();
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      const db = getFirestore();
      const q = query(collection(db, "extractedText"), where("userId", "==", user.uid));

      getDocs(q)
        .then((querySnapshot) => {
          const caseData = querySnapshot.docs.map((doc) => ({
            id: doc.id,
            ...doc.data(),
          }));
          setCases(caseData);
          setLoading(false);
        })
        .catch((error) => {
          console.error("Error getting documents: ", error);
          setLoading(false);
        });
    }
  }, [user]);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6 text-center">Case History</h1>
      <div className="space-y-4">
        {cases.map((caseItem) => (
          <div key={caseItem.id} className="p-4 border rounded-lg">
            <h2 className="text-xl font-bold">{caseItem.classification}</h2>
            <p>Merit Score: {caseItem.meritScore}/100</p>
            <p>Suggested Forms: {caseItem.suggestedForms.join(", ")}</p>
          </div>
        ))}
      </div>
    </div>
  );
}