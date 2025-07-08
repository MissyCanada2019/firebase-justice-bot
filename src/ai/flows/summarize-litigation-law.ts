'use server';

/**
 * @fileOverview Summarizes litigation laws for a given Canadian province or territory.
 *
 * - summarizeLitigationLaw - A function that takes a province/territory and returns a summary of relevant litigation laws.
 * - SummarizeLitigationLawInput - The input type for the summarizeLitigationLaw function.
 * - SummarizeLitigationLawOutput - The return type for the summarizeLitigationLaw function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const SummarizeLitigationLawInputSchema = z.object({
  provinceOrTerritory: z.string().describe('The Canadian province or territory for which to summarize litigation laws.'),
});
export type SummarizeLitigationLawInput = z.infer<typeof SummarizeLitigationLawInputSchema>;

const SummarizeLitigationLawOutputSchema = z.object({
  summary: z.string().describe('A summary of the relevant litigation laws and civil procedures for the specified province or territory.'),
});
export type SummarizeLitigationLawOutput = z.infer<typeof SummarizeLitigationLawOutputSchema>;

export async function summarizeLitigationLaw(input: SummarizeLitigationLawInput): Promise<SummarizeLitigationLawOutput> {
  return summarizeLitigationLawFlow(input);
}

const prompt = ai.definePrompt({
  name: 'summarizeLitigationLawPrompt',
  input: {schema: SummarizeLitigationLawInputSchema},
  output: {schema: SummarizeLitigationLawOutputSchema},
  prompt: `You are a legal expert specializing in Canadian civil litigation procedures.

  Summarize the key aspects of litigation law and Rules of Civil Procedure for the following Canadian province or territory:

  {{{provinceOrTerritory}}}

  Provide a concise and informative summary covering topics like starting a lawsuit, the discovery process, motions, and trial preparation. This summary should be useful to a self-represented litigant.
  `,
});

const summarizeLitigationLawFlow = ai.defineFlow(
  {
    name: 'summarizeLitigationLawFlow',
    inputSchema: SummarizeLitigationLawInputSchema,
    outputSchema: SummarizeLitigationLawOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
