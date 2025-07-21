"use client";

import { useState } from "react";
import { useAuth } from "@/hooks/use-auth";
import { storage } from "@/lib/firebase";
import { ref, uploadBytes } from "firebase/storage";

export default function EvidenceUploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const { user } = useAuth();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (file && user) {
      const storageRef = ref(storage, `evidence/${user.uid}/${file.name}`);
      try {
        await uploadBytes(storageRef, file);
        alert("File uploaded successfully!");
      } catch (error) {
        console.error("Error uploading file:", error);
        alert("Error uploading file.");
      }
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Upload Your Evidence</h1>
      <div className="flex items-center space-x-4">
        <label htmlFor="evidence-upload" className="sr-only">
          Choose a file
        </label>
        <input id="evidence-upload" type="file" onChange={handleFileChange} />
        <button
          onClick={handleUpload}
          disabled={!file || !user}
          className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-400"
        >
          Upload Evidence
        </button>
      </div>
    </div>
  );
}