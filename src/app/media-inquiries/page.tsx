
import SiteHeader from '@/components/site-header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Mail } from 'lucide-react';
import Link from 'next/link';

export default function MediaInquiriesPage() {
  return (
    <div className="bg-background min-h-screen">
      <SiteHeader />
      <main className="py-24 sm:py-32">
        <div className="mx-auto max-w-4xl px-6 lg:px-8">
          <Card>
            <CardHeader>
              <CardTitle className="font-headline text-4xl">Media Inquiries</CardTitle>
              <p className="text-muted-foreground pt-2">
                For journalists, bloggers, and media professionals.
              </p>
            </CardHeader>
            <CardContent className="space-y-6 text-foreground/80">
              <div className="space-y-2">
                <h2 className="text-xl font-bold font-headline text-foreground">Get in Touch</h2>
                <p>
                  We are happy to connect with members of the media to discuss the mission behind JusticeBot.AI, the challenges of navigating the Canadian legal system, and the role of technology in access to justice.
                </p>
                <p>
                  For all media-related inquiries, including requests for interviews with our founder, Teresa, please contact us directly.
                </p>
              </div>
              <div className="space-y-4">
                 <div className="flex items-center gap-4">
                    <Mail className="h-6 w-6 text-primary"/>
                    <div>
                        <h3 className="font-semibold text-foreground">Email</h3>
                        <a href="mailto:teresa@justice-bot.com" className="text-primary hover:underline">
                            teresa@justice-bot.com
                        </a>
                    </div>
                 </div>
              </div>
               <div className="space-y-2">
                <h2 className="text-xl font-bold font-headline text-foreground">About JusticeBot.AI</h2>
                <p>
                  JusticeBot.AI was founded out of a personal struggle with the legal system. Our mission is to empower self-represented litigants across Canada with AI-powered tools to demystify legal documents, understand their rights, and navigate their legal journey with more confidence.
                </p>
                 <p>
                  Learn more about <Link href="/about" className="text-primary hover:underline">Our Story</Link>.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
