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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { summarizeLitigationLaw, SummarizeLitigationLawOutput } from '@/ai/flows/summarize-litigation-law';
import { BookOpen, Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { CANADIAN_PROVINCES_TERRITORIES } from '@/lib/constants';
import { Skeleton } from '@/components/ui/skeleton';

export default function LitigationLawPage() {
  const [province, setProvince] = useState('');
  const [result, setResult] = useState<SummarizeLitigationLawOutput | null>(null);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async () => {
    if (!province) {
      toast({
        title: 'Province/Territory Required',
        description: 'Please select a province or territory.',
        variant: 'destructive',
      });
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const output = await summarizeLitigationLaw({ provinceOrTerritory: province });
      setResult(output);
    } catch (error) {
      console.error(error);
      toast({
        title: 'Summary Failed',
        description: 'An error occurred while generating the summary. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-4">
        <BookOpen className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-3xl font-bold tracking-tight font-headline">Litigation Law</h1>
          <p className="text-muted-foreground">
            Get AI-powered summaries of litigation laws and civil procedures across Canada.
          </p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Select Location</CardTitle>
          <CardDescription>
            Choose a province or territory to get a summary of its litigation laws.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Select onValueChange={setProvince} value={province} disabled={loading}>
            <SelectTrigger className="w-full md:w-1/2">
              <SelectValue placeholder="Select a province or territory" />
            </SelectTrigger>
            <SelectContent>
              {CANADIAN_PROVINCES_TERRITORIES.map((name) => (
                <SelectItem key={name} value={name}>
                  {name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardContent>
        <CardFooter>
          <Button onClick={handleSubmit} disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating...
              </>
            ) : (
              'Generate Summary'
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
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-4/5" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/5" />
            </CardContent>
        </Card>
      )}

      {result && (
        <Card>
          <CardHeader>
            <CardTitle>Summary for {province}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="whitespace-pre-wrap text-foreground/90">{result.summary}</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
