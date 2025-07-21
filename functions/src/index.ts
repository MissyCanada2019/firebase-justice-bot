import * as admin from "firebase-admin";
import { onObjectFinalized } from "firebase-functions/v2/storage";
import { onDocumentCreated } from "firebase-functions/v2/firestore";
import { getStorage } from "firebase-admin/storage";
import { getFirestore } from "firebase-admin/firestore";
import { ImageAnnotatorClient } from "@google-cloud/vision";
import pdf from "pdf-parse";
import { runFlow } from "@genkit-ai/flow";
import { classifyDocumentFlow } from "../../src/ai/flows/classify-document";

admin.initializeApp();

const visionClient = new ImageAnnotatorClient();

async function extractText(filePath: string, contentType: string): Promise<string> {
  try {
    console.log("Downloading file from Cloud Storage...");
    const bucket = getStorage().bucket();
    const file = bucket.file(filePath);
    const [buffer] = await file.download();
    console.log("File downloaded successfully.");

    if (contentType.startsWith("image/")) {
      console.log("Extracting text from image...");
      const [result] = await visionClient.textDetection(buffer);
      console.log("Text extracted from image.");
      return result.fullTextAnnotation?.text || "";
    } else if (contentType === "application/pdf") {
      console.log("Extracting text from PDF...");
      const data = await pdf(buffer);
      console.log("Text extracted from PDF.");
      return data.text;
    } else {
      console.log(`Unsupported content type: ${contentType}`);
      return "";
    }
  } catch (error) {
    console.error("Error during text extraction:", error);
    return "";
  }
}

export const processEvidence = onObjectFinalized({ cpu: "gcf_gen1" }, async (event) => {
  try {
    console.log("Function triggered for file:", event.data.name);
    const { name: filePath, contentType } = event.data;

    if (!filePath.startsWith("evidence/")) {
      console.log("File is not in evidence folder, skipping.");
      return;
    }

    const text = await extractText(filePath, contentType || "");
    if (!text) {
      console.log("No text extracted.");
      return;
    }

    const classification = await runFlow(classifyDocumentFlow, text);

    const { suggestLegalForms } = await import("../../src/ai/flows/suggest-legal-forms");
    const { suggestedForms } = await suggestLegalForms({ classification, text });

    const { assessDisputeMerit } = await import("../../src/ai/flows/assess-dispute-merit");
    const docId = filePath.split("/").pop()?.split(".")[0];
    const { meritScore, explanation } = await assessDisputeMerit({ classification, text, caseName: docId || "", disputeDetails: text });

    const db = getFirestore();
    if (docId) {
      const userId = filePath.split("/")[1];
      console.log("Saving extracted text, classification, suggested forms, and merit score to Firestore...");
      await db.collection("extractedText").doc(docId).set({
        text: text,
        classification: classification,
        suggestedForms: suggestedForms,
        meritScore: meritScore,
        explanation: explanation,
        createdAt: admin.firestore.FieldValue.serverTimestamp(),
        userId: userId,
      });
      console.log("Successfully saved to Firestore.");
    }
  } catch (error) {
    console.error("An unexpected error occurred in the processEvidence function:", error);
  }
});

export const onEvidenceProcessed = onDocumentCreated("extractedText/{docId}", async (event) => {
  const snapshot = event.data;
  if (!snapshot) {
    console.log("No data associated with the event");
    return;
  }
  const data = snapshot.data();
  const userId = data.userId;

  const payload = {
    notification: {
      title: "Your Evidence has been Processed",
      body: "Your evidence has been successfully processed and is ready for review.",
    },
  };

  const db = getFirestore();
  const tokensSnapshot = await db.collection("users").doc(userId).collection("tokens").get();

  const tokens = tokensSnapshot.docs.map((doc) => doc.id);

  if (tokens.length > 0) {
    return admin.messaging().sendToDevice(tokens, payload);
  } else {
    console.log("No tokens for user", userId);
    return;
  }
});