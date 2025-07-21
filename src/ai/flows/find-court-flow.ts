import { ai } from '@/ai/genkit';
import { z } from 'genkit';

const FindCourtInputSchema = z.object({
  issueType: z.string().describe('The type of legal issue (e.g., "Landlord/Tenant", "Small Claims").'),
  postalCode: z.string().describe('The user\'s postal code.'),
});
export type FindCourtInput = z.infer<typeof FindCourtInputSchema>;

const FindCourtOutputSchema = z.object({
    venue: z.string().describe('The suggested legal venue (e.g., "Landlord and Tenant Board", "Small Claims Court").'),
    address: z.string().describe('The address of the courthouse or tribunal.'),
});
export type FindCourtOutput = z.infer<typeof FindCourtOutputSchema>;

export async function findCourt(input: FindCourtInput): Promise<FindCourtOutput> {
    return findCourtFlow(input);
}

const prompt = ai.definePrompt({
    name: 'findCourtPrompt',
    input: { schema: FindCourtInputSchema },
    output: { schema: FindCourtOutputSchema },
    system: `You are a legal assistant. Based on the user's issue type and postal code, determine the correct legal venue and provide its address.`,
    prompt: `
        Issue Type: {{{issueType}}}
        Postal Code: {{{postalCode}}}
    `,
});

const findCourtFlow = ai.defineFlow(
    {
        name: 'findCourtFlow',
        inputSchema: FindCourtInputSchema,
        outputSchema: FindCourtOutputSchema,
    },
    async (input) => {
        const { output } = await prompt(input);
        return output!;
    }
);
