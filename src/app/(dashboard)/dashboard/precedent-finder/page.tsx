
'use client';

import { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import {
  findPrecedents,
  FindPrecedentsOutput,
} from '@/ai/flows/find-precedents-flow';
import { AssessDisputeMeritOutput } from '@/ai/flows/assess-dispute-merit';
import { Library, Loader2, AlertCircle, Scale } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { useAuth } from '@/hooks/use-auth';
import { getLatestCaseAssessment } from '@/lib/firestoreService';

export default function PrecedentFinderPage() {
  const [assessment, setAssessment] = useState<AssessDisputeMeritOutput | null>(null);
  const [result, setResult] = useState<FindPrecedentsOutput | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();
  const { user } = useAuth();

  useEffect(() => {
    const loadDataAndFetch = async () => {
      if (!user) {
        setLoading(false);
        return;
      }
      
      try {
        const storedAssessment = await getLatestCaseAssessment(user.uid);
        if (storedAssessment) {
          setAssessment(storedAssessment);
          const output = await findPrecedents({
            caseClassification: storedAssessment.caseClassification,
            disputeDetails: storedAssessment.analysis,
          });
          setResult(output);
        }
      } catch (err: any) {
        console.error(err);
        setError('Failed to find precedents. The AI may be experiencing high load. Please try again later.');
        toast({
          title: 'Precedent Search Failed',
          description: err.message || 'An error occurred while finding similar cases.',
          variant: 'destructive',
        });
      } finally {
        setLoading(false);
      }
    };

    loadDataAndFetch();
  }, [user, toast]);

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="flex items-center gap-4">
          <Library className="h-8 w-8 text-primary" />
          <div>
            <h1 className="text-3xl font-bold tracking-tight font-headline">
              Finding Similar Cases...
            </h1>
            <p className="text-muted-foreground">The AI is searching for relevant precedents from CanLII.</p>
          </div>
        </div>
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-1/2" />
          </CardHeader>
          <CardContent className="space-y-6">
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!assessment && !loading) {
    return (
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>No Case Data Found</AlertTitle>
        <AlertDescription>
          You need to submit a dispute for analysis before we can find similar cases.
          <Button asChild className="mt-4">
            <Link href="/dashboard/submit-dispute">Submit a Dispute</Link>
          </Button>
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-4">
        <Library className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-3xl font-bold tracking-tight font-headline">CanLII Precedent Finder</h1>
          <p className="text-muted-foreground">
            Compare your case to similar ones from the Canadian Legal Information Institute.
          </p>
        </div>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {result && (
        <>
            <Card className="border-accent">
                <CardHeader>
                    <CardTitle className="font-headline text-xl flex items-center gap-2">
                        <Scale className="h-5 w-5"/>
                        Outcome Analysis
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <p className="text-muted-foreground">{result.outcomeAnalysis}</p>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>Relevant Precedent Cases</CardTitle>
                    <CardDescription>Click on each case to see the summary and details.</CardDescription>
                </CardHeader>
                <CardContent>
                    <Accordion type="single" collapsible className="w-full">
                        {result.precedentCases.map((item, index) => (
                            <AccordionItem value={`item-${index}`} key={index}>
                            <AccordionTrigger className="text-lg font-headline">
                                <div>
                                    {item.caseName}
                                    <p className="text-sm font-mono text-muted-foreground font-normal">{item.citation}</p>
                                </div>
                            </AccordionTrigger>
                            <AccordionContent className="space-y-4 text-base">
                                <div>
                                    <h4 className="font-semibold text-sm">Relevance Summary</h4>
                                    <p className="text-foreground/90">{item.summary}</p>
                                </div>
                                 <div>
                                    <h4 className="font-semibold text-sm">Legal Test / Principle Applied</h4>
                                    <p className="text-foreground/90">{item.legalTestApplied}</p>
                                </div>
                                <div>
                                    <h4 className="font-semibold text-sm">Outcome</h4>
                                    <p className="text-foreground/90">{item.outcome}</p>
                                </div>
                            </AccordionContent>
                            </AccordionItem>
                        ))}
                    </Accordion>
                </CardContent>
            </Card>
        </>
      )}
    </div>
  );
}
