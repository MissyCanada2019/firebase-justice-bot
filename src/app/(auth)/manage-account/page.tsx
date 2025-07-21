"use client";

import { useAuth } from "@/hooks/use-auth";
import {
  sendPasswordResetEmail,
  sendEmailVerification,
  getAuth,
} from "firebase/auth";

export default function ManageAccountPage() {
  const { user } = useAuth();

  const handlePasswordReset = () => {
    if (user && user.email) {
      const auth = getAuth();
      sendPasswordResetEmail(auth, user.email)
        .then(() => {
          alert("Password reset email sent!");
        })
        .catch((error) => {
          console.error("Error sending password reset email:", error);
          alert("Error sending password reset email.");
        });
    }
  };

  const handleEmailVerification = () => {
    if (user) {
      sendEmailVerification(user)
        .then(() => {
          alert("Verification email sent!");
        })
        .catch((error) => {
          console.error("Error sending verification email:", error);
          alert("Error sending verification email.");
        });
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6 text-center">Manage Account</h1>
      <div className="max-w-md mx-auto space-y-4">
        <button
          onClick={handlePasswordReset}
          disabled={!user}
          className="w-full px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 disabled:bg-gray-400"
        >
          Send Password Reset Email
        </button>
        <button
          onClick={handleEmailVerification}
          disabled={!user || user.emailVerified}
          className="w-full px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 disabled:bg-gray-400"
        >
          {user?.emailVerified ? "Email Verified" : "Send Verification Email"}
        </button>
      </div>
    </div>
  );
}