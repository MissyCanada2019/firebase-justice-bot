"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.processEvidence = void 0;
const admin = require("firebase-admin");
admin.initializeApp();
const storage_1 = require("firebase-functions/v2/storage");
// Placeholder for the file processing function
exports.processEvidence = (0, storage_1.onObjectFinalized)({ cpu: "gcf_gen1" }, async (event) => {
    const filePath = event.data.name;
    console.log(`File uploaded: ${filePath}`);
    // Text extraction logic will be added here
});
//# sourceMappingURL=index.js.map