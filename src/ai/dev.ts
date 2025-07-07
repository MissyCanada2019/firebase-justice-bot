import { config } from 'dotenv';
config();

import '@/ai/flows/analyze-legal-document.ts';
import '@/ai/flows/summarize-family-law.ts';
import '@/ai/flows/summarize-criminal-law.ts';
import '@/ai/flows/summarize-ltb-law.ts';