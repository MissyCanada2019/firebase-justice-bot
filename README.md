# JusticeBot.AI on Firebase Studio

This is your project for JusticeBot.AI, built with Next.js and ready for deployment on Firebase.

## Local Development & Deployment

To run and deploy this project from your local machine, follow these steps.

### Prerequisites

*   You have an account with [Firebase](https://firebase.google.com/).
*   [Node.js](https://nodejs.org/) (version 20 or later recommended).
*   [Firebase CLI](https://firebase.google.com/docs/cli#install-cli-npm) installed on your machine.

### Step 1: Get the Project Files

Create a new directory on your local machine and copy all the project files from Firebase Studio into it.

### Step 2: Install Dependencies

Once you have the project files on your local machine, navigate to the project directory in your terminal and install the necessary dependencies.

```bash
npm install
```

### Step 3: Set Up Environment Variables

Your project requires Firebase configuration to run locally. Create a new file named `.env.local` in the root of your project directory and add the following lines.

These values can be found in your `apphosting.yaml` file.

```
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_auth_domain
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_storage_bucket
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_messaging_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
```

### Step 4: Run the Local Development Server

Start the Next.js development server to see your application running locally.

```bash
npm run dev
```

Your app should now be running at `http://localhost:9002`.

### Step 5: Initialize Firebase in Your Project

This is a crucial step to connect your local project folder to your Firebase project.

1.  **Log in to Firebase:**
    ```bash
    firebase login
    ```

2.  **Initialize Firebase:**
    Run the following command from your project's root directory:
    ```bash
    firebase init
    ```

3.  **Follow the prompts:**
    *   When asked "Which Firebase features do you want to set up?", use the arrow keys to navigate to **App Hosting** and press the spacebar to select it, then press Enter.
    *   When asked to select a project, choose **Use an existing project** and select `justicebotai` from the list.
    *   When asked for your backend ID, you can find this in the Firebase Console under App Hosting. It will likely be named something like `justicebotai`.
    *   It will ask about deploying with `npm run build`. You can accept the default.

This will create a `.firebaserc` file in your project, officially linking it to Firebase.

### Step 6: Deploy to App Hosting

Now that your project is initialized, you can deploy it directly from your local machine.

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
