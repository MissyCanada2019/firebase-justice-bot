import { defineFlow } from "@genkit-ai/flow";
import { z } from "zod";
import { gemini10Pro } from "@genkit-ai/googleai";
import { generate } from "@genkit-ai/ai";

export const classifyDocumentFlow = defineFlow(
  {
    name: "classifyDocumentFlow",
    inputSchema: z.string(),
    outputSchema: z.string(),
  },
  async (text: string) => {
    const prompt = `
      Please classify the following legal document text into one of the following categories:
      - Lease Agreement
      - Eviction Notice
      - Employment Contract
      - Pay Stub
      - Other

      Document Text:
      ${text}
    `;

    const llmResponse = await (generate as any)({
      prompt: prompt,
      model: gemini10Pro,
      config: {
        temperature: 0.1,
      },
    });

    return llmResponse.text();
  }
);