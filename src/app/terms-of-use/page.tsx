import SiteHeader from '@/components/site-header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function TermsOfUsePage() {
  return (
    <div className="bg-background min-h-screen">
      <SiteHeader />
      <main className="py-24 sm:py-32">
        <div className="mx-auto max-w-4xl px-6 lg:px-8">
          <Card>
            <CardHeader>
              <CardTitle className="font-headline text-4xl">Terms of Use</CardTitle>
              <p className="text-muted-foreground pt-2">Last Updated: {new Date().toLocaleDateString()}</p>
            </CardHeader>
            <CardContent className="space-y-6 text-foreground/80">
              <div className="space-y-2">
                <h2 className="text-xl font-bold font-headline text-foreground">1. Acceptance of Terms</h2>
                <p>
                  By accessing or using JusticeBot.AI (the "Service"), you agree to be bound by these Terms of Use ("Terms"). If you do not agree to these Terms, you may not use the Service. This is a legally binding agreement.
                </p>
                <p className="font-bold text-destructive">
                  IMPORTANT: The information provided by this Service does not, and is not intended to, constitute legal advice; instead, all information, content, and materials available on this site are for general informational purposes only. Information on this website may not constitute the most up-to-date legal or other information.
                </p>
              </div>
              <div className="space-y-2">
                <h2 className="text-xl font-bold font-headline text-foreground">2. Description of Service</h2>
                <p>
                  JusticeBot.AI is an AI-powered platform designed to assist self-represented litigants in Canada by providing document analysis, legal information summaries, and form generation. The Service is intended to empower users, not to replace a qualified legal professional.
                </p>
              </div>
              <div className="space-y-2">
                <h2 className="text-xl font-bold font-headline text-foreground">3. No Legal Advice or Lawyer-Client Relationship</h2>
                <p>
                  Your use of the Service does not create a lawyer-client relationship between you and JusticeBot.AI or its creators. The Service provides information, not legal advice. You should consult with a qualified lawyer for advice on your specific legal issues. We are not a law firm and are not a substitute for a lawyer's advice.
                </p>
              </div>
              <div className="space-y-2">
                <h2 className="text-xl font-bold font-headline text-foreground">4. User Responsibilities</h2>
                <p>
                  You are responsible for the accuracy of the information you provide to the Service. You agree not to use the Service for any unlawful purpose. You are solely responsible for all decisions and actions taken based on the information provided by the Service.
                </p>
              </div>
              <div className="space-y-2">
                <h2 className="text-xl font-bold font-headline text-foreground">5. Limitation of Liability</h2>
                <p>
                  To the fullest extent permitted by law, JusticeBot.AI, its creators, and its affiliates shall not be liable for any indirect, incidental, special, consequential, or punitive damages, or any loss of profits or revenues, whether incurred directly or indirectly, or any loss of data, use, goodwill, or other intangible losses, resulting from (a) your access to or use of or inability to access or use the Service; (b) any conduct or content of any third party on the Service; or (c) unauthorized access, use, or alteration of your transmissions or content.
                </p>
                 <p className="font-bold">
                  The information is provided "as is"; no representations are made that the content is error-free.
                </p>
              </div>
              <div className="space-y-2">
                <h2 className="text-xl font-bold font-headline text-foreground">6. Changes to Terms</h2>
                <p>
                  We reserve the right to modify these Terms at any time. We will provide notice of any significant changes. Your continued use of the Service after such changes constitutes your acceptance of the new Terms.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
