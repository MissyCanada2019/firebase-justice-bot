
'use server';
/**
 * @fileOverview Verifies a Google reCAPTCHA Enterprise token.
 *
 * - verifyRecaptchaToken - A function that handles the verification of a reCAPTCHA token.
 * - VerifyRecaptchaInput - The input type for the verifyRecaptchaToken function.
 * - VerifyRecaptchaOutput - The return type for the verifyRecaptchaToken function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';
import { GoogleAuth } from 'google-auth-library';


export const VerifyRecaptchaInputSchema = z.object({
  token: z.string().describe('The reCAPTCHA token generated on the client side.'),
  expectedAction: z.string().describe('The action expected for this token (e.g., "LOGIN").'),
});
export type VerifyRecaptchaInput = z.infer<typeof VerifyRecaptchaInputSchema>;

export const VerifyRecaptchaOutputSchema = z.object({
  isValid: z.boolean().describe('Whether the reCAPTCHA token is valid and the action matches.'),
  score: z.number().describe('The risk score from 0.0 to 1.0.'),
  reason: z.string().optional().describe('The reason for the assessment outcome.'),
});
export type VerifyRecaptchaOutput = z.infer<typeof VerifyRecaptchaOutputSchema>;

export async function verifyRecaptchaToken(input: VerifyRecaptchaInput): Promise<VerifyRecaptchaOutput> {
    return verifyRecaptchaFlow(input);
}

const verifyRecaptchaFlow = ai.defineFlow(
  {
    name: 'verifyRecaptchaFlow',
    inputSchema: VerifyRecaptchaInputSchema,
    outputSchema: VerifyRecaptchaOutputSchema,
  },
  async ({ token, expectedAction }) => {
    try {
        const projectId = process.env.GOOGLE_PROJECT_ID;
        const siteKey = process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY;

        if (!projectId) {
            throw new Error('GOOGLE_PROJECT_ID is not configured in environment variables.');
        }
        if (!siteKey) {
            throw new Error('NEXT_PUBLIC_RECAPTCHA_SITE_KEY is not configured in environment variables.');
        }

        const auth = new GoogleAuth({
            scopes: 'https://www.googleapis.com/auth/cloud-platform',
        });
        const client = await auth.getClient();
        const url = `https://recaptchaenterprise.googleapis.com/v1/projects/${projectId}/assessments`;
        
        const assessmentRequest = {
            assessment: {
                event: {
                    token: token,
                    siteKey: siteKey,
                    expectedAction: expectedAction,
                },
            },
        };

        const response = await client.request({
            url,
            method: 'POST',
            data: assessmentRequest,
        });
        
        const data = response.data as any;

        if (!data.tokenProperties || !data.tokenProperties.valid) {
            return { isValid: false, score: 0, reason: `Token validation failed: ${data.tokenProperties?.invalidReason}` };
        }
        
        if (data.tokenProperties.action !== expectedAction) {
             return { isValid: false, score: data.riskAnalysis?.score || 0, reason: `Mismatched action. Expected ${expectedAction} but got ${data.tokenProperties.action}` };
        }

        const score = data.riskAnalysis?.score || 0;
        // Consider scores > 0.5 as valid for this example. Adjust as needed.
        const isValid = score >= 0.5;

        return { isValid, score, reason: 'Assessment successful' };

    } catch (error: any) {
        console.error('reCAPTCHA verification error:', error.response?.data || error.message);
        return { isValid: false, score: 0, reason: `An error occurred during verification: ${error.message}` };
    }
  }
);
