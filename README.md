# JusticeBot.AI on Firebase Studio

This is your project for JusticeBot.AI, built with Next.js and ready for deployment on Firebase.

## Getting Started

To get familiar with the code, take a look at `src/app/page.tsx`.

## Before You Deploy

Make sure you have populated the `.env` file with your Firebase project credentials. You can find these in your Firebase project settings. The file should look like this:

```
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_auth_domain
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_storage_bucket
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_messaging_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
```

## Publishing Your App

1.  **Deploy to Firebase:** Use the "Deploy" button in Firebase Studio. This will build and deploy your application to Firebase App Hosting.
2.  **Connect Your Domain:**
    *   After deploying, go to the **App Hosting** section of your Firebase Console.
    *   Find your newly deployed app and click "Add custom domain".
    *   Follow the on-screen instructions to add `justice-bot.com`.
    *   Firebase will give you DNS records (like an `A` record) to add to your domain registrar (where you bought the domain).
    *   Once you've added the records, Firebase will verify your domain and automatically set up a free SSL certificate.

And that's it! Your app will be live at `https://justice-bot.com`.
