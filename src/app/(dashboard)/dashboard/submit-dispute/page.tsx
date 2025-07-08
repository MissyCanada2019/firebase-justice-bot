'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { FileText, Loader2, UploadCloud, BarChart, FileSignature, Milestone, CalendarClock, FilePlus2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { useState } from 'react';
import { assessDisputeMerit, AssessDisputeMeritOutput } from '@/ai/flows/assess-dispute-merit';
import { Progress } from '@/components/ui/progress';
import { Skeleton } from '@/components/ui/skeleton';
import Link from 'next/link';

const formSchema = z.object({
  caseName: z.string().min(2, {
    message: 'Case name must be at least 2 characters.',
  }),
  disputeDetails: z.string().min(50, {
    message: 'Please provide at least 50 characters of detail.',
  }),
  evidence: z.custom<FileList>().optional(),
});

export default function SubmitDisputePage() {
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<AssessDisputeMeritOutput | null>(null);
    const { toast } = useToast();
    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            caseName: '',
            disputeDetails: '',
        },
    });

    // Helper to read file as text
    const readFileAsText = (file: File): Promise<string> => {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result as string);
            reader.onerror = (error) => reject(error);
            reader.readAsText(file);
        });
    }

    async function onSubmit(values: z.infer<typeof formSchema>) {
        setLoading(true);
        setResult(null);

        try {
            let evidenceText: string | undefined = undefined;
            if (values.evidence && values.evidence.length > 0) {
                const file = values.evidence[0];
                // Basic check for text-based files. In a real app, you'd want more robust handling.
                if (file.type.startsWith('text/') || file.name.endsWith('.md')) {
                   evidenceText = await readFileAsText(file);
                } else {
                    toast({
                        title: 'Unsupported File Type',
                        description: 'For this demo, please upload a plain text file (.txt, .md). We will add support for more file types like PDF and DOCX soon.',
                        variant: 'destructive',
                    });
                    setLoading(false);
                    return;
                }
            }

            const output = await assessDisputeMerit({
                caseName: values.caseName,
                disputeDetails: values.disputeDetails,
                evidenceText: evidenceText,
            });

            setResult(output);
            
            // Store result in local storage for other pages to use
            if (typeof window !== 'undefined') {
                localStorage.setItem('caseAssessment', JSON.stringify(output));
            }

            toast({
                title: 'Analysis Complete!',
                description: 'Your case assessment is ready below.',
            });
            form.reset();
        } catch (error) {
            console.error(error);
            toast({
                title: 'Analysis Failed',
                description: 'An error occurred during the analysis. Please try again.',
                variant: 'destructive',
            });
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="space-y-8">
            <div className="flex items-center gap-4">
                <FileText className="h-8 w-8 text-primary" />
                <div>
                    <h1 className="text-3xl font-bold tracking-tight font-headline">Submit a Legal Dispute</h1>
                    <p className="text-muted-foreground">
                        Provide details of your legal dispute and upload relevant evidence for AI-powered analysis.
                    </p>
                </div>
            </div>

            <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
                    <Card>
                        <CardHeader>
                            <CardTitle>Case Details</CardTitle>
                            <CardDescription>
                                Fill out the form below to submit your case for an initial assessment.
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            <FormField
                                control={form.control}
                                name="caseName"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Case Name / Title</FormLabel>
                                        <FormControl>
                                            <Input placeholder="e.g., Smith vs. Landlord Corp" {...field} disabled={loading} />
                                        </FormControl>
                                        <FormDescription>
                                            A short, descriptive name for your case.
                                        </FormDescription>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="disputeDetails"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Dispute Details</FormLabel>
                                        <FormControl>
                                            <Textarea
                                                placeholder="Describe your legal issue in detail. Include key events, dates, and people involved."
                                                className="min-h-[200px]"
                                                {...field}
                                                disabled={loading}
                                            />
                                        </FormControl>
                                        <FormDescription>
                                            The more detail you provide, the better the analysis.
                                        </FormDescription>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="evidence"
                                render={({ field: { onChange, value, ...rest } }) => (
                                    <FormItem>
                                        <FormLabel>Upload Evidence (Optional)</FormLabel>
                                        <FormControl>
                                            <div className="flex items-center justify-center w-full">
                                                <label
                                                    htmlFor="dropzone-file"
                                                    className="flex flex-col items-center justify-center w-full h-64 border-2 border-dashed rounded-lg cursor-pointer bg-card hover:bg-muted"
                                                >
                                                    <div className="flex flex-col items-center justify-center pt-5 pb-6">
                                                        <UploadCloud className="w-10 h-10 mb-3 text-muted-foreground" />
                                                        <p className="mb-2 text-sm text-muted-foreground">
                                                            <span className="font-semibold">Click to upload</span> or drag and drop
                                                        </p>
                                                        <p className="text-xs text-muted-foreground">Plain Text (.txt, .md)</p>
                                                    </div>
                                                    <Input 
                                                        id="dropzone-file" 
                                                        type="file" 
                                                        className="hidden" 
                                                        {...rest}
                                                        onChange={(e) => onChange(e.target.files)}
                                                        disabled={loading}
                                                    />
                                                </label>
                                            </div>
                                        </FormControl>
                                        <FormDescription>
                                            Upload a text file containing evidence like emails or transcripts.
                                        </FormDescription>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </CardContent>
                    </Card>
                    <Button type="submit" disabled={loading}>
                        {loading ? (
                            <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                Submitting for Analysis...
                            </>
                        ) : (
                            'Get AI Assessment'
                        )}
                    </Button>
                </form>
            </Form>
            
            {loading && (
                <Card>
                    <CardHeader>
                        <CardTitle>Generating Assessment...</CardTitle>
                        <CardDescription>The AI is analyzing your case details. This may take a moment.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="space-y-2">
                            <Skeleton className="h-4 w-[150px]" />
                            <Skeleton className="h-8 w-full" />
                        </div>
                        <div className="space-y-2">
                             <Skeleton className="h-4 w-[150px]" />
                            <Skeleton className="h-20 w-full" />
                        </div>
                    </CardContent>
                </Card>
            )}

            {result && (
                 <Card className="border-primary">
                    <CardHeader>
                        <CardTitle className="font-headline text-2xl">Your Case Assessment</CardTitle>
                        <CardDescription>
                            Here is an AI-powered initial assessment of your case. This is not legal advice.
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="grid gap-6 md:grid-cols-2">
                            <Card>
                                <CardHeader className="flex flex-row items-center justify-between pb-2">
                                    <CardTitle className="text-sm font-medium">Merit Score</CardTitle>
                                    <BarChart className="h-4 w-4 text-muted-foreground" />
                                </CardHeader>
                                <CardContent>
                                    <div className="text-2xl font-bold">{result.meritScore}/100</div>
                                    <p className="text-xs text-muted-foreground">
                                        Indicates the potential strength of your case.
                                    </p>
                                    <Progress value={result.meritScore} className="mt-4" />
                                </CardContent>
                            </Card>
                             <Card>
                                <CardHeader className="flex flex-row items-center justify-between pb-2">
                                    <CardTitle className="text-sm font-medium">Case Classification</CardTitle>
                                    <FileSignature className="h-4 w-4 text-muted-foreground" />
                                </CardHeader>
                                <CardContent>
                                    <div className="text-2xl font-bold">{result.caseClassification}</div>
                                     <p className="text-xs text-muted-foreground">
                                        The area of law your case falls under.
                                    </p>
                                </CardContent>
                            </Card>
                        </div>
                        <Card>
                            <CardHeader>
                                <CardTitle className="text-lg font-headline flex items-center gap-2">
                                     <Milestone className="h-5 w-5" />
                                    Suggested Next Steps
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div>
                                    <h4 className="font-semibold">Analysis</h4>
                                    <p className="text-muted-foreground text-sm whitespace-pre-wrap">{result.analysis}</p>
                                </div>
                                 <div>
                                    <h4 className="font-semibold">Recommended Actions</h4>
                                    <p className="text-muted-foreground text-sm whitespace-pre-wrap">{result.suggestedAvenues}</p>
                                </div>
                            </CardContent>
                        </Card>
                    </CardContent>
                    <CardFooter className="flex-wrap gap-2">
                        <Button asChild variant="outline">
                            <Link href="/dashboard/timeline">
                                <CalendarClock className="mr-2 h-4 w-4" />
                                View Your Legal Timeline
                            </Link>
                        </Button>
                        <Button asChild>
                            <Link href="/dashboard/generate-form">
                                <FilePlus2 className="mr-2 h-4 w-4" />
                                Generate Legal Form
                            </Link>
                        </Button>
                    </CardFooter>
                </Card>
            )}
        </div>
    );
}
