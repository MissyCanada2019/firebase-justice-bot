
'use client';

import { useState, useEffect } from 'react';
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
import { Input } from '@/components/ui/input';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { findCourtAndAid, FindCourtAndAidOutput } from '@/ai/flows/find-court-flow';
import { AssessDisputeMeritOutput } from '@/ai/flows/assess-dispute-merit';
import { MapPin, Loader2, AlertCircle, Building, LifeBuoy } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import Link from 'next/link';
import { Skeleton } from '@/components/ui/skeleton';
import { useAuth } from '@/hooks/use-auth';
import { getLatestCaseAssessment } from '@/lib/firestoreService';

const formSchema = z.object({
  postalCode: z.string().regex(/^[A-Za-z]\d[A-Za-z][ -]?\d[A-Za-z]\d$/, {
    message: 'Please enter a valid Canadian postal code.',
  }),
});

export default function CourtLocatorPage() {
  const [assessment, setAssessment] = useState<AssessDisputeMeritOutput | null>(null);
  const [result, setResult] = useState<FindCourtAndAidOutput | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingInitialData, setLoadingInitialData] = useState(true);
  const { toast } = useToast();
  const { user } = useAuth();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: { postalCode: '' },
  });

  useEffect(() => {
    if (user) {
      getLatestCaseAssessment(user.uid)
        .then(data => {
          if (data) {
            setAssessment(data);
          }
        })
        .catch(e => {
          console.error('Error reading from Firestore', e);
          toast({
            title: 'Could not load case data',
            description: 'Please submit a dispute again to use this tool.',
            variant: 'destructive',
          });
        })
        .finally(() => {
          setLoadingInitialData(false);
        });
    } else {
        setLoadingInitialData(false);
    }
  }, [user, toast]);

  async function onSubmit(values: z.infer<typeof formSchema>) {
    if (!assessment) {
      toast({
        title: 'No Case Data',
        description: 'Please submit a dispute before finding a court.',
        variant: 'destructive',
      });
      return;
    }
    setLoading(true);
    setResult(null);
    try {
      const output = await findCourtAndAid({
        postalCode: values.postalCode,
        caseClassification: assessment.caseClassification,
      });
      setResult(output);
    } catch (error) {
      console.error(error);
      toast({
        title: 'Search Failed',
        description: 'An error occurred while finding the court. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  }

  if (loadingInitialData) {
    return (
        <Card>
            <CardHeader>
                <Skeleton className="h-6 w-1/4" />
                <Skeleton className="h-4 w-1/2" />
            </CardHeader>
             <CardContent>
                <Loader2 className="mx-auto h-12 w-12 animate-spin text-primary"/>
                <p className="text-center text-muted-foreground">Loading your case data...</p>
            </CardContent>
        </Card>
    )
  }

  if (!assessment) {
    return (
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>No Case Data Found</AlertTitle>
        <AlertDescription>
          You need to submit a dispute for analysis before we can find the right court for you.
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
        <MapPin className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-3xl font-bold tracking-tight font-headline">Court & Aid Locator</h1>
          <p className="text-muted-foreground">
            Find the right courthouse and nearby legal aid clinics for your case.
          </p>
        </div>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
          <Card>
            <CardHeader>
              <CardTitle>Enter Your Postal Code</CardTitle>
              <CardDescription>
                We'll use your postal code to find the nearest court for your '{assessment.caseClassification}' case.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <FormField
                control={form.control}
                name="postalCode"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Postal Code</FormLabel>
                    <FormControl>
                      <Input placeholder="e.g., A1A 1A1" {...field} disabled={loading} className="max-w-xs" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </CardContent>
            <CardFooter>
              <Button type="submit" disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Searching...
                  </>
                ) : 'Find Court'}
              </Button>
            </CardFooter>
          </Card>
        </form>
      </Form>

      {loading && (
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-1/3" />
          </CardHeader>
          <CardContent className="space-y-4">
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-20 w-full" />
          </CardContent>
        </Card>
      )}

      {result && (
        <div className="space-y-8">
            <Card className="border-primary">
                <CardHeader>
                    <CardTitle className="font-headline text-2xl flex items-center gap-2">
                        <Building className="h-6 w-6"/>
                        Your Courthouse/Tribunal
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <h3 className="text-xl font-bold">{result.courthouse.name}</h3>
                    <p className="text-muted-foreground">{result.courthouse.address}</p>
                    <div>
                        <h4 className="font-semibold">Filing Methods</h4>
                        <p className="text-muted-foreground">{result.courthouse.filingMethods}</p>
                    </div>
                     {result.courthouse.rulesLink && (
                        <Button asChild variant="link" className="p-0">
                            <a href={result.courthouse.rulesLink} target="_blank" rel="noopener noreferrer">View Official Rules</a>
                        </Button>
                    )}
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle className="font-headline text-2xl flex items-center gap-2">
                         <LifeBuoy className="h-6 w-6" />
                        Nearby Legal Aid Clinics
                    </CardTitle>
                </CardHeader>
                 <CardContent className="space-y-6">
                    {result.legalAidClinics.length > 0 ? (
                        result.legalAidClinics.map((clinic, index) => (
                             <div key={index} className="p-4 border rounded-lg">
                                <h3 className="font-bold">{clinic.name}</h3>
                                <p className="text-sm text-muted-foreground">{clinic.address}</p>
                                {clinic.notes && <p className="text-sm text-muted-foreground mt-1 italic">"{clinic.notes}"</p>}
                            </div>
                        ))
                    ) : (
                        <p className="text-muted-foreground">No specific legal aid clinics were found for this area.</p>
                    )}
                 </CardContent>
            </Card>
        </div>
      )}
    </div>
  );
}
