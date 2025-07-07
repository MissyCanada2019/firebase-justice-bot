import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BookOpen, Construction } from 'lucide-react';

export default function LitigationLawPage() {
  return (
    <div className="space-y-8">
      <div className="flex items-center gap-4">
        <BookOpen className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-3xl font-bold tracking-tight font-headline">Litigation Law</h1>
          <p className="text-muted-foreground">
            AI-powered access to litigation laws across all Canadian provinces and territories.
          </p>
        </div>
      </div>

      <Card className="text-center">
        <CardHeader>
          <div className="mx-auto bg-primary/10 p-4 rounded-full w-fit">
            <Construction className="h-12 w-12 text-primary" />
          </div>
        </CardHeader>
        <CardContent className="mt-4">
          <CardTitle className="font-headline text-2xl">Feature Coming Soon</CardTitle>
          <p className="mt-2 text-muted-foreground">
            We are working hard to bring you AI-powered summaries and argument generation for litigation law.
            <br />
            Please check back later!
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
