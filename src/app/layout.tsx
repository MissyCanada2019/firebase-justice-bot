import type { Metadata } from 'next';
import { Toaster } from '@/components/ui/toaster';
import FloatingLeaves from '@/components/floating-leaves';
import './globals.css';
import { AuthProvider } from '@/hooks/use-auth';
import Script from 'next/script';

export const metadata: Metadata = {
  metadataBase: new URL('https://justice-bot.com'),
  title: 'JusticeBot.AI - Your Partner in Canadian Law',
  description:
    'AI-powered legal analysis, document summaries, and argument generation based on Canadian law. Specializing in Family, Criminal, and LTB matters with a focus on the Charter of Rights and Freedoms.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=PT+Sans:wght@400;700&display=swap" rel="stylesheet" />
        <Script 
          src={`https://www.google.com/recaptcha/enterprise.js?render=${process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY}`} 
          strategy="lazyOnload" 
        />
      </head>
      <body className="font-body antialiased min-h-screen">
        <AuthProvider>
          <FloatingLeaves />
          {children}
          <Toaster />
        </AuthProvider>
      </body>
    </html>
  );
}
