import { ai } from '@/ai/genkit';
import { z } from 'genkit';

const GenerateLegalTimelineInputSchema = z.object({
  formType: z.string().describe('The type of legal form (e.g., "T2 Application").'),
});
export type GenerateLegalTimelineInput = z.infer<typeof GenerateLegalTimelineInputSchema>;

const TimelineStepSchema = z.object({
  step: z.number().describe('The step number in the timeline.'),
  title: z.string().describe('The title of the step.'),
  description: z.string().describe('A description of the step.'),
  deadline: z.string().optional().describe('The deadline for the step.'),
});

const GenerateLegalTimelineOutputSchema = z.object({
    timeline: z.array(TimelineStepSchema).describe('A timeline of steps for filing the legal form.'),
});
export type GenerateLegalTimelineOutput = z.infer<typeof GenerateLegalTimelineOutputSchema>;

export async function generateLegalTimeline(input: GenerateLegalTimelineInput): Promise<GenerateLegalTimelineOutput> {
    return generateLegalTimelineFlow(input);
}

const prompt = ai.definePrompt({
    name: 'generateLegalTimelinePrompt',
    input: { schema: GenerateLegalTimelineInputSchema },
    output: { schema: GenerateLegalTimelineOutputSchema },
    system: `You are a legal assistant. Based on the provided form type, generate a timeline of steps for filing the legal form. Include instructions for service, deadlines, fees, and what to expect at hearings.`,
    prompt: `
        Form Type: {{{formType}}}
    `,
});

const generateLegalTimelineFlow = ai.defineFlow(
    {
        name: 'generateLegalTimelineFlow',
        inputSchema: GenerateLegalTimelineInputSchema,
        outputSchema: GenerateLegalTimelineOutputSchema,
    },
    async (input) => {
        const { output } = await prompt(input);
        return output!;
    }
);
