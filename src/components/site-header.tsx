
'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { MainNav } from './main-nav';
import { useAuth } from '@/hooks/use-auth';
import { Skeleton } from '@/components/ui/skeleton';
import { Icons } from './icons';

export default function SiteHeader() {
  const { user, loading } = useAuth();

  return (
    <header className="absolute inset-x-0 top-0 z-50">
      <nav className="flex items-center justify-between p-6 lg:px-8" aria-label="Global">
        <div className="flex lg:flex-1">
          <Link href="/" className="-m-1.5 p-1.5 flex items-center gap-2">
            <Icons.justiceBotLogo className="h-8 w-auto" />
            <span className="font-headline text-xl font-bold text-foreground">JusticeBot.AI</span>
          </Link>
        </div>
        <div className="hidden lg:flex lg:gap-x-12">
            <MainNav />
        </div>
        <div className="flex items-center gap-4 lg:flex-1 lg:justify-end">
          {loading ? (
            <Skeleton className="h-10 w-24" />
          ) : user ? (
            <Button asChild>
              <Link href="/dashboard">Go to Dashboard</Link>
            </Button>
          ) : (
            <>
                <Button asChild variant="ghost">
                    <Link href="/login">Login</Link>
                </Button>
                 <Button asChild>
                    <Link href="/signup">Sign Up</Link>
                </Button>
            </>
          )}
        </div>
      </nav>
    </header>
  );
}
