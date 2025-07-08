'use client';

import { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  CardFooter,
} from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import {
  generateLegalForm,
  GenerateLegalFormOutput,
} from '@/ai/flows/generate-legal-form';
import { AssessDisputeMeritOutput } from '@/ai/flows/assess-dispute-merit';
import { FilePlus2, Loader2, AlertCircle, Download, FileText } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { Skeleton } from '@/components/ui/skeleton';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { useAuth } from '@/hooks/use-auth';

export default function GenerateFormPage() {
  const { user } = useAuth(); // We'll need this to check payment status later
  const [assessment, setAssessment] = useState<AssessDisputeMeritOutput | null>(null);
  const [formContent, setFormContent] = useState<GenerateLegalFormOutput | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    try {
      if (typeof window !== 'undefined') {
        const storedAssessment = localStorage.getItem('caseAssessment');
        if (storedAssessment) {
          const parsedAssessment = JSON.parse(storedAssessment) as AssessDisputeMeritOutput;
          setAssessment(parsedAssessment);
        }
      }
    } catch (e) {
        console.error("Error reading from local storage", e);
        setError("Could not load your case data. Please submit your dispute again.");
    }
  }, []);

  const handleGenerateClick = async () => {
    if (!assessment) {
        toast({
            title: 'No Case Data',
            description: 'Please submit a dispute before generating a form.',
            variant: 'destructive'
        });
        return;
    }
    setLoading(true);
    setError(null);
    setFormContent(null);
    try {
        const output = await generateLegalForm({
            caseClassification: assessment.caseClassification,
            disputeDetails: assessment.analysis, // Using analysis for better context
            suggestedAvenues: assessment.suggestedAvenues,
        });
        setFormContent(output);
    } catch (err) {
        console.error(err);
        setError('Failed to generate the form content. The AI may be experiencing high load. Please try again later.');
        toast({
            title: 'Form Generation Failed',
            description: 'An error occurred while generating the form.',
            variant: 'destructive',
        });
    } finally {
        setLoading(false);
    }
  }

  // Placeholder for checking download permissions.
  // In a real app, this would check user.role from a database.
  const canDownload = false; 

  if (!assessment && !loading) {
    return (
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>No Case Data Found</AlertTitle>
        <AlertDescription>
          You need to submit a dispute for analysis before a form can be generated.
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
            <FilePlus2 className="h-8 w-8 text-primary" />
            <div>
            <h1 className="text-3xl font-bold tracking-tight font-headline">
                AI Form Generator
            </h1>
            <p className="text-muted-foreground">
                Auto-fill legal forms based on your case details.
            </p>
            </div>
        </div>

        {assessment && !formContent && (
            <Card>
                <CardHeader>
                    <CardTitle>Ready to Generate Your Form?</CardTitle>
                    <CardDescription>
                        Based on your case assessment for <span className="font-semibold text-primary">{assessment.caseClassification}</span>, we can generate a draft of the relevant legal form.
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <p className="text-sm text-muted-foreground">
                        The AI will structure the information you provided into the standard sections of the legal form. You can review and edit the content before downloading.
                    </p>
                </CardContent>
                <CardFooter>
                    <Button onClick={handleGenerateClick} disabled={loading}>
                        {loading ? (
                            <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                Generating...
                            </>
                        ) : 'Generate Form Content'}
                    </Button>
                </CardFooter>
            </Card>
        )}

        {loading && (
            <Card>
                <CardHeader>
                    <Skeleton className="h-6 w-1/3" />
                    <Skeleton className="h-4 w-1/2" />
                </CardHeader>
                <CardContent className="space-y-6">
                    <div className="space-y-2">
                        <Skeleton className="h-4 w-[150px]" />
                        <Skeleton className="h-20 w-full" />
                    </div>
                     <div className="space-y-2">
                        <Skeleton className="h-4 w-[150px]" />
                        <Skeleton className="h-20 w-full" />
                    </div>
                </CardContent>
            </Card>
        )}
        
        {error && (
            <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
            </Alert>
        )}

        {formContent && (
            <Card className="border-primary">
                <CardHeader>
                    <CardTitle className="font-headline text-2xl">Generated Form: {formContent.suggestedForm}</CardTitle>
                    <CardDescription>
                        Below is a preview of your auto-filled form. Review each section carefully. This is not legal advice.
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    {formContent.formSections.map((section, index) => (
                        <Card key={index}>
                            <CardHeader>
                                <CardTitle className="text-lg flex items-center gap-2 font-headline">
                                    <FileText className="h-5 w-5"/>
                                    {section.sectionTitle}
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <p className="text-muted-foreground text-sm whitespace-pre-wrap">{section.sectionContent}</p>
                            </CardContent>
                        </Card>
                    ))}
                </CardContent>
                <CardFooter className="flex-wrap gap-4">
                    <TooltipProvider>
                        <Tooltip>
                            <TooltipTrigger asChild>
                                {/* The button is wrapped in a span for the tooltip to work when disabled */}
                                <span tabIndex={0}>
                                    <Button disabled={!canDownload}>
                                        <Download className="mr-2 h-4 w-4" />
                                        Download as PDF
                                    </Button>
                                </span>
                            </TooltipTrigger>
                            {!canDownload && (
                                <TooltipContent>
                                    <p>A one-time payment or subscription is required to download forms.</p>
                                </TooltipContent>
                            )}
                        </Tooltip>
                    </TooltipProvider>
                </CardFooter>
            </Card>
        )}
    </div>
  );
}
