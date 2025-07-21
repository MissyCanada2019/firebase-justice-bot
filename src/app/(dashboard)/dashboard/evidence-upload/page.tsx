"use client";

import { useEvidenceUploader } from "@/hooks/useEvidenceUploader";
import { FileUp, Loader2 } from "lucide-react";

export default function EvidenceUploadPage() {
  const {
    file,
    isDragging,
    isUploading,
    handleFileChange,
    handleDragOver,
    handleDragLeave,
    handleDrop,
    handleUpload,
  } = useEvidenceUploader();

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6 text-center">
        Upload Your Evidence
      </h1>
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors duration-200 ${
          isDragging ? "border-primary bg-primary/10" : "border-gray-300"
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          id="evidence-upload"
          type="file"
          onChange={handleFileChange}
          className="hidden"
          disabled={isUploading}
        />
        <label
          htmlFor="evidence-upload"
          className={`cursor-pointer flex flex-col items-center space-y-2 ${
            isUploading ? "cursor-not-allowed" : ""
          }`}
        >
          <FileUp className="w-12 h-12 text-gray-400" />
          <p className="text-gray-500">
            Drag and drop your file here, or click to select a file.
          </p>
        </label>
      </div>
      {file && (
        <div className="mt-6 text-center">
          <p className="font-semibold">Selected file:</p>
          <p className="text-gray-600">{file.name}</p>
        </div>
      )}
      <div className="mt-6 text-center">
        <button
          onClick={handleUpload}
          disabled={!file || isUploading}
          className="inline-flex items-center justify-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {isUploading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          {isUploading ? "Uploading..." : "Upload Evidence"}
        </button>
      </div>
    </div>
  );
}