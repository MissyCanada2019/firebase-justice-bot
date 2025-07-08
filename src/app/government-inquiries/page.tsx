import SiteHeader from '@/components/site-header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ClientDate } from '@/components/client-date';

export default function GovernmentInquiriesPage() {
  return (
    <div className="bg-background min-h-screen">
      <SiteHeader />
      <main className="py-24 sm:py-32">
        <div className="mx-auto max-w-4xl px-6 lg:px-8">
          <Card>
            <CardHeader>
              <CardTitle className="font-headline text-4xl">Government and Law Enforcement Inquiries</CardTitle>
               <p className="text-muted-foreground pt-2">Last Updated: <ClientDate /></p>
            </CardHeader>
            <CardContent className="space-y-6 text-foreground/80">
              <div className="space-y-2">
                <h2 className="text-xl font-bold font-headline text-foreground">1. Our Commitment</h2>
                <p>
                    JusticeBot.AI is committed to user privacy and protecting the sensitive data entrusted to us. At the same time, we are required to comply with Canadian law. This policy outlines our principles and process for responding to government and law enforcement requests for user data.
                </p>
              </div>
               <div className="space-y-2">
                <h2 className="text-xl font-bold font-headline text-foreground">2. Principles</h2>
                <ul className="list-disc pl-6 space-y-1">
                    <li><strong>Legality:</strong> We will only disclose user data when required by a legally valid and binding order, such as a subpoena, court order, or search warrant, issued by a Canadian court or government body with proper jurisdiction.</li>
                    <li><strong>Specificity:</strong> We will interpret all requests as narrowly as possible and will push back against overly broad requests for information. We will not provide "bulk" data or direct access to our systems.</li>
                    <li><strong>Transparency:</strong> Whenever legally permitted, we will notify users of a request for their data before disclosure, providing them with an opportunity to challenge the request. We may delay notification if prohibited by law or if we believe notification could create a risk of injury or death.</li>
                </ul>
              </div>
              <div className="space-y-2">
                <h2 className="text-xl font-bold font-headline text-foreground">3. Process for Handling Requests</h2>
                <p>
                    All government and law enforcement requests must be sent to our designated legal contact address. Upon receipt, our team will:
                </p>
                 <ul className="list-decimal pl-6 space-y-1">
                    <li>Verify the legal validity of the request.</li>
                    <li>Assess whether the request is overly broad or otherwise inappropriate.</li>
                    <li>If the request is valid, we will search for and retrieve only the specific information required.</li>
                    <li>Unless prohibited by law, we will attempt to notify the affected user.</li>
                    <li>We will maintain a record of all requests received and the data disclosed.</li>
                </ul>
              </div>
               <div className="space-y-2">
                <h2 className="text-xl font-bold font-headline text-foreground">4. International Requests</h2>
                <p>
                  Requests from foreign governments must be processed through a Canadian court via a mutual legal assistance treaty (MLAT) or similar diplomatic procedure. We will not respond directly to requests from non-Canadian law enforcement agencies.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
