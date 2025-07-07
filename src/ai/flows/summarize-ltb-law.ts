'use server';
/**
 * @fileOverview Summarizes Landlord Tenant Board (LTB) laws for a given Canadian province or territory.
 *
 * - summarizeLTBLaw - A function that summarizes LTB laws.
 * - SummarizeLTBLawInput - The input type for the summarizeLTBLaw function.
 * - SummarizeLTBLawOutput - The return type for the summarizeLTBLaw function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const SummarizeLTBLawInputSchema = z.object({
  provinceOrTerritory: z
    .string()
    .describe('The Canadian province or territory to summarize LTB laws for.'),
});
export type SummarizeLTBLawInput = z.infer<typeof SummarizeLTBLawInputSchema>;

const SummarizeLTBLawOutputSchema = z.object({
  summary: z
    .string()
    .describe('A summary of the Landlord Tenant Board (LTB) laws for the specified province or territory.'),
});
export type SummarizeLTBLawOutput = z.infer<typeof SummarizeLTBLawOutputSchema>;

export async function summarizeLTBLaw(input: SummarizeLTBLawInput): Promise<SummarizeLTBLawOutput> {
  return summarizeLTBLawFlow(input);
}

const prompt = ai.definePrompt({
  name: 'summarizeLTBLawPrompt',
  input: {schema: SummarizeLTBLawInputSchema},
  output: {schema: SummarizeLTBLawOutputSchema},
  prompt: `You are an expert in Canadian Landlord Tenant Board (LTB) laws.

  Summarize the LTB laws for the following Canadian province or territory:

  {{{provinceOrTerritory}}}

  Provide a concise summary that a landlord or tenant can use to understand their rights and obligations.`,
});

const summarizeLTBLawFlow = ai.defineFlow(
  {
    name: 'summarizeLTBLawFlow',
    inputSchema: SummarizeLTBLawInputSchema,
    outputSchema: SummarizeLTBLawOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
