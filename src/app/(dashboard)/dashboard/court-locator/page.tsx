"use client";

import { useState } from "react";
import { findCourt, FindCourtInput } from "@/ai/flows/find-court-flow";

export default function CourtLocatorPage() {
  const [issueType, setIssueType] = useState("");
  const [postalCode, setPostalCode] = useState("");
  const [venue, setVenue] = useState<string | null>(null);
  const [address, setAddress] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleFindCourt = async () => {
    setLoading(true);
    const input: FindCourtInput = { issueType, postalCode };
    const result = await findCourt(input);
    setVenue(result.venue);
    setAddress(result.address);
    setLoading(false);
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6 text-center">Court Locator</h1>
      <div className="max-w-md mx-auto">
        <div className="mb-4">
          <label htmlFor="issueType" className="block text-sm font-medium text-gray-700">
            Issue Type
          </label>
          <input
            type="text"
            id="issueType"
            value={issueType}
            onChange={(e) => setIssueType(e.target.value)}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          />
        </div>
        <div className="mb-4">
          <label htmlFor="postalCode" className="block text-sm font-medium text-gray-700">
            Postal Code
          </label>
          <input
            type="text"
            id="postalCode"
            value={postalCode}
            onChange={(e) => setPostalCode(e.target.value)}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          />
        </div>
        <button
          onClick={handleFindCourt}
          disabled={loading}
          className="w-full px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 disabled:bg-gray-400"
        >
          {loading ? "Finding..." : "Find Court"}
        </button>
      </div>
      {venue && address && (
        <div className="mt-8 text-center">
          <h2 className="text-2xl font-bold">{venue}</h2>
          <p className="mt-2">{address}</p>
        </div>
      )}
    </div>
  );
}
