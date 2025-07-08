import { config } from 'dotenv';
config();

import '@/ai/flows/analyze-legal-document.ts';
import '@/ai/flows/summarize-family-law.ts';
import '@/ai/flows/summarize-criminal-law.ts';
import '@/ai/flows/summarize-ltb-law.ts';
import '@/ai/flows/assess-dispute-merit.ts';
import '@/ai/flows/generate-legal-timeline.ts';
import '@/ai/flows/generate-legal-form.ts';
import '@/ai/flows/explain-legal-document.ts';
