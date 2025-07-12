
'use server';
/**
 * @fileOverview Provides a conversational chat interface for users.
 *
 * - conversationalChat - A function that handles a user's chat message.
 * - ConversationalChatInput - The input type for the function.
 * - ConversationalChatOutput - The return type for the function.
 */

import { ai } from '@/ai/genkit';
import { z } from 'genkit';
import { AssessDisputeMeritOutputSchema } from './assess-dispute-merit'; // Re-use existing schema

const ChatMessageSchema = z.object({
  role: z.enum(['user', 'bot']),
  content: z.string(),
});

export const ConversationalChatInputSchema = z.object({
  question: z.string().describe("The user's latest message or question."),
  caseContext: AssessDisputeMeritOutputSchema.optional().describe(
    'The full context of the user\'s assessed case, if available.'
  ),
  chatHistory: z
    .array(ChatMessageSchema)
    .optional()
    .describe('The history of the conversation so far.'),
});
export type ConversationalChatInput = z.infer<typeof ConversationalChatInputSchema>;

export const ConversationalChatOutputSchema = z.object({
  answer: z.string().describe('The AI\'s response to the user\'s question.'),
});
export type ConversationalChatOutput = z.infer<typeof ConversationalChatOutputSchema>;

export async function conversationalChat(
  input: ConversationalChatInput
): Promise<ConversationalChatOutput> {
  return conversationalChatFlow(input);
}

const prompt = ai.definePrompt({
  name: 'conversationalChatPrompt',
  input: { schema: ConversationalChatInputSchema },
  output: { schema: ConversationalChatOutputSchema },
  system: `You are JusticeBot, a helpful and empathetic AI legal assistant for Canada. Your goal is to assist users by answering their questions in plain, easy-to-understand language.

- If the user provides case context, use it as the primary source of truth to answer their questions. Refer to their case classification, merit score, and suggested avenues.
- If there is a chat history, maintain the context of the conversation.
- If there is no case context, you can answer general questions about Canadian law, but you must include a disclaimer that you are not a lawyer and this is not legal advice.
- Always be supportive and encouraging. The legal system is stressful, and your role is to be a helpful guide.
- Do not invent facts or legal advice. If you don't know the answer, say so.
`,
  prompt: `{{#if caseContext}}
Case Context:
- Case Name: {{{caseContext.caseName}}}
- Classification: {{{caseContext.caseClassification}}}
- Merit Score: {{{caseContext.meritScore}}}/100
- Analysis & Next Steps: {{{caseContext.analysis}}} - {{{caseContext.suggestedAvenues}}}
{{/if}}

Chat History:
{{#each chatHistory}}
{{#if (eq role 'user')}}User: {{content}}{{/if}}
{{#if (eq role 'bot')}}JusticeBot: {{content}}{{/if}}
{{/each}}

New Question from User:
{{{question}}}

Please provide a helpful and direct response to the user's new question based on the provided context and history.
`,
});

const conversationalChatFlow = ai.defineFlow(
  {
    name: 'conversationalChatFlow',
    inputSchema: ConversationalChatInputSchema,
    outputSchema: ConversationalChatOutputSchema,
  },
  async (input) => {
    const { output } = await prompt(input);
    return output!;
  }
);
