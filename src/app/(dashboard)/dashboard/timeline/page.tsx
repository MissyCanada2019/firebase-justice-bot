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
  generateLegalTimeline,
  GenerateLegalTimelineOutput,
} from '@/ai/flows/generate-legal-timeline';
import { AssessDisputeMeritOutput } from '@/ai/flows/assess-dispute-merit';
import { CalendarClock, Loader2, AlertCircle, Clock, FileText } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';

export default function TimelinePage() {
  const [assessment, setAssessment] = useState<AssessDisputeMeritOutput | null>(null);
  const [timeline, setTimeline] = useState<GenerateLegalTimelineOutput | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    try {
      if (typeof window !== 'undefined') {
        const storedAssessment = localStorage.getItem('caseAssessment');
        if (storedAssessment) {
          const parsedAssessment = JSON.parse(storedAssessment) as AssessDisputeMeritOutput;
          setAssessment(parsedAssessment);

          const fetchTimeline = async () => {
            try {
              const output = await generateLegalTimeline({
                caseClassification: parsedAssessment.caseClassification,
                disputeDetails: parsedAssessment.analysis, // Using analysis for context
              });
              setTimeline(output);
            } catch (err) {
              console.error(err);
              setError('Failed to generate the legal timeline. The AI may be experiencing high load. Please try again later.');
              toast({
                title: 'Timeline Generation Failed',
                description: 'An error occurred while generating the timeline.',
                variant: 'destructive',
              });
            } finally {
              setLoading(false);
            }
          };

          fetchTimeline();
        } else {
          setLoading(false);
        }
      }
    } catch (e) {
        console.error("Error reading from local storage", e);
        setError("Could not load your case data. Please submit your dispute again.");
        setLoading(false);
    }
  }, [toast]);

  if (loading) {
    return (
        <div className="space-y-8">
            <div className="flex items-center gap-4">
                <CalendarClock className="h-8 w-8 text-primary" />
                <div>
                <h1 className="text-3xl font-bold tracking-tight font-headline">
                    Generating Your Legal Timeline...
                </h1>
                <p className="text-muted-foreground">
                    The AI is building a step-by-step guide for your case.
                </p>
                </div>
            </div>
            <Card>
                <CardHeader>
                    <Skeleton className="h-6 w-1/2" />
                </CardHeader>
                <CardContent className="space-y-6">
                    <div className="flex gap-4">
                        <Skeleton className="h-10 w-10 rounded-full" />
                        <div className="flex-1 space-y-2">
                            <Skeleton className="h-4 w-1/4" />
                            <Skeleton className="h-4 w-full" />
                             <Skeleton className="h-4 w-3/4" />
                        </div>
                    </div>
                     <div className="flex gap-4">
                        <Skeleton className="h-10 w-10 rounded-full" />
                        <div className="flex-1 space-y-2">
                            <Skeleton className="h-4 w-1/4" />
                            <Skeleton className="h-4 w-full" />
                             <Skeleton className="h-4 w-3/4" />
                        </div>
                    </div>
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
          You need to submit a dispute for analysis before a timeline can be generated.
          <Button asChild className="mt-4">
            <Link href="/dashboard/submit-dispute">Submit a Dispute</Link>
          </Button>
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-8">
        {assessment && (
            <div className="flex items-center gap-4">
                <CalendarClock className="h-8 w-8 text-primary" />
                <div>
                <h1 className="text-3xl font-bold tracking-tight font-headline">
                    Your Legal Timeline
                </h1>
                <p className="text-muted-foreground">
                    A step-by-step guide for your <span className="font-semibold text-primary">{assessment.caseClassification}</span> case.
                </p>
                </div>
            </div>
        )}

        {error && (
            <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
            </Alert>
        )}

        {timeline && (
            <div className="space-y-8">
                {timeline.timeline.map((step, index) => (
                     <div key={index} className="flex gap-x-4 md:gap-x-8">
                        {/* Icon/Number Column */}
                        <div className="relative flex-shrink-0">
                            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary text-primary-foreground ring-8 ring-background">
                                <span className="text-xl font-bold">{index + 1}</span>
                            </div>
                            {index < timeline.timeline.length - 1 && (
                                <div className="absolute left-1/2 top-12 h-full w-0.5 -translate-x-1/2 bg-border" />
                            )}
                        </div>

                        {/* Content Column */}
                        <div className="flex-grow pt-1 pb-8">
                            <h3 className="text-2xl font-bold font-headline">{step.title}</h3>
                             <div className="flex items-center text-sm text-muted-foreground gap-2 mt-1 mb-4">
                                <Clock className="h-4 w-4" />
                                <span>Estimated Duration: {step.expectedDuration}</span>
                            </div>
                            <p className="text-foreground/90 whitespace-pre-wrap mb-6">{step.description}</p>
                            {step.forms && step.forms.length > 0 && (
                                <div className="bg-muted/50 p-4 rounded-lg">
                                    <h4 className="font-semibold flex items-center gap-2 mb-2 text-base">
                                        <FileText className="h-5 w-5" />
                                        Relevant Forms
                                    </h4>
                                    <div className="flex flex-wrap gap-2">
                                        {step.forms.map((form, formIndex) => (
                                            <Badge key={formIndex} variant="secondary" className="text-sm">{form}</Badge>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        )}
    </div>
  );
}
