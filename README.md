# JusticeBot.AI on Firebase Studio

This is your project for JusticeBot.AI, built with Next.js and ready for deployment on Firebase.

## Local Development Setup

To run this project on your local machine, follow these steps.

### Prerequisites

*   [Node.js](https://nodejs.org/) (version 20 or later recommended)
*   [Firebase CLI](https://firebase.google.com/docs/cli#install-cli-npm)

### 1. Install Dependencies

Once you have the project files on your local machine, navigate to the project directory in your terminal and install the necessary dependencies.

```bash
npm install
```

### 2. Set Up Environment Variables

Your project requires Firebase configuration to run. Create a new file named `.env.local` in the root of your project directory and add the following lines.

These values can be found in your `apphosting.yaml` file.

```
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_auth_domain
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_storage_bucket
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_messaging_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
```

### 3. Run the Development Server

Start the Next.js development server to see your application running locally.

```bash
npm run dev
```

Your app should now be running at `http://localhost:9002`.

## Deploying from Your Local Machine

You can deploy your application directly from your local machine using the Firebase CLI.

### 1. Login to Firebase

If you haven't already, log in to your Google account through the Firebase CLI.

```bash
firebase login
```

### 2. Select Your Firebase Project

Set the CLI to use your Firebase project. Your project ID is `justicebotai`.

```bash
firebase use justicebotai
```

### 3. Deploy to App Hosting

Deploy your app to Firebase App Hosting with the following command.

```bash
firebase apphosting:deploy
```

The CLI will build your Next.js application and deploy it. Once finished, it will provide you with the URL to your live application.

## Connecting a Custom Domain

To connect `justice-bot.com` to your live application:

1.  After deploying, go to the **App Hosting** section of your Firebase Console.
2.  Find your newly deployed app and click "Add custom domain".
3.  Follow the on-screen instructions to add your domain.
4.  Firebase will provide DNS records (like an `A` record) to add to your domain registrar (where you bought the domain).
5.  Once you've added the records, Firebase will verify your domain and automatically set up a free SSL certificate.
