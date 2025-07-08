import SiteHeader from '@/components/site-header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertTriangle, CheckCircle } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function TroubleshootingPage() {
  const projectId = 'justicebotai';
  const authSettingsUrl = `https://console.firebase.google.com/project/${projectId}/authentication/settings`;
  const domainToAdd = 'studio--justicebotai.us-central1.hosted.app';

  return (
    <div className="bg-background min-h-screen">
      <SiteHeader />
      <main className="py-24 sm:py-32">
        <div className="mx-auto max-w-4xl px-6 lg:px-8">
          <Card>
            <CardHeader>
              <CardTitle className="font-headline text-4xl">Troubleshooting Guide</CardTitle>
              <p className="text-muted-foreground pt-2">
                Solve common issues to get your app running smoothly.
              </p>
            </CardHeader>
            <CardContent className="space-y-8 text-foreground/80">
              
              <div className="space-y-4 p-6 border-l-4 border-destructive bg-destructive/5 rounded-lg">
                <h2 className="text-2xl font-bold font-headline text-foreground flex items-center gap-2">
                  <AlertTriangle className="h-6 w-6 text-destructive" />
                  Fixing Sign-In: The 'auth/auth-domain-config-required' Error
                </h2>
                <p>
                  This is the most common issue and it's easy to fix! It means your Firebase project doesn't yet trust your app's website address. This is a security feature, and you just need to add the address to an "allow list".
                </p>

                <div className="space-y-3">
                    <h3 className="font-bold text-foreground">Step 1: Go directly to the right page</h3>
                    <p>Click the button below to open the "Authentication Settings" page for your project in the Firebase Console. No more hunting around!</p>
                     <Button asChild>
                        <a href={authSettingsUrl} target="_blank" rel="noopener noreferrer">
                            Open Firebase Auth Settings
                        </a>
                    </Button>
                </div>

                <div className="space-y-3">
                    <h3 className="font-bold text-foreground">Step 2: Find "Authorized domains"</h3>
                    <p>On the settings page, scroll down until you see a section titled <span className="font-mono p-1 bg-muted rounded-md">Authorized domains</span>. It will look something like this:</p>
                    <div className="p-4 border rounded-md bg-background">
                        <p className="font-semibold">Authorized domains</p>
                        <p className="text-sm text-muted-foreground mt-1">Add domains that are allowed to make authentication requests.</p>
                        <div className="mt-4 flex items-center justify-center h-10 w-48 bg-muted/50 rounded-md border border-dashed">
                             <p className="text-sm text-muted-foreground">[List of domains here]</p>
                        </div>
                    </div>
                </div>

                <div className="space-y-3">
                    <h3 className="font-bold text-foreground">Step 3: Add your app's domain</h3>
                    <p>Click the <span className="font-mono p-1 bg-muted rounded-md">Add domain</span> button and enter your app's live URL:</p>
                    <div className="p-3 rounded-md bg-muted text-center font-mono text-sm break-all">
                        {domainToAdd}
                    </div>
                    <p>For testing on your local machine, you should also add <span className="font-mono p-1 bg-muted rounded-md">localhost</span>.</p>
                </div>
                 
                <div className="space-y-3 pt-4 border-t mt-4">
                     <h3 className="font-bold text-foreground flex items-center gap-2">
                        <CheckCircle className="h-5 w-5 text-green-500" />
                        That's it!
                    </h3>
                    <p>
                        After adding the domain(s), refresh your app page. The sign-in process should now work perfectly.
                    </p>
                </div>

              </div>

            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
