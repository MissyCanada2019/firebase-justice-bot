import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Icons } from '@/components/icons';
import { MainNav } from './main-nav';

export default function SiteHeader() {
  return (
    <header className="absolute inset-x-0 top-0 z-50">
      <nav className="flex items-center justify-between p-6 lg:px-8" aria-label="Global">
        <div className="flex lg:flex-1">
          <Link href="/" className="-m-1.5 p-1.5 flex items-center gap-2">
            <Icons.mapleLeaf className="h-8 w-8 text-accent" />
            <span className="font-headline text-xl font-bold text-foreground">JusticeBot.AI</span>
          </Link>
        </div>
        <div className="hidden lg:flex lg:gap-x-12">
            <MainNav />
        </div>
        <div className="hidden lg:flex lg:flex-1 lg:justify-end">
          <Button asChild>
            <Link href="/dashboard">Login</Link>
          </Button>
        </div>
      </nav>
    </header>
  );
}
