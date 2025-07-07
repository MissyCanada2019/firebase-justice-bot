'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
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
import { FileText, Loader2, UploadCloud } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { useState } from 'react';

const formSchema = z.object({
  caseName: z.string().min(2, {
    message: 'Case name must be at least 2 characters.',
  }),
  disputeDetails: z.string().min(50, {
    message: 'Please provide at least 50 characters of detail.',
  }),
  evidence: z.any().optional(),
});

export default function SubmitDisputePage() {
    const [loading, setLoading] = useState(false);
  const { toast } = useToast();
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      caseName: '',
      disputeDetails: '',
    },
  });

  function onSubmit(values: z.infer<typeof formSchema>) {
    setLoading(true);
    console.log(values);
    // Simulate API call
    setTimeout(() => {
        toast({
            title: "Dispute Submitted!",
            description: "Your case has been received for analysis.",
        });
        form.reset();
        setLoading(false);
    }, 2000);
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-4">
        <FileText className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-3xl font-bold tracking-tight font-headline">Submit a Legal Dispute</h1>
          <p className="text-muted-foreground">
            Provide details of your legal dispute and upload any relevant evidence for AI-powered analysis.
          </p>
        </div>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
          <Card>
            <CardHeader>
              <CardTitle>Case Details</CardTitle>
              <CardDescription>
                Fill out the form below to submit your case.
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
                      <Input placeholder="e.g., Smith vs. Landlord Corp" {...field} />
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
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Upload Evidence</FormLabel>
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
                            <p className="text-xs text-muted-foreground">PDF, DOCX, JPG, PNG (MAX. 10MB)</p>
                          </div>
                          <Input id="dropzone-file" type="file" className="hidden" {...field} />
                        </label>
                      </div>
                    </FormControl>
                    <FormDescription>
                      Upload any documents, images, or other evidence. (This is a demo and does not actually upload files).
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
                    Submitting...
                </>
            ) : (
                'Submit for Analysis'
            )}
          </Button>
        </form>
      </Form>
    </div>
  );
}
