// src/ai/flows/analyze-legal-document.ts
'use server';

/**
 * @fileOverview Analyzes legal documents and provides references to the Canadian Charter of Rights and Freedoms.
 *
 * - analyzeLegalDocument - A function that handles the analysis of a legal document.
 * - AnalyzeLegalDocumentInput - The input type for the analyzeLegalDocument function.
 * - AnalyzeLegalDocumentOutput - The return type for the analyzeLegalDocument function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const AnalyzeLegalDocumentInputSchema = z.object({
  documentText: z
    .string()
    .describe('The text content of the legal document to be analyzed.'),
});
export type AnalyzeLegalDocumentInput = z.infer<typeof AnalyzeLegalDocumentInputSchema>;

const AnalyzeLegalDocumentOutputSchema = z.object({
  analysis: z
    .string()
    .describe(
      'An analysis of the legal document, referencing relevant sections of the Canadian Charter of Rights and Freedoms.'
    ),
  relevantCharterSections: z
    .array(z.string())
    .describe('A list of relevant sections from the Canadian Charter of Rights and Freedoms.'),
});
export type AnalyzeLegalDocumentOutput = z.infer<typeof AnalyzeLegalDocumentOutputSchema>;

export async function analyzeLegalDocument(input: AnalyzeLegalDocumentInput): Promise<AnalyzeLegalDocumentOutput> {
  return analyzeLegalDocumentFlow(input);
}

const charterReferenceTool = ai.defineTool({
  name: 'getCharterSection',
  description: 'Retrieves a specific section of the Canadian Charter of Rights and Freedoms.',
  inputSchema: z.object({
    sectionNumber: z.string().describe('The section number of the Charter to retrieve (e.g., 2b).'),
  }),
  outputSchema: z.string(),
}, async (input) => {
  // This is a placeholder; in a real application, this would fetch
  // the actual Charter section from a database or external source.
  const charterSections: { [key: string]: string } = {
    '2b': '2b. Everyone has the following fundamental freedoms: freedom of thought, belief, opinion and expression, including freedom of the press and other media of communication.',
    '7': '7. Everyone has the right to life, liberty and security of the person and the right not to be deprived thereof except in accordance with the principles of fundamental justice.',
    '8': '8. Everyone has the right to be secure against unreasonable search or seizure.',
    '9': '9. Everyone has the right not to be arbitrarily detained or imprisoned.',
    '10': '10. Everyone has the right on arrest or detention (a) to be informed promptly of the reasons therefor; (b) to retain and instruct counsel without delay and to be informed of that right; and (c) to have the validity of the detention determined by way of habeas corpus and to be released if the detention is not lawful.',
    '11': '11. Any person charged with an offence has the right (a) to be informed without unreasonable delay of the specific offence; (b) to be tried within a reasonable time; (c) not to be compelled to be a witness in proceedings against that person in respect of that offence; (d) to be presumed innocent until proven guilty according to law in a fair and public hearing by an independent and impartial tribunal; (e) not to be denied reasonable bail without just cause;
(f) except in the case of an offence under military law tried before a military tribunal, to the benefit of trial by jury where the maximum punishment for the offence is imprisonment for five years or a more severe punishment; (g) not to be found guilty on account of any act or omission unless, at the time of the act or omission, it constituted an offence under Canadian or international law or was criminal according to the general principles of law recognized by civilized nations; (h) if finally acquitted of the offence, not to be tried for it again and, if finally found guilty and punished for the offence, not to be tried or punished for it again; and (i) if found guilty of the offence and if the punishment for the offence has been varied between the time of commission and the time of sentence, to the benefit of the lesser punishment.',
  };

  const section = charterSections[input.sectionNumber];
  if (!section) {
    return `Charter Section ${input.sectionNumber} not found.`;
  }
  return section;
});

const prompt = ai.definePrompt({
  name: 'analyzeLegalDocumentPrompt',
  input: {schema: AnalyzeLegalDocumentInputSchema},
  output: {schema: AnalyzeLegalDocumentOutputSchema},
  tools: [charterReferenceTool],
  system: `You are a legal expert specializing in the Canadian Charter of Rights and Freedoms.

  Analyze the provided legal document and identify any potential violations or relevant sections of the Charter.

  If the document raises questions related to specific Charter sections, use the 'getCharterSection' tool to retrieve the content of those sections and include them in your analysis.

  Provide a detailed analysis of the document and a list of potentially relevant Charter sections.
  `,
  prompt: `Legal Document:
{{{documentText}}}`, // removed media, don't pass a data URI here.
});

const analyzeLegalDocumentFlow = ai.defineFlow(
  {
    name: 'analyzeLegalDocumentFlow',
    inputSchema: AnalyzeLegalDocumentInputSchema,
    outputSchema: AnalyzeLegalDocumentOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
