'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import {
  explainLegalDocument,
  ExplainLegalDocumentOutput,
} from '@/ai/flows/explain-legal-document';
import { FileSearch, Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';

export default function DocumentExplainerPage() {
  const [documentText, setDocumentText] = useState('');
  const [result, setResult] = useState<ExplainLegalDocumentOutput | null>(null);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async () => {
    if (!documentText.trim()) {
      toast({
        title: 'Input Required',
        description: 'Please paste the text of your document to explain it.',
        variant: 'destructive',
      });
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const output = await explainLegalDocument({ documentText });
      setResult(output);
      toast({
        title: 'Explanation Ready!',
        description: 'The AI has explained your document below.',
      });
    } catch (error) {
      console.error(error);
      toast({
        title: 'Explanation Failed',
        description: 'An error occurred while explaining the document. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-4">
        <FileSearch className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-3xl font-bold tracking-tight font-headline">
            Document Explainer
          </h1>
          <p className="text-muted-foreground">
            Demystify legal documents. Get plain-language explanations for any text.
          </p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Document Text</CardTitle>
          <CardDescription>
            Paste the text of the legal document or form you want explained.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Textarea
            placeholder="Paste your legal document here..."
            className="min-h-[250px] text-base"
            value={documentText}
            onChange={(e) => setDocumentText(e.target.value)}
            disabled={loading}
          />
        </CardContent>
        <CardFooter>
          <Button onClick={handleSubmit} disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Explaining...
              </>
            ) : (
              'Explain Document'
            )}
          </Button>
        </CardFooter>
      </Card>

      {loading && (
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-1/3" />
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-4/5" />
            </div>
            <div className="space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-4/5" />
            </div>
          </CardContent>
        </Card>
      )}

      {result && result.explanations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Your Explained Document</CardTitle>
            <CardDescription>Click on each section to see its explanation.</CardDescription>
          </CardHeader>
          <CardContent>
            <Accordion type="single" collapsible className="w-full">
              {result.explanations.map((item, index) => (
                <AccordionItem value={`item-${index}`} key={index}>
                  <AccordionTrigger className="text-lg font-headline">{item.sectionTitle}</AccordionTrigger>
                  <AccordionContent className="whitespace-pre-wrap text-foreground/90 text-base">
                    {item.explanation}
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
