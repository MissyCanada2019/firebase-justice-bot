"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.processEvidence = void 0;
const admin = require("firebase-admin");
const storage_1 = require("firebase-functions/v2/storage");
const storage_2 = require("firebase-admin/storage");
const firestore_1 = require("firebase-admin/firestore");
const vision_1 = require("@google-cloud/vision");
const pdf = require("pdf-parse");
admin.initializeApp();
const visionClient = new vision_1.ImageAnnotatorClient();
async function extractText(filePath, contentType) {
    var _a;
    try {
        console.log("Downloading file from Cloud Storage...");
        const bucket = (0, storage_2.getStorage)().bucket();
        const file = bucket.file(filePath);
        const [buffer] = await file.download();
        console.log("File downloaded successfully.");
        if (contentType.startsWith("image/")) {
            console.log("Extracting text from image...");
            const [result] = await visionClient.textDetection(buffer);
            console.log("Text extracted from image.");
            return ((_a = result.fullTextAnnotation) === null || _a === void 0 ? void 0 : _a.text) || "";
        }
        else if (contentType === "application/pdf") {
            console.log("Extracting text from PDF...");
            const data = await pdf(buffer);
            console.log("Text extracted from PDF.");
            return data.text;
        }
        else {
            console.log(`Unsupported content type: ${contentType}`);
            return "";
        }
    }
    catch (error) {
        console.error("Error during text extraction:", error);
        return "";
    }
}
exports.processEvidence = (0, storage_1.onObjectFinalized)({ cpu: "gcf_gen1" }, async (event) => {
    var _a;
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
        const db = (0, firestore_1.getFirestore)();
        const docId = (_a = filePath.split("/").pop()) === null || _a === void 0 ? void 0 : _a.split(".")[0];
        if (docId) {
            console.log("Saving extracted text to Firestore...");
            await db.collection("extractedText").doc(docId).set({
                text: text,
                createdAt: admin.firestore.FieldValue.serverTimestamp(),
            });
            console.log("Successfully saved to Firestore.");
        }
    }
    catch (error) {
        console.error("An unexpected error occurred in the processEvidence function:", error);
    }
});
//# sourceMappingURL=index.js.map