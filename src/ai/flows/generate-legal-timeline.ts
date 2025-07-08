'use server';
/**
 * @fileOverview Generates a legal timeline for a given case.
 *
 * - generateLegalTimeline - A function that generates a legal timeline.
 * - GenerateLegalTimelineInput - The input type for the generateLegalTimeline function.
 * - GenerateLegalTimelineOutput - The return type for the generateLegalTimeline function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

export const GenerateLegalTimelineInputSchema = z.object({
  caseClassification: z
    .string()
    .describe('The classification of the legal issue (e.g., "Landlord/Tenant Dispute", "Family Law - Custody").'),
   disputeDetails: z
    .string()
    .describe('A detailed description of the legal issue, including key events, dates, and people involved.'),
});
export type GenerateLegalTimelineInput = z.infer<typeof GenerateLegalTimelineInputSchema>;

const TimelineStepSchema = z.object({
    title: z.string().describe('The title of this step in the legal timeline (e.g., "Filing the Application").'),
    description: z.string().describe('A detailed, plain-language explanation of what this step involves, what the user needs to do, and what to expect.'),
    expectedDuration: z.string().describe('The estimated time this step might take (e.g., "1-2 weeks", "30-60 days").'),
    forms: z.array(z.string()).optional().describe('A list of specific forms that may need to be filed during this step (e.g., "Form T2", "Form 8A").'),
});

export const GenerateLegalTimelineOutputSchema = z.object({
    timeline: z.array(TimelineStepSchema).describe('A step-by-step timeline for the legal process.')
});
export type GenerateLegalTimelineOutput = z.infer<typeof GenerateLegalTimelineOutputSchema>;

export async function generateLegalTimeline(input: GenerateLegalTimelineInput): Promise<GenerateLegalTimelineOutput> {
  return generateLegalTimelineFlow(input);
}

const prompt = ai.definePrompt({
  name: 'generateLegalTimelinePrompt',
  input: {schema: GenerateLegalTimelineInputSchema},
  output: {schema: GenerateLegalTimelineOutputSchema},
  system: `You are an expert Canadian legal assistant AI named JusticeBot. Your purpose is to create a clear, step-by-step timeline for a user navigating the legal system.

Based on the case classification and dispute details, generate a typical legal timeline. The timeline should cover the process from the initial filing to the hearing and potential appeal window.

For each step, provide:
1.  A clear, action-oriented title.
2.  A detailed description in plain language of what the step involves.
3.  An estimated duration for the step.
4.  If applicable, a list of specific form names or numbers relevant to that step.

The timeline should be tailored to the Canadian legal context for the given case type.
`,
  prompt: `Please generate a legal timeline for the following case:

Case Classification: {{{caseClassification}}}

Dispute Details:
{{{disputeDetails}}}
`,
});

const generateLegalTimelineFlow = ai.defineFlow(
  {
    name: 'generateLegalTimelineFlow',
    inputSchema: GenerateLegalTimelineInputSchema,
    outputSchema: GenerateLegalTimelineOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
