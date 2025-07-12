
'use server';

import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2024-06-20',
  typescript: true,
});

export async function createCheckoutSession(
  priceId: string,
  userId: string,
  planId: string
) {
  try {
    const appUrl = process.env.NEXT_PUBLIC_APP_URL;

    // A one-time purchase is a different mode than a subscription
    const mode = planId === 'single' ? 'payment' : 'subscription';

    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      mode: mode,
      line_items: [
        {
          price: priceId,
          quantity: 1,
        },
      ],
      // Pass the user ID to the session so we can identify the user
      // when we receive the webhook event from Stripe.
      client_reference_id: userId,
      // Add the planId to metadata so we can identify the plan in webhooks
      metadata: {
        planId,
      },
      success_url: `${appUrl}/dashboard/billing?success=true&session_id={CHECKOUT_SESSION_ID}&plan_id=${planId}`,
      cancel_url: `${appUrl}/dashboard/billing?canceled=true`,
    });

    return { sessionId: session.id };
  } catch (error: any) {
    console.error('Stripe Error:', error.message);
    return { error: 'Failed to create Stripe checkout session.' };
  }
}
