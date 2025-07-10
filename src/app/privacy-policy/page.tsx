import SiteHeader from '@/components/site-header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ClientDate } from '@/components/client-date';

export default function PrivacyPolicyPage() {
  return (
    <div className="bg-background min-h-screen">
      <SiteHeader />
      <main className="py-24 sm:py-32">
        <div className="mx-auto max-w-4xl px-6 lg:px-8">
          <Card>
            <CardHeader>
              <CardTitle className="font-headline text-4xl">Privacy Policy</CardTitle>
              <p className="text-muted-foreground pt-2">Last Updated: <ClientDate /></p>
            </CardHeader>
            <CardContent className="space-y-6 text-foreground/80">
              <div className="space-y-2">
                <h2 className="text-xl font-bold font-headline text-foreground">1. Introduction</h2>
                <p>
                  JusticeBot.AI ("we," "our," or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our website and services (the "Service"). Our goal is to comply with Canada's Personal Information Protection and Electronic Documents Act (PIPEDA).
                </p>
              </div>
              <div className="space-y-2">
                <h2 className="text-xl font-bold font-headline text-foreground">2. Information We Collect</h2>
                <p>We may collect the following types of information:</p>
                <ul className="list-disc pl-6 space-y-1">
                    <li>
                        <strong>Personal Information:</strong> Information you provide when you register, such as your name and email address. We do not store your password directly, only a secure, encrypted version of it.
                    </li>
                     <li>
                        <strong>Case Information:</strong> Details and text from documents you provide for analysis. By submitting this information, you consent to it being stored securely in our database and associated with your account to enable core application features like generating timelines, finding precedents, and maintaining a case history for your convenience.
                    </li>
                     <li>
                        <strong>Usage Data:</strong> We may collect information about how you interact with the Service, such as your IP address and browser type, to monitor for security threats and improve the Service. We also use Google reCAPTCHA to protect our login and registration pages from abuse.
                    </li>
                </ul>
              </div>
              <div className="space-y-2">
                <h2 className="text-xl font-bold font-headline text-foreground">3. How We Use Your Information</h2>
                <p>We use the information we collect to:</p>
                 <ul className="list-disc pl-6 space-y-1">
                    <li>Provide, operate, and maintain the Service.</li>
                    <li>Process your payments and manage your account.</li>
                    <li>Analyze your case information to provide AI-powered summaries, scores, and recommendations. Your data is sent to our AI service provider (Google) for this purpose. We do not permit them to use this data to train their models.</li>
                    <li>Improve the Service and develop new features.</li>
                    <li>Communicate with you, including sending you updates and service-related notifications.</li>
                    <li>Comply with legal obligations and enforce our terms.</li>
                </ul>
              </div>
              <div className="space-y-2">
                <h2 className="text-xl font-bold font-headline text-foreground">4. Data Security</h2>
                <p>
                  We implement a variety of security measures to maintain the safety of your personal information. Your account is secured by Firebase Authentication. All data transmitted between your browser, our servers, and our AI service providers is encrypted using Transport Layer Security (TLS). Data is stored securely in Google's Firestore databases. However, no method of transmission over the Internet is 100% secure.
                </p>
              </div>
              <div className="space-y-2">
                <h2 className="text-xl font-bold font-headline text-foreground">5. Data Retention</h2>
                <p>
                  We will retain your account information and your submitted case data as long as your account is active. This allows you to access your case history and use the app's features seamlessly. You can request the deletion of your account and all associated personal and case data at any time by contacting us.
                </p>
              </div>
               <div className="space-y-2">
                <h2 className="text-xl font-bold font-headline text-foreground">6. Third-Party Services</h2>
                <p>
                  We use third-party services like Google (for AI models and authentication) and may use payment processors (e.g., PayPal). These services have their own privacy policies, and we encourage you to review them. We are not responsible for the privacy practices of third parties.
                </p>
              </div>
              <div className="space-y-2">
                <h2 className="text-xl font-bold font-headline text-foreground">7. Your Rights</h2>
                <p>
                  You have the right to access, correct, or delete your personal information. Please contact us to make such a request.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
