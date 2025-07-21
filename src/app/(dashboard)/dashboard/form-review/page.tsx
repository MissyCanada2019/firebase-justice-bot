"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/hooks/use-auth";
import { getFirestore, doc, getDoc } from "firebase/firestore";
import { jsPDF } from "jspdf";

// This is a placeholder for a subscription check
const hasActiveSubscription = async (userId: string) => {
  console.log(`Checking subscription for user ${userId}...`);
  return true;
};

export default function FormReviewPage() {
  const { user } = useAuth();
  const [formContent, setFormContent] = useState<string | null>(null);
  const [canDownload, setCanDownload] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      const db = getFirestore();
      // This is just an example, you'll need to get the docId from the generated form
      const docId = "some-form-id";
      const docRef = doc(db, "generatedForms", docId);

      getDoc(docRef)
        .then((docSnap) => {
          if (docSnap.exists()) {
            setFormContent(docSnap.data().content);
          } else {
            console.log("No such document!");
          }
          setLoading(false);
        })
        .catch((error) => {
          console.error("Error getting document:", error);
          setLoading(false);
        });

      hasActiveSubscription(user.uid).then((subscribed) => {
        setCanDownload(subscribed);
      });
    }
  }, [user]);

  const handleDownload = () => {
    if (formContent) {
      const doc = new jsPDF();
      doc.text(formContent, 10, 10);
      doc.save("completed-form.pdf");
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6 text-center">Review Your Form</h1>
      <div className="prose lg:prose-xl mx-auto">
        {formContent ? (
          <div dangerouslySetInnerHTML={{ __html: formContent }} />
        ) : (
          <p>No form content available.</p>
        )}
      </div>
      <div className="mt-8 text-center">
        <button
          onClick={handleDownload}
          disabled={!canDownload}
          className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 disabled:bg-gray-400"
        >
          {canDownload ? "Download PDF" : "Subscription Required"}
        </button>
      </div>
    </div>
  );
}