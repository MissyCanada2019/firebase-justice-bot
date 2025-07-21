import { ai } from '@/ai/genkit';
import { z } from 'genkit';

const SuggestLegalFormsInputSchema = z.object({
  classification: z.string().describe('The classification of the legal document.'),
  text: z.string().describe('The text content of the legal document.'),
});
export type SuggestLegalFormsInput = z.infer<typeof SuggestLegalFormsInputSchema>;

const SuggestLegalFormsOutputSchema = z.object({
    suggestedForms: z.array(z.string()).describe('A list of suggested legal forms.'),
});
export type SuggestLegalFormsOutput = z.infer<typeof SuggestLegalFormsOutputSchema>;

export async function suggestLegalForms(input: SuggestLegalFormsInput): Promise<SuggestLegalFormsOutput> {
    return suggestLegalFormsFlow(input);
}

const prompt = ai.definePrompt({
    name: 'suggestLegalFormsPrompt',
    input: { schema: SuggestLegalFormsInputSchema },
    output: { schema: SuggestLegalFormsOutputSchema },
    system: `You are a helpful legal assistant. Based on the provided document classification and text, suggest relevant legal forms.`,
    prompt: `
        Classification: {{{classification}}}
        Document Text:
        {{{text}}}
    `,
});

const suggestLegalFormsFlow = ai.defineFlow(
    {
        name: 'suggestLegalFormsFlow',
        inputSchema: SuggestLegalFormsInputSchema,
        outputSchema: SuggestLegalFormsOutputSchema,
    },
    async (input) => {
        const { output } = await prompt(input);
        return output!;
    }
);