import { NextRequest, NextResponse } from "next/server";
import { storage } from "../../../lib/firebase";
import { ref, uploadBytes } from "firebase/storage";
import { getAuth, DecodedIdToken } from "firebase-admin/auth";
import { adminApp } from "../../../lib/firebase-admin";

const FILE_FORM_DATA_KEY = "file";
const AUTH_HEADER_KEY = "Authorization";
const STORAGE_PATH_PREFIX = "evidence";

/**
 * Verifies the Firebase ID token and returns the user's UID.
 * @param idToken The Firebase ID token from the Authorization header.
 * @returns A promise that resolves with the user's UID.
 * @throws An error if the token is invalid or verification fails.
 */
async function getAuthenticatedUid(idToken: string): Promise<string> {
  if (!adminApp) {
    throw new Error("Firebase admin app not initialized");
  }
  try {
    const decodedToken: DecodedIdToken = await getAuth(adminApp).verifyIdToken(idToken);
    return decodedToken.uid;
  } catch (error) {
    console.error("Error verifying Firebase ID token:", error);
    throw new Error("Invalid authentication token.");
  }
}

export async function POST(req: NextRequest) {
  try {
    const authHeader = req.headers.get(AUTH_HEADER_KEY);
    const idToken = authHeader?.split("Bearer ")[1];

    if (!idToken) {
      return NextResponse.json({ error: "Unauthorized: Missing authentication token." }, { status: 401 });
    }

    const uid = await getAuthenticatedUid(idToken);

    const formData = await req.formData();
    const file = formData.get(FILE_FORM_DATA_KEY);

    if (!file || !(file instanceof File)) {
      return NextResponse.json({ error: "Bad Request: No file provided or invalid file format." }, { status: 400 });
    }

    const storageRef = ref(storage, `${STORAGE_PATH_PREFIX}/${uid}/${file.name}`);

    // Upload the file directly. `uploadBytes` can handle File objects (as Blobs),
    // which avoids loading the entire file into memory with `file.arrayBuffer()`.
    await uploadBytes(storageRef, file, {
      contentType: file.type,
    });

    return NextResponse.json({ message: "File uploaded successfully." });
  } catch (error) {
    console.error("File upload failed:", error);
    const errorMessage = error instanceof Error ? error.message : "An unknown error occurred.";
    
    if (errorMessage.includes("Invalid authentication token")) {
        return NextResponse.json({ error: `Unauthorized: ${errorMessage}` }, { status: 401 });
    }

    return NextResponse.json({ error: `Internal Server Error: ${errorMessage}` }, { status: 500 });
  }
}