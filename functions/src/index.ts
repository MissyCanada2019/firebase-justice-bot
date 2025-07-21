import * as admin from "firebase-admin";
import { onObjectFinalized } from "firebase-functions/v2/storage";
import { getStorage } from "firebase-admin/storage";
import { getFirestore } from "firebase-admin/firestore";
import { ImageAnnotatorClient } from "@google-cloud/vision";
import * as pdf from "pdf-parse";

admin.initializeApp();

const visionClient = new ImageAnnotatorClient();

async function extractText(filePath: string, contentType: string): Promise<string> {
  const bucket = getStorage().bucket();
  const file = bucket.file(filePath);
  const [buffer] = await file.download();

  if (contentType.startsWith("image/")) {
    const [result] = await visionClient.textDetection(buffer);
    return result.fullTextAnnotation?.text || "";
  } else if (contentType === "application/pdf") {
    const data = await pdf(buffer);
    return data.text;
  } else {
    console.log(`Unsupported content type: ${contentType}`);
    return "";
  }
}

export const processEvidence = onObjectFinalized({ cpu: "gcf_gen1" }, async (event) => {
  const { name: filePath, contentType } = event.data;

  if (!filePath.startsWith("evidence/")) {
    return;
  }

  const text = await extractText(filePath, contentType || "");
  if (!text) {
    console.log("No text extracted.");
    return;
  }

  const db = getFirestore();
  const docId = filePath.split("/").pop()?.split(".")[0];
  if (docId) {
    await db.collection("extractedText").doc(docId).set({
      text: text,
      createdAt: admin.firestore.FieldValue.serverTimestamp(),
    });
  }
});