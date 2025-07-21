import * as admin from "firebase-admin";

admin.initializeApp();

import { onObjectFinalized } from "firebase-functions/v2/storage";

// Placeholder for the file processing function
export const processEvidence = onObjectFinalized({ cpu: "gcf_gen1" }, async (event) => {
  const filePath = event.data.name;
  console.log(`File uploaded: ${filePath}`);
  // Text extraction logic will be added here
});