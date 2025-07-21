"use client";

import { useState } from "react";
import {
  generateLegalTimeline,
  GenerateLegalTimelineInput,
  GenerateLegalTimelineOutput,
} from "@/ai/flows/generate-legal-timeline";

export default function TimelinePage() {
  const [formType, setFormType] = useState("");
  const [timeline, setTimeline] = useState<GenerateLegalTimelineOutput["timeline"] | null>(null);
  const [loading, setLoading] = useState(false);

  const handleGenerateTimeline = async () => {
    setLoading(true);
    const input: GenerateLegalTimelineInput = { formType };
    const result = await generateLegalTimeline(input);
    setTimeline(result.timeline);
    setLoading(false);
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6 text-center">Filing Walkthrough</h1>
      <div className="max-w-md mx-auto">
        <div className="mb-4">
          <label htmlFor="formType" className="block text-sm font-medium text-gray-700">
            Form Type
          </label>
          <input
            type="text"
            id="formType"
            value={formType}
            onChange={(e) => setFormType(e.target.value)}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          />
        </div>
        <button
          onClick={handleGenerateTimeline}
          disabled={loading}
          className="w-full px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 disabled:bg-gray-400"
        >
          {loading ? "Generating..." : "Generate Timeline"}
        </button>
      </div>
      {timeline && (
        <div className="mt-8">
          <ol className="relative border-l border-gray-200 dark:border-gray-700">
            {timeline.map((step) => (
              <li key={step.step} className="mb-10 ml-4">
                <div className="absolute w-3 h-3 bg-gray-200 rounded-full mt-1.5 -left-1.5 border border-white dark:border-gray-900 dark:bg-gray-700"></div>
                <time className="mb-1 text-sm font-normal leading-none text-gray-400 dark:text-gray-500">
                  {step.deadline}
                </time>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  {step.title}
                </h3>
                <p className="mb-4 text-base font-normal text-gray-500 dark:text-gray-400">
                  {step.description}
                </p>
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}
