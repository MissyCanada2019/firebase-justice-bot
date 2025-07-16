
'use server';
/**
 * @fileOverview Simulates a search of the CanLII database for relevant case precedents.
 *
 * - findPrecedents - A function that finds case precedents.
 * - FindPrecedentsInput - The input type for the findPrecedents function.
 * - FindPrecedentsOutput - The return type for the findPrecedents function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

export const FindPrecedentsInputSchema = z.object({
  caseClassification: z
    .string()
    .describe('The classification of the legal issue (e.g., "Landlord/Tenant Dispute", "Family Law - Custody").'),
  disputeDetails: z
    .string()
    .describe('A detailed description of the legal issue.'),
});
export type FindPrecedentsInput = z.infer<typeof FindPrecedentsInputSchema>;

const PrecedentCaseSchema = z.object({
    caseName: z.string().describe("The name of the case (e.g., 'Smith v. Jones')."),
    citation: z.string().describe("The neutral citation for the case (e.g., '2022 ONLTB 1234')."),
    summary: z.string().describe("A brief summary of the case's facts and why it's relevant to the user's situation."),
    outcome: z.string().describe("The outcome of the case (e.g., 'Tenant's application was granted.')."),
    legalTestApplied: z.string().describe("A key legal test or principle that was applied in the case."),
});

export const FindPrecedentsOutputSchema = z.object({
    precedentCases: z.array(PrecedentCaseSchema).describe('An array of relevant precedent cases from CanLII.'),
    outcomeAnalysis: z.string().describe("A high-level analysis of the precedents, summarizing common outcomes or key factors judges consider for this type of case."),
});
export type FindPrecedentsOutput = z.infer<typeof FindPrecedentsOutputSchema>;

export async function findPrecedents(input: FindPrecedentsInput): Promise<FindPrecedentsOutput> {
  return findPrecedentsFlow(input);
}

const prompt = ai.definePrompt({
  name: 'findPrecedentsPrompt',
  input: {schema: FindPrecedentsInputSchema},
  output: {schema: FindPrecedentsOutputSchema},
  system: `You are an expert Canadian legal researcher AI. Your task is to simulate a search of the CanLII legal database.

Based on the user's case classification and dispute details, you will:
1.  **Identify Relevant Precedents**: Find 3-5 real or highly plausible and representative Canadian case precedents. The cases should be relevant to the user's issue.
2.  **Extract Key Information**: For each case, provide its name, citation, a summary of its relevance, the final outcome, and the key legal test or principle that was used.
3.  **Analyze Outcomes**: Provide a brief, high-level analysis summarizing what these precedents suggest about how judges or adjudicators typically handle such cases.
`,
  prompt: `Please find CanLII precedents for the following case:

Case Classification: {{{caseClassification}}}

Dispute Details:
{{{disputeDetails}}}
`,
});

const findPrecedentsFlow = ai.defineFlow(
  {
    name: 'findPrecedentsFlow',
    inputSchema: FindPrecedentsInputSchema,
    outputSchema: FindPrecedentsOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
