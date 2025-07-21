"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/hooks/use-auth";
import { getFirestore, doc, getDoc } from "firebase/firestore";

export default function MeritScorePage() {
  const { user } = useAuth();
  const [meritScore, setMeritScore] = useState<number | null>(null);
  const [explanation, setExplanation] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      const db = getFirestore();
      // This is just an example, you'll need to get the docId from the uploaded file
      const docId = "some-doc-id"; 
      const docRef = doc(db, "extractedText", docId);

      getDoc(docRef)
        .then((docSnap) => {
          if (docSnap.exists()) {
            const data = docSnap.data();
            setMeritScore(data.meritScore);
            setExplanation(data.explanation);
          } else {
            console.log("No such document!");
          }
          setLoading(false);
        })
        .catch((error) => {
          console.error("Error getting document:", error);
          setLoading(false);
        });
    }
  }, [user]);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6 text-center">Merit Score</h1>
      {meritScore !== null && explanation !== null ? (
        <div className="text-center">
          <p className="text-5xl font-bold">{meritScore}/100</p>
          <p className="mt-4 text-lg">{explanation}</p>
        </div>
      ) : (
        <p>No merit score available.</p>
      )}
    </div>
  );
}