import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CreditCard, Mail } from 'lucide-react';

export default function BillingPage() {
  return (
    <div className="space-y-8">
      <div className="flex items-center gap-4">
        <CreditCard className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-3xl font-bold tracking-tight font-headline">Billing & Payments</h1>
          <p className="text-muted-foreground">
            Securely process payments for your case analysis and services.
          </p>
        </div>
      </div>

      <div className="grid gap-8 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 font-headline">
              <svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 fill-current text-blue-600"><title>PayPal</title><path d="M7.744 24c-3.153 0-4.943-.91-5.087-1.02-.38-.285-.568-.78-.49-1.287l1.32-9.332c.114-.77.87-1.334 1.648-1.334h3.69c3.198 0 4.88-1.55 5.373-3.697l.886-3.882c.152-.664.78-1.144 1.45-1.144h2.99c.56 0 .99.37 1.133.914L24 15.39c-.19.95-.95 1.647-1.92 1.647h-4.48c-.9 0-1.68-.618-1.85-1.49-.6-3.18-3.1-4.92-6.1-4.92H6.18l-1.01 7.123c-.15.8.46 1.55 1.28 1.55h2.12c.9 0 1.68.617 1.85 1.49l.77 4.045c.49 2.58 2.5 4.18 5.17 4.18h.3c3.152 0 4.942-.91 5.086-1.02.38-.284.568-.78.49-1.286l-1.32-9.33c-.113-.77-.87-1.335-1.647-1.335h-2.18c-1.26 0-2.22.99-2.07 2.24.6 5.13-3.6 6.36-7.38 6.36Z"/></svg>
              PayPal
            </CardTitle>
            <CardDescription>
              Pay securely using your PayPal account or a credit/debit card.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Click the button below to be redirected to PayPal's secure payment page. You will be able to enter the payment amount there.
            </p>
            <Button className="w-full">Pay with PayPal</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 font-headline">
              <Mail className="h-6 w-6 text-primary" />
              Interac e-Transfer
            </CardTitle>
            <CardDescription>
              Send payments directly from your Canadian bank account.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-2">
              Please send e-Transfers to the following email address:
            </p>
            <div className="p-3 rounded-md bg-muted text-center font-mono text-sm">
              teresa@justice-bot.com
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Please include your case name or user ID in the e-Transfer message for reference.
            </p>
          </CardContent>
        </Card>
      </div>

       <Card className="border-accent">
          <CardHeader>
            <CardTitle className="font-headline">Important Information</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              After making a payment, please allow up to 24 hours for it to be reflected in your account. You will receive an email confirmation once your payment has been processed. If you have any questions or issues with billing, please contact support.
            </p>
          </CardContent>
        </Card>
    </div>
  );
}
