'use client';

import SiteHeader from '@/components/site-header';
import { Button } from '@/components/ui/button';
import { AlertTriangle, ExternalLink } from 'lucide-react';

export default function TroubleshootingPage() {
  const projectId = 'justicebotai';
  const authSettingsUrl = `https://console.firebase.google.com/u/0/project/${projectId}/authentication/settings`;
  const domainToAdd = 'studio--justicebotai.us-central1.hosted.app';

  return (
    <>
      <SiteHeader />
      <main className="flex items-center justify-center min-h-screen px-4 py-12">
        <div className="w-full max-w-3xl p-8 space-y-8 text-center border-4 border-dashed rounded-lg border-destructive bg-destructive/5">
          <AlertTriangle className="w-16 h-16 mx-auto text-destructive" />
          <h1 className="text-4xl font-bold tracking-tight font-headline text-foreground">
            Let's Fix Sign-In
          </h1>
          <p className="text-lg text-muted-foreground">
            This is the final step. For security, your Firebase project needs you to approve your app's website address.
          </p>
          
          <div className="p-6 text-left border rounded-lg bg-background">
            <h2 className="text-2xl font-bold text-left font-headline">The 3-Step Fix</h2>
            <ol className="mt-4 space-y-6 text-base list-decimal list-inside text-foreground/80">
              <li>
                Click the button below to go to your Firebase project's "Authentication Settings" page.
                <Button asChild className="w-full mt-2">
                  <a href={authSettingsUrl} target="_blank" rel="noopener noreferrer">
                    Open Firebase Auth Settings <ExternalLink className="ml-2"/>
                  </a>
                </Button>
              </li>
              <li>
                On that page, find the section called <strong className="text-foreground">"Authorized domains"</strong> and click the <strong className="text-foreground">"Add domain"</strong> button.
              </li>
              <li>
                Enter the following domain and click "Add":
                <div className="p-3 mt-2 rounded-md bg-muted text-center font-mono text-sm break-all text-foreground">
                  {domainToAdd}
                </div>
                 <p className="mt-1 text-xs text-muted-foreground">
                  (You should also add <code className="font-mono p-1 text-xs rounded-md bg-muted">localhost</code> if you want to test on your local machine.)
                </p>
              </li>
            </ol>
          </div>

          <p className="text-muted-foreground">
            Once you've added the domain, come back here and try signing in again. It will work.
          </p>

        </div>
      </main>
    </>
  );
}
