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
    const bucket = (0, storage_2.getStorage)().bucket();
    const file = bucket.file(filePath);
    const [buffer] = await file.download();
    if (contentType.startsWith("image/")) {
        const [result] = await visionClient.textDetection(buffer);
        return ((_a = result.fullTextAnnotation) === null || _a === void 0 ? void 0 : _a.text) || "";
    }
    else if (contentType === "application/pdf") {
        const data = await pdf(buffer);
        return data.text;
    }
    else {
        console.log(`Unsupported content type: ${contentType}`);
        return "";
    }
}
exports.processEvidence = (0, storage_1.onObjectFinalized)({ cpu: "gcf_gen1" }, async (event) => {
    var _a;
    console.log("Function triggered for file:", event.data.name);
    const { name: filePath, contentType } = event.data;
    if (!filePath.startsWith("evidence/")) {
        console.log("File is not in evidence folder, skipping.");
        return;
    }
    console.log("Starting text extraction...");
    const text = await extractText(filePath, contentType || "");
    if (!text) {
        console.log("No text extracted.");
        return;
    }
    console.log("Text extraction successful.");
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
});
//# sourceMappingURL=index.js.map