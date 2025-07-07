'use server';
/**
 * @fileOverview Assesses a legal dispute and provides a merit score.
 *
 * - assessDisputeMerit - A function that handles the dispute assessment.
 * - AssessDisputeMeritInput - The input type for the assessDisputeMerit function.
 * - AssessDisputeMeritOutput - The return type for the assessDisputeMerit function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

export const AssessDisputeMeritInputSchema = z.object({
  caseName: z.string().describe('A short, descriptive name for the case.'),
  disputeDetails: z
    .string()
    .describe('A detailed description of the legal issue, including key events, dates, and people involved.'),
  evidenceText: z
    .string()
    .optional()
    .describe('The extracted text content from an uploaded evidence document.'),
});
export type AssessDisputeMeritInput = z.infer<typeof AssessDisputeMeritInputSchema>;

export const AssessDisputeMeritOutputSchema = z.object({
  meritScore: z
    .number()
    .min(0)
    .max(100)
    .describe(
      'A score from 0 to 100 indicating the merit of the case based on the provided information. A higher score means a stronger case.'
    ),
  caseClassification: z
    .string()
    .describe('The classification of the legal issue (e.g., "Landlord/Tenant Dispute", "Family Law - Custody", "Small Claims").'),
  suggestedAvenues: z
    .string()
    .describe(
      'A summary of recommended next steps and proper avenues for the user to take, such as which forms to file and at which type of courthouse.'
    ),
    analysis: z.string().describe('A brief analysis explaining the reasoning for the merit score and suggested avenues.')
});
export type AssessDisputeMeritOutput = z.infer<typeof AssessDisputeMeritOutputSchema>;

export async function assessDisputeMerit(input: AssessDisputeMeritInput): Promise<AssessDisputeMeritOutput> {
  return assessDisputeMeritFlow(input);
}

const prompt = ai.definePrompt({
  name: 'assessDisputeMeritPrompt',
  input: {schema: AssessDisputeMeritInputSchema},
  output: {schema: AssessDisputeMeritOutputSchema},
  system: `You are an expert Canadian legal assistant AI named JusticeBot. Your purpose is to provide an initial assessment of a user's legal dispute to help them understand its strength and potential next steps. You do not provide legal advice.

Analyze the user's case name, dispute details, and any provided evidence text. Based on this information:
1.  **Classify the Case**: Determine the area of law (e.g., LTB, Family, Criminal, Small Claims).
2.  **Assess Merit**: Evaluate the strength of the case based on the facts provided. Assign a merit score from 0 (very low merit) to 100 (very high merit). Consider clarity, evidence, and potential legal standing.
3.  **Provide a Brief Analysis**: Explain your reasoning for the score in simple terms.
4.  **Suggest Avenues**: Recommend concrete next steps for a self-represented litigant in the relevant Canadian province. Mention specific form types (e.g., T2 for tenant rights, Form 8A for a divorce application) and the type of court or tribunal they need to engage with (e.g., Landlord and Tenant Board, Superior Court of Justice).
`,
  prompt: `Please assess the following legal dispute:

Case Name: {{{caseName}}}

Dispute Details:
{{{disputeDetails}}}

{{#if evidenceText}}
Evidence Document Text:
{{{evidenceText}}}
{{/if}}
`,
});

const assessDisputeMeritFlow = ai.defineFlow(
  {
    name: 'assessDisputeMeritFlow',
    inputSchema: AssessDisputeMeritInputSchema,
    outputSchema: AssessDisputeMeritOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
