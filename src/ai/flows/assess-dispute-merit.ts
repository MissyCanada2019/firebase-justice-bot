import { ai } from '@/ai/genkit';
import { z } from 'genkit';

const AssessDisputeMeritInputSchema = z.object({
  classification: z.string().describe('The classification of the legal document.'),
  text: z.string().describe('The text content of the legal document.'),
  caseName: z.string().describe('The name of the case.'),
  disputeDetails: z.string().describe('The details of the dispute.'),
});
export type AssessDisputeMeritInput = z.infer<typeof AssessDisputeMeritInputSchema>;

const AssessDisputeMeritOutputSchema = z.object({
  meritScore: z.number().describe('A score from 0 to 100 representing the merit of the case.'),
  explanation: z.string().describe('An explanation of the strengths and weaknesses of the case.'),
  caseClassification: z.string().describe('The classification of the legal document.'),
  analysis: z.string().describe('A detailed analysis of the case.'),
  suggestedAvenues: z.string().describe('Suggested avenues for the user to take.'),
  caseName: z.string().describe('The name of the case.'),
});
export type AssessDisputeMeritOutput = z.infer<typeof AssessDisputeMeritOutputSchema>;

export async function assessDisputeMerit(input: AssessDisputeMeritInput): Promise<AssessDisputeMeritOutput> {
    return assessDisputeMeritFlow(input);
}

const prompt = ai.definePrompt({
    name: 'assessDisputeMeritPrompt',
    input: { schema: AssessDisputeMeritInputSchema },
    output: { schema: AssessDisputeMeritOutputSchema },
    system: `You are a legal analyst. Based on the provided document classification and text, assess the merit of the case and provide a score from 0 to 100, along with an explanation of the case's strengths and weaknesses.`,
    prompt: `
        Classification: {{{classification}}}
        Document Text:
        {{{text}}}
    `,
});

const assessDisputeMeritFlow = ai.defineFlow(
    {
        name: 'assessDisputeMeritFlow',
        inputSchema: AssessDisputeMeritInputSchema,
        outputSchema: AssessDisputeMeritOutputSchema,
    },
    async (input) => {
        const { output } = await prompt(input);
        return output!;
    }
);
