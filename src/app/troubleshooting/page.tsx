
'use client';

import SiteHeader from '@/components/site-header';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertTriangle, ExternalLink, CheckCircle, Mail } from 'lucide-react';

export default function TroubleshootingPage() {
  const projectId = 'justicebotai';
  const authSettingsUrl = `https://console.firebase.google.com/u/0/project/${projectId}/authentication/settings`;
  const signInMethodUrl = `https://console.firebase.google.com/u/0/project/${projectId}/authentication/sign-in-method`;
  const domainToAdd = 'studio--justicebotai.us-central1.hosted.app';

  return (
    <>
      <SiteHeader />
      <main className="min-h-screen px-4 py-12 bg-background">
        <div className="mx-auto w-full max-w-3xl space-y-8">
            <div className="text-center">
                <AlertTriangle className="w-16 h-16 mx-auto text-destructive" />
                <h1 className="mt-4 text-3xl font-bold tracking-tight font-headline text-foreground">
                    Authentication Setup
                </h1>
                <p className="text-lg text-muted-foreground">
                    Follow these one-time steps in Firebase to enable sign-in.
                </p>
            </div>

            <Card className="border-destructive border-2">
            <CardHeader>
                <CardTitle className="flex items-center gap-2 font-headline text-2xl">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-google"><path d="M12 12v1h.5a2.5 2.5 0 1 0 0-5H12v1z"/><path d="M11.38 12.5A2.5 2.5 0 1 0 7.5 7.77"/><path d="M12.5 11.38A2.5 2.5 0 1 0 16.23 15"/></svg>
                    Fix Google Sign-In
                </CardTitle>
                <p className="text-muted-foreground">
                    This fixes errors like `auth/unauthorized-domain`.
                </p>
            </CardHeader>
            <CardContent className="space-y-6">
                <div className="space-y-4 text-lg">
                <div className="flex items-start gap-4">
                    <div className="flex items-center justify-center w-8 h-8 font-bold rounded-full bg-primary text-primary-foreground shrink-0">1</div>
                    <div className="flex-1">
                    <p className="font-semibold text-foreground">Open Authentication Settings</p>
                    <p className="text-base text-muted-foreground">Click the button below to go to the "Settings" tab in Firebase Authentication.</p>
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
            </CardContent>
            </Card>

            <Card className="border-primary border-2">
            <CardHeader>
                <CardTitle className="flex items-center gap-2 font-headline text-2xl">
                    <Mail />
                    Fix Email & Password Sign-Up
                </CardTitle>
                <p className="text-muted-foreground">
                    This fixes errors like `auth/requests-to-this-api...are-blocked`.
                </p>
            </CardHeader>
            <CardContent className="space-y-6">
                <div className="space-y-4 text-lg">
                <div className="flex items-start gap-4">
                    <div className="flex items-center justify-center w-8 h-8 font-bold rounded-full bg-primary text-primary-foreground shrink-0">1</div>
                    <div className="flex-1">
                    <p className="font-semibold text-foreground">Open Sign-in Methods</p>
                    <p className="text-base text-muted-foreground">Click the button below. It will open the "Sign-in method" tab in your Firebase project.</p>
                    <Button asChild className="w-full mt-2">
                        <a href={signInMethodUrl} target="_blank" rel="noopener noreferrer">
                        Go to Firebase Sign-in Methods <ExternalLink className="ml-2"/>
                        </a>
                    </Button>
                    </div>
                </div>

                <div className="flex items-start gap-4">
                    <div className="flex items-center justify-center w-8 h-8 font-bold rounded-full bg-primary text-primary-foreground shrink-0">2</div>
                    <div className="flex-1">
                    <p className="font-semibold text-foreground">Enable Email/Password</p>
                    <p className="text-base text-muted-foreground">From the list of providers, click on <strong className="text-primary">"Email/Password"</strong>. A panel will open on the right.</p>
                    </div>
                </div>

                <div className="flex items-start gap-4">
                    <div className="flex items-center justify-center w-8 h-8 font-bold rounded-full bg-primary text-primary-foreground shrink-0">3</div>
                    <div className="flex-1">
                    <p className="font-semibold text-foreground">Flick the Switch</p>
                    <p className="text-base text-muted-foreground">Click the toggle switch to enable the provider, and then click "Save".</p>
                    </div>
                </div>
                </div>
            </CardContent>
            </Card>
            
            <div className="p-4 text-center rounded-lg bg-green-50 border-green-200 border">
                <CheckCircle className="w-8 h-8 mx-auto text-green-600"/>
                <p className="mt-2 font-semibold text-green-800">That's it! Once you've completed these steps, your sign-in and sign-up pages will work correctly.</p>
            </div>
        </div>
      </main>
    </>
  );
}
