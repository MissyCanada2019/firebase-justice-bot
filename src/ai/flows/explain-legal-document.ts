'use server';
/**
 * @fileOverview Explains a legal document in plain language.
 *
 * - explainLegalDocument - A function that handles the explanation of a legal document.
 * - ExplainLegalDocumentInput - The input type for the explainLegalDocument function.
 * - ExplainLegalDocumentOutput - The return type for the explainLegalDocument function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

export const ExplainLegalDocumentInputSchema = z.object({
  documentText: z
    .string()
    .describe('The text content of the legal document to be explained.'),
});
export type ExplainLegalDocumentInput = z.infer<typeof ExplainLegalDocumentInputSchema>;

const ExplainedSectionSchema = z.object({
    sectionTitle: z.string().describe("The title or a brief summary of this section of the legal document (e.g., 'Section 5: Obligations of the Tenant', 'What This Form is For')."),
    explanation: z.string().describe("A clear, plain-language explanation of what this section means, its implications for the user, and any key terms to be aware of."),
});

export const ExplainLegalDocumentOutputSchema = z.object({
    explanations: z.array(ExplainedSectionSchema).describe('An array of explained sections from the document.'),
});
export type ExplainLegalDocumentOutput = z.infer<typeof ExplainLegalDocumentOutputSchema>;

export async function explainLegalDocument(input: ExplainLegalDocumentInput): Promise<ExplainLegalDocumentOutput> {
  return explainLegalDocumentFlow(input);
}

const prompt = ai.definePrompt({
  name: 'explainLegalDocumentPrompt',
  input: {schema: ExplainLegalDocumentInputSchema},
  output: {schema: ExplainLegalDocumentOutputSchema},
  system: `You are an expert Canadian legal assistant AI named JusticeBot. Your purpose is to demystify complex legal documents for users who are not lawyers.

Analyze the provided document text and break it down into its core sections. For each section, you must provide:
1.  A clear title that summarizes what the section is about.
2.  A plain-language explanation of what the section means. Avoid legal jargon. Explain what the user is being asked to do, agree to, or what rights they have. Highlight any critical points or potential risks.

Structure your response as an array of explained sections.
`,
  prompt: `Please explain the following legal document:

{{{documentText}}}
`,
});

const explainLegalDocumentFlow = ai.defineFlow(
  {
    name: 'explainLegalDocumentFlow',
    inputSchema: ExplainLegalDocumentInputSchema,
    outputSchema: ExplainLegalDocumentOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
