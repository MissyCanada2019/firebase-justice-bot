'use client';

imimport Head from 'next/head';import SiteFooter from '@/components/site-footer';port Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowRight, Gavel, Scale, ShieldCheck } from 'lucide-react';
import SiteHeader from '@/components/site-header';
import { useAuth } from '@/hooks/use-auth';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { useToast } from '@/hooks/use-toast';

// Make grecaptcha available on the window object
declare global {
  interface Window {
    grecaptcha: any;
  }
}

export default function Home() {
  const { user, loading, signInWithGoogle } = useAuth();
  const router = useRouter();
  const { toast } = useToast();

  useEffect(() => {
    if (!loading && user) {
      router.push('/dashboard');
    }
  }, [user, loading, router]);

  const handleLoginClick = async () => {
    if (window.grecaptcha && window.grecaptcha.enterprise) {
      try {
        await window.grecaptcha.enterprise.ready();
        const token = await window.grecaptcha.enterprise.execute('6LdDBn4rAAAAADuEa2UqVQRkdrHRD-25aqWhWaYj', {action: 'LOGIN'});

        if (token) {
          await signInWithGoogle(token);
        } else {
           toast({
            title: 'reCAPTCHA Failed',
            description: 'Could not get a security token. Please try again.',
            variant: 'destructive',
          });
        }
      } catch (error) {
         console.error("reCAPTCHA execution error:", error);
         toast({
            title: 'reCAPTCHA Error',
            description: 'There was a problem with the security check. Please try again later.',
            variant: 'destructive',
          });
      }
    } else {
       toast({
        title: 'reCAPTCHA Not Loaded',
        description: 'The security script did not load. Please refresh the page and try again.',
        variant: 'destructive'
       });
    }
  }

  const features = [
    {
      icon: <Gavel className="h-8 w-8 text-primary" />,
      title: 'Charter-Informed Analysis',
      description: 'Analyze legal documents with integrated Canadian Charter of Rights and Freedoms references.',
    },
    {
      icon: <Scale className="h-8 w-8 text-primary" />,
      title: 'Broad Legal Coverage',
      description: 'AI-powered summaries for Family, Criminal, and Landlord Tenant Board (LTB) laws.',
    },
    {
      icon: <ShieldCheck className="h-8 w-8 text-primary" />,
      title: 'Empowering Self-Advocates',
      description: 'Generate arguments and understand your rights and obligations with confidence.',
    },
  ];

  return (
    <div className="relative isolate min-h-screen flex flex-col">
      <SiteHeader />
      <main className="flex-grow">
        <div className="relative px-6 lg:px-8">
          <div className="mx-auto max-w-3xl pt-20 pb-32 sm:pt-48 sm:pb-40">
            <div className="text-center">
              <h1 className="font-headline text-4xl font-bold tracking-tight text-foreground sm:text-6xl">
                JusticeBot.AI
              </h1>
              <p className="mt-6 text-lg leading-8 text-foreground/80">
                Your partner in navigating the complexities of Canadian law. AI-powered insights for everyday people.
              </p>
              <div className="mt-10 flex items-center justify-center gap-x-6">
                <Button onClick={handleLoginClick} size="lg" disabled={loading || user !== null}>
                  Get Started with Google <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
                <Button asChild variant="link" size="lg">
                  <Link href="/about">
                    Our Story <span aria-hidden="true">→</span>
                  </Link>
                </Button>
              </div>
              <p className="mt-6 text-sm text-muted-foreground">
                Psst... the first 1,000 users get free access for life!
              </p>
            </div>
          </div>
        </div>

        <div className="bg-background/80 backdrop-blur-sm py-24 sm:py-32">
          <div className="mx-auto max-w-7xl px-6 lg:px-8">
            <div className="mx-auto max-w-2xl lg:text-center">
              <h2 className="text-base font-semibold leading-7 text-accent font-body">Empower Your Case</h2>
              <p className="mt-2 text-3xl font-bold tracking-tight text-foreground sm:text-4xl font-headline">
                Everything you need to advocate for yourself
              </p>
              <p className="mt-6 text-lg leading-8 text-foreground/80">
                JusticeBot.AI provides powerful, AI-driven tools to demystify legal documents and legislation, helping you build a stronger case.
              </p>
            </div>
            <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
              <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
                {features.map((feature) => (
                  <Card key={feature.title} className="hover:shadow-lg transition-shadow duration-300">
                    <CardHeader>
                      <div className="flex items-center gap-4">
                        {feature.icon}
                        <CardTitle className="font-headline text-xl">{feature.title}</CardTitle>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-foreground/80">{feature.description}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>

      <footer className="bg-background/80 mt-auto py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm text-foreground/60">
           <div className="flex justify-center flex-wrap gap-x-6 gap-y-2 mb-4">
              <Link href="/terms-of-use" className="hover:text-primary transition-colors duration-200">Terms of Use</Link>
              <Link href="/privacy-policy" className="hover:text-primary transition-colors duration-200">Privacy Policy</Link>
              <Link href="/government-inquiries" className="hover:text-primary transition-colors duration-200">Government Inquiries</Link>
              <Link href="/media-inquiries" className="hover:text-primary transition-colors duration-200">Media Inquiries</Link>
              <Link href="/troubleshooting" className="hover:text-primary transition-colors duration-200">Troubleshooting</Link>
            </div>
          <p>&copy; {new Date().getFullYear()} JusticeBot.AI. All Rights Reserved.</p>
          <p className="mt-2">Made with <span className="text-accent">❤</span> in Canada</p>
        </div>
      </footer>
    </div>
  );
}
