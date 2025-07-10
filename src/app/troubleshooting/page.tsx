
'use client';

import SiteHeader from '@/components/site-header';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertTriangle, ExternalLink, CheckCircle, Circle } from 'lucide-react';

export default function TroubleshootingPage() {
  const projectId = 'justicebotai';
  const authSettingsUrl = `https://console.firebase.google.com/u/0/project/${projectId}/authentication/settings`;
  const domainToAdd = 'studio--justicebotai.us-central1.hosted.app';

  return (
    <>
      <SiteHeader />
      <main className="flex items-center justify-center min-h-screen px-4 py-12 bg-background">
        <Card className="w-full max-w-3xl border-destructive border-2">
          <CardHeader className="text-center">
            <AlertTriangle className="w-16 h-16 mx-auto text-destructive" />
            <CardTitle className="mt-4 text-3xl font-bold tracking-tight font-headline text-foreground">
              Final Step: Fix Login
            </CardTitle>
            <p className="text-lg text-muted-foreground">
              Follow this checklist to enable login. This is a one-time security step in Firebase.
            </p>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-4 text-lg">
              <div className="flex items-start gap-4">
                <div className="flex items-center justify-center w-8 h-8 font-bold rounded-full bg-primary text-primary-foreground shrink-0">1</div>
                <div className="flex-1">
                  <p className="font-semibold text-foreground">Open Firebase Settings</p>
                  <p className="text-base text-muted-foreground">Click the button below. It will open a new browser tab with the correct page in your Firebase project.</p>
                  <Button asChild className="w-full mt-2">
                    <a href={authSettingsUrl} target="_blank" rel="noopener noreferrer">
                      Go to Firebase Auth Settings <ExternalLink className="ml-2"/>
                    </a>
                  </Button>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="flex items-center justify-center w-8 h-8 font-bold rounded-full bg-primary text-primary-foreground shrink-0">2</div>
                 <div className="flex-1">
                  <p className="font-semibold text-foreground">Add Domain</p>
                  <p className="text-base text-muted-foreground">On the new page, find the section called <strong className="text-primary">"Authorized domains"</strong> and click the button that says <strong className="text-primary">"Add domain"</strong>.</p>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="flex items-center justify-center w-8 h-8 font-bold rounded-full bg-primary text-primary-foreground shrink-0">3</div>
                 <div className="flex-1">
                  <p className="font-semibold text-foreground">Enter This Exact Text</p>
                  <p className="text-base text-muted-foreground">A box will pop up. Copy the text below and paste it into the box, then click "Add".</p>
                  <div className="p-3 mt-2 font-mono text-sm text-center break-all rounded-md bg-muted text-foreground">
                    {domainToAdd}
                  </div>
                </div>
              </div>
            </div>
            
            <div className="p-4 text-center rounded-lg bg-green-50 border-green-200 border">
                <CheckCircle className="w-8 h-8 mx-auto text-green-600"/>
                <p className="mt-2 font-semibold text-green-800">That's it! Once you've done this, come back to this page and log in. The error will be gone.</p>
            </div>
          </CardContent>
        </Card>
      </main>
    </>
  );
}
