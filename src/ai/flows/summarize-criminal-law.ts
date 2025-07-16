// Summarize Criminal Law Flow
'use server';

/**
 * @fileOverview Summarizes criminal laws for a given Canadian province or territory.
 *
 * - summarizeCriminalLaw - A function that takes a province/territory and returns a summary of relevant criminal laws.
 * - SummarizeCriminalLawInput - The input type for the summarizeCriminalLaw function.
 * - SummarizeCriminalLawOutput - The return type for the summarizeCriminalLaw function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const SummarizeCriminalLawInputSchema = z.object({
  provinceOrTerritory: z.string().describe('The Canadian province or territory for which to summarize criminal laws.'),
});
export type SummarizeCriminalLawInput = z.infer<typeof SummarizeCriminalLawInputSchema>;

const SummarizeCriminalLawOutputSchema = z.object({
  summary: z.string().describe('A summary of the relevant criminal laws for the specified province or territory.'),
});
export type SummarizeCriminalLawOutput = z.infer<typeof SummarizeCriminalLawOutputSchema>;

export async function summarizeCriminalLaw(input: SummarizeCriminalLawInput): Promise<SummarizeCriminalLawOutput> {
  return summarizeCriminalLawFlow(input);
}

const prompt = ai.definePrompt({
  name: 'summarizeCriminalLawPrompt',
  input: {schema: SummarizeCriminalLawInputSchema},
  output: {schema: SummarizeCriminalLawOutputSchema},
  prompt: `You are a legal expert specializing in Canadian criminal law.

  Summarize the relevant criminal laws for the following Canadian province or territory:

  {{{provinceOrTerritory}}}

  Provide a concise and informative summary.
  `,
});

const summarizeCriminalLawFlow = ai.defineFlow(
  {
    name: 'summarizeCriminalLawFlow',
    inputSchema: SummarizeCriminalLawInputSchema,
    outputSchema: SummarizeCriminalLawOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
