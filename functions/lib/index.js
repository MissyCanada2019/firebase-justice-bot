"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.processEvidence = void 0;
const admin = require("firebase-admin");
const storage_1 = require("firebase-functions/v2/storage");
const storage_2 = require("firebase-admin/storage");
const firestore_1 = require("firebase-admin/firestore");
const vision_1 = require("@google-cloud/vision");
const pdf = require("pdf-parse");
const core_1 = require("@genkit-ai/core");
const googleai_1 = require("@genkit-ai/googleai");
const firebase_1 = require("@genkit-ai/firebase");
admin.initializeApp();
const visionClient = new vision_1.ImageAnnotatorClient();
(0, firebase_1.configure)({
    plugins: [(0, googleai_1.googleAI)()],
    model: "googleai/gemini-1.5-flash-latest",
});
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
    const { name: filePath, contentType } = event.data;
    if (!filePath.startsWith("evidence/")) {
        return;
    }
    const text = await extractText(filePath, contentType || "");
    if (!text) {
        console.log("No text extracted.");
        return;
    }
    const analysis = await (0, core_1.generate)({
        prompt: `Analyze the following legal document and provide a summary, identify the document type, and suggest potential legal actions: ${text}`,
    });
    const db = (0, firestore_1.getFirestore)();
    const docId = (_a = filePath.split("/").pop()) === null || _a === void 0 ? void 0 : _a.split(".")[0];
    if (docId) {
        await db.collection("evidenceAnalysis").doc(docId).set({
            analysis: analysis.text(),
            createdAt: admin.firestore.FieldValue.serverTimestamp(),
        });
    }
});
//# sourceMappingURL=index.js.map