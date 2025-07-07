import SiteHeader from '@/components/site-header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function PrivacyPolicyPage() {
  return (
    <div className="bg-background min-h-screen">
      <SiteHeader />
      <main className="py-24 sm:py-32">
        <div className="mx-auto max-w-4xl px-6 lg:px-8">
          <Card>
            <CardHeader>
              <CardTitle className="font-headline text-4xl">Privacy Policy</CardTitle>
              <p className="text-muted-foreground pt-2">Last Updated: {new Date().toLocaleDateString()}</p>
            </CardHeader>
            <CardContent className="space-y-6 text-foreground/80">
              <div className="space-y-2">
                <h2 className="text-xl font-bold font-headline text-foreground">1. Introduction</h2>
                <p>
                  JusticeBot.AI ("we," "our," or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our website and services (the "Service").
                </p>
              </div>
              <div className="space-y-2">
                <h2 className="text-xl font-bold font-headline text-foreground">2. Information We Collect</h2>
                <p>We may collect the following types of information:</p>
                <ul className="list-disc pl-6 space-y-1">
                    <li>
                        <strong>Personal Information:</strong> Information you provide when you register, such as your name, email address, and payment information. Your Firebase authentication UID may be stored.
                    </li>
                     <li>
                        <strong>Case Information:</strong> Details and documents you upload related to your legal dispute. This may include sensitive personal information. We treat this with the highest level of confidentiality.
                    </li>
                     <li>
                        <strong>Usage Data:</strong> Information about how you interact with the Service, such as your IP address, browser type, and pages visited. This is collected automatically.
                    </li>
                </ul>
              </div>
              <div className="space-y-2">
                <h2 className="text-xl font-bold font-headline text-foreground">3. How We Use Your Information</h2>
                <p>We use the information we collect to:</p>
                 <ul className="list-disc pl-6 space-y-1">
                    <li>Provide, operate, and maintain the Service.</li>
                    <li>Process your payments and manage your account.</li>
                    <li>Analyze your case information to provide AI-powered summaries, scores, and recommendations.</li>
                    <li>Improve the Service and develop new features.</li>
                    <li>Communicate with you, including sending you updates and service-related notifications.</li>
                    <li>Comply with legal obligations and protect our rights.</li>
                </ul>
              </div>
              <div className="space-y-2">
                <h2 className="text-xl font-bold font-headline text-foreground">4. Data Security</h2>
                <p>
                  We implement a variety of security measures to maintain the safety of your personal information. All communications with our AI models and internal services are encrypted. However, no method of transmission over the Internet or method of electronic storage is 100% secure.
                </p>
              </div>
              <div className="space-y-2">
                <h2 className="text-xl font-bold font-headline text-foreground">5. Data Retention</h2>
                <p>
                  We will retain your personal information and case data only for as long as is necessary for the purposes set out in this Privacy Policy, or as required by law. You can request the deletion of your account and associated data at any time.
                </p>
              </div>
               <div className="space-y-2">
                <h2 className="text-xl font-bold font-headline text-foreground">6. Third-Party Services</h2>
                <p>
                  We use third-party services like Google (for AI models and authentication) and payment processors (e.g., Stripe, PayPal). These services have their own privacy policies, and we encourage you to review them. We are not responsible for the privacy practices of third parties.
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
