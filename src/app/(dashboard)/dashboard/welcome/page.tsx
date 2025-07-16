import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { CheckCircle, ArrowRight } from 'lucide-react';
import Link from 'next/link';
import { Icons } from '@/components/icons';

export default function WelcomePage() {
    return (
        <div className="flex items-center justify-center min-h-[calc(100vh-10rem)]">
            <Card className="w-full max-w-2xl text-center">
                <CardHeader>
                    <div className="mx-auto bg-primary/10 p-4 rounded-full w-fit mb-4">
                        <Icons.mapleLeaf className="h-12 w-12 text-primary" />
                    </div>
                    <CardTitle className="font-headline text-3xl">Welcome to JusticeBot.AI!</CardTitle>
                    <CardDescription>
                        You're all set up. We're thrilled to have you on board.
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 text-left px-8">
                    <p className="text-muted-foreground">
                        You now have access to a suite of AI-powered tools designed to help you navigate the Canadian legal system. Here's what you can do next:
                    </p>
                    <ul className="space-y-2">
                        <li className="flex items-start gap-3">
                            <CheckCircle className="h-5 w-5 text-green-500 mt-1 shrink-0" />
                            <div>
                                <span className="font-semibold">Submit a Dispute:</span> Get an instant AI assessment of your case, including a merit score and suggested next steps.
                            </div>
                        </li>
                        <li className="flex items-start gap-3">
                            <CheckCircle className="h-5 w-5 text-green-500 mt-1 shrink-0" />
                            <div>
                                <span className="font-semibold">Generate a Legal Timeline:</span> See a step-by-step roadmap for your legal journey based on your case type.
                            </div>
                        </li>
                        <li className="flex items-start gap-3">
                            <CheckCircle className="h-5 w-5 text-green-500 mt-1 shrink-0" />
                            <div>
                                <span className="font-semibold">Explore Legal Summaries:</span> Understand complex laws for Family, Criminal, or LTB matters in plain language.
                            </div>
                        </li>
                    </ul>
                </CardContent>
                <CardFooter className="flex justify-center">
                    <Button asChild size="lg">
                        <Link href="/dashboard">
                            Go to my Dashboard <ArrowRight className="ml-2 h-5 w-5" />
                        </Link>
                    </Button>
                </CardFooter>
            </Card>
        </div>
    );
}
