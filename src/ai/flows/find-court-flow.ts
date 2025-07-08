'use server';
/**
 * @fileOverview Finds the appropriate courthouse and legal aid clinics based on a postal code and case type.
 *
 * - findCourtAndAid - A function that handles finding the court and aid.
 * - FindCourtAndAidInput - The input type for the findCourtAndAid function.
 * - FindCourtAndAidOutput - The return type for the findCourtAndAid function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

export const FindCourtAndAidInputSchema = z.object({
  postalCode: z.string().describe('The user\'s postal code in Canada.'),
  caseClassification: z
    .string()
    .describe('The classification of the legal issue (e.g., "Landlord/Tenant Dispute", "Family Law - Custody").'),
});
export type FindCourtAndAidInput = z.infer<typeof FindCourtAndAidInputSchema>;

const LegalAidClinicSchema = z.object({
    name: z.string().describe('The name of the legal aid clinic.'),
    address: z.string().describe('The full address of the clinic.'),
    notes: z.string().optional().describe('Any relevant notes, like "Specializes in family law".')
});

export const FindCourtAndAidOutputSchema = z.object({
    courthouse: z.object({
        name: z.string().describe('The name of the most appropriate courthouse or tribunal.'),
        address: z.string().describe('The full address of the courthouse or tribunal.'),
        filingMethods: z.string().describe('A summary of how to file documents at this location (e.g., "Online portal, in-person at the clerk\'s office.").'),
        rulesLink: z.string().url().optional().describe('A URL to the specific rules for that court or tribunal, if available.'),
    }),
    legalAidClinics: z.array(LegalAidClinicSchema).describe('A list of nearby legal aid clinics that may be able to assist.')
});
export type FindCourtAndAidOutput = z.infer<typeof FindCourtAndAidOutputSchema>;

export async function findCourtAndAid(input: FindCourtAndAidInput): Promise<FindCourtAndAidOutput> {
  return findCourtAndAidFlow(input);
}

const prompt = ai.definePrompt({
  name: 'findCourtAndAidPrompt',
  input: {schema: FindCourtAndAidInputSchema},
  output: {schema: FindCourtAndAidOutputSchema},
  system: `You are an expert Canadian legal assistant AI named JusticeBot. Your purpose is to help users find the correct venue for their legal dispute and locate legal aid resources.

Based on the user's postal code and the type of legal case:
1.  **Identify the Correct Courthouse/Tribunal**: Determine the specific court (e.g., Superior Court of Justice - Family Court) or tribunal (e.g., Landlord and Tenant Board) for the given 'caseClassification'.
2.  **Find the Nearest Location**: Based on the postal code, find the address of the nearest physical location for that court/tribunal.
3.  **Provide Filing Information**: Summarize the typical ways to file documents at that venue and provide a link to the official rules if possible.
4.  **Locate Legal Aid**: Find up to three legal aid clinics or services in the vicinity of the provided postal code that could be relevant to the user's case type.
`,
  prompt: `Please find the correct court and nearby legal aid for the following:

Case Type: {{{caseClassification}}}
Postal Code: {{{postalCode}}}
`,
});

const findCourtAndAidFlow = ai.defineFlow(
  {
    name: 'findCourtAndAidFlow',
    inputSchema: FindCourtAndAidInputSchema,
    outputSchema: FindCourtAndAidOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
