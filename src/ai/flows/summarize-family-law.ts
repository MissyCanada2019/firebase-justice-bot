// Summarizes Canadian family law and child protection laws for a given province or territory.
// - summarizeFamilyLaw - A function that summarizes the relevant laws.
// - SummarizeFamilyLawInput - The input type for the summarizeFamilyLaw function.
// - SummarizeFamilyLawOutput - The return type for the summarizeFamilyLaw function.

'use server';

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const SummarizeFamilyLawInputSchema = z.object({
  provinceOrTerritory: z
    .string() // Ideally, this would be an enum of provinces/territories
    .describe('The Canadian province or territory for which to summarize family law.'),
});
export type SummarizeFamilyLawInput = z.infer<typeof SummarizeFamilyLawInputSchema>;

const SummarizeFamilyLawOutputSchema = z.object({
  summary: z.string().describe('A summary of the family law and child protection laws for the specified province or territory.'),
});
export type SummarizeFamilyLawOutput = z.infer<typeof SummarizeFamilyLawOutputSchema>;

export async function summarizeFamilyLaw(input: SummarizeFamilyLawInput): Promise<SummarizeFamilyLawOutput> {
  return summarizeFamilyLawFlow(input);
}

const prompt = ai.definePrompt({
  name: 'summarizeFamilyLawPrompt',
  input: {schema: SummarizeFamilyLawInputSchema},
  output: {schema: SummarizeFamilyLawOutputSchema},
  prompt: `You are an expert in Canadian family law and child protection laws.  Provide a summary of the relevant laws for the following province or territory: {{{provinceOrTerritory}}}. Focus on information relevant to parents seeking to understand their rights and obligations.
`,
});

const summarizeFamilyLawFlow = ai.defineFlow(
  {
    name: 'summarizeFamilyLawFlow',
    inputSchema: SummarizeFamilyLawInputSchema,
    outputSchema: SummarizeFamilyLawOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
