
'use client';

import { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  CardFooter,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Check, CreditCard } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';
import { useAuth } from '@/hooks/use-auth';
import { Badge } from '@/components/ui/badge';
import Link from 'next/link';

const pricingTiers = [
  {
    name: 'Single Document',
    price: '$5.99',
    duration: 'one-time',
    description: 'One legal form download (e.g., T2, HRTO-1).',
    features: ['One-time purchase', 'Form remains unlocked permanently', 'Ideal for single-use needs'],
    planId: 'single',
  },
  {
    name: 'Monthly Plan',
    price: '$59.99',
    duration: '/ 49 days',
    description: 'Unlimited access to all tools & downloads.',
    features: ['Unlimited form generation', 'Unlimited PDF downloads', 'Access all legal summary tools', 'Priority AI access'],
    isPopular: true,
    planId: 'monthly',
  },
  {
    name: 'Annual Plan',
    price: '$499.99',
    duration: '/ year',
    description: 'The best value for long-term needs.',
    features: ['All features from Monthly', '365 days of access', 'Significant savings over monthly'],
    planId: 'annual',
  },
   {
    name: 'Low-Income Verified',
    price: '$25.99',
    duration: '/ year',
    description: 'Full access for verified users.',
    features: ['All features from Annual', 'Requires verification (coming soon)', 'Our commitment to access to justice'],
    planId: 'low_income',
  },
];

export default function PricingPage() {
  const [activeSubscription, setActiveSubscription] = useState<string | null>(null);
  const { toast } = useToast();
  const router = useRouter();
  const { isFreeTier } = useAuth();

  useEffect(() => {
    const subscription = localStorage.getItem('justiceBotSubscription');
    setActiveSubscription(subscription);
  }, []);

  const handleChoosePlan = (planId: string) => {
    // In a real app, this would redirect to a payment provider.
    // Here, we simulate a successful payment and subscription update.
    localStorage.setItem('justiceBotSubscription', planId);
    setActiveSubscription(planId);
    toast({
      title: 'Plan Activated!',
      description: `You have successfully subscribed. All features are now unlocked.`,
    });
    router.push('/dashboard/generate-form');
  };

  if (isFreeTier) {
      return (
         <div className="flex items-center justify-center min-h-[calc(100vh-10rem)]">
            <Card className="w-full max-w-lg text-center border-primary">
                <CardHeader>
                    <div className="mx-auto bg-green-100 p-4 rounded-full w-fit mb-4">
                       <Check className="h-12 w-12 text-green-600" />
                    </div>
                    <CardTitle className="font-headline text-3xl">You Have Free Lifetime Access!</CardTitle>
                    <CardDescription>
                       As one of our first 1,000 users, you have full access to all JusticeBot.AI features, including unlimited PDF downloads, forever. Thank you for being an early supporter!
                    </CardDescription>
                </CardHeader>
                <CardFooter className="flex justify-center">
                    <Button asChild size="lg">
                        <Link href="/dashboard">Return to Dashboard</Link>
                    </Button>
                </CardFooter>
            </Card>
        </div>
      )
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-4">
        <CreditCard className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-3xl font-bold tracking-tight font-headline">Pricing & Plans</h1>
          <p className="text-muted-foreground">
            Choose a plan that fits your needs. Unlock premium features like PDF downloads.
          </p>
        </div>
      </div>

      <div className="grid gap-8 md:grid-cols-1 lg:grid-cols-2 xl:grid-cols-4">
        {pricingTiers.map((tier) => (
          <Card key={tier.name} className={cn("flex flex-col", tier.isPopular && "border-primary border-2 shadow-lg")}>
            <CardHeader className="relative">
                {tier.isPopular && (
                    <Badge className="absolute top-0 right-0 -mr-2 -mt-2 bg-accent text-accent-foreground">Most Popular</Badge>
                )}
              <CardTitle className="font-headline text-2xl">{tier.name}</CardTitle>
              <div className="flex items-baseline gap-2">
                <span className="text-4xl font-bold">{tier.price}</span>
                {tier.duration && <span className="text-muted-foreground">{tier.duration}</span>}
              </div>
              <CardDescription>{tier.description}</CardDescription>
            </CardHeader>
            <CardContent className="flex-grow space-y-4">
              <ul className="space-y-2">
                {tier.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-2">
                    <Check className="h-5 w-5 text-green-500 mt-1 shrink-0" />
                    <span className="text-muted-foreground">{feature}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
            <CardFooter>
              <Button 
                className="w-full" 
                onClick={() => handleChoosePlan(tier.planId)}
                disabled={activeSubscription === tier.planId || tier.planId === 'low_income'}
                variant={tier.isPopular ? 'default' : 'outline'}
              >
                {activeSubscription === tier.planId ? 'Current Plan' : 'Choose Plan'}
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  );
}
