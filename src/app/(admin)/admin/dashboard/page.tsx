"use client";

import { useState } from "react";

export default function AdminDashboardPage() {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6 text-center">Admin Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-4 border rounded-lg">
          <h2 className="text-xl font-bold">Approve Low-Income Plans</h2>
          {/* Add UI for this feature here */}
        </div>
        <div className="p-4 border rounded-lg">
          <h2 className="text-xl font-bold">View Top Cases</h2>
          {/* Add UI for this feature here */}
        </div>
        <div className="p-4 border rounded-lg">
          <h2 className="text-xl font-bold">Moderate Flagged Content</h2>
          {/* Add UI for this feature here */}
        </div>
        <div className="p-4 border rounded-lg">
          <h2 className="text-xl font-bold">Toggle User Roles</h2>
          {/* Add UI for this feature here */}
        </div>
      </div>
    </div>
  );
}