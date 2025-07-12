'use client';

import {
  SidebarHeader,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarFooter,
  SidebarContent,
  SidebarSeparator,
} from '@/components/ui/sidebar';
import {
  BookOpen,
  Gavel,
  Home,
  Landmark,
  Scale,
  ShieldCheck,
  FileText,
  CreditCard,
  CalendarClock,
  FilePlus2,
  FileSearch,
  MapPin,
  Library,
  MessageCircle,
  FolderOpen,
} from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Button } from '../ui/button';
import { Icons } from '../icons';

const menuItems = [
  { href: '/dashboard', label: 'Dashboard', icon: Home },
  {
    href: '/dashboard/ask-justicebot',
    label: 'Ask JusticeBot',
    icon: MessageCircle,
  },
  {
    href: '/dashboard/submit-dispute',
    label: 'Submit Dispute',
    icon: FileText,
  },
  {
    href: '/dashboard/evidence-locker',
    label: 'Evidence Locker',
    icon: FolderOpen,
  },
  {
    href: '/dashboard/timeline',
    label: 'Legal Timeline',
    icon: CalendarClock,
  },
  {
    href: '/dashboard/generate-form',
    label: 'Generate Form',
    icon: FilePlus2,
  },
  {
    href: '/dashboard/court-locator',
    label: 'Court Locator',
    icon: MapPin,
  },
  {
    href: '/dashboard/precedent-finder',
    label: 'Precedent Finder',
    icon: Library,
  },
  {
    href: '/dashboard/charter-analysis',
    label: 'Charter Analysis',
    icon: Gavel,
  },
  {
    href: '/dashboard/document-explainer',
    label: 'Document Explainer',
    icon: FileSearch,
  },
  { href: '/dashboard/family-law', label: 'Family Law', icon: ShieldCheck },
  { href: '/dashboard/criminal-law', label: 'Criminal Law', icon: Scale },
  { href: '/dashboard/ltb-law', label: 'LTB Law', icon: Landmark },
  {
    href: '/dashboard/litigation-law',
    label: 'Litigation Law',
    icon: BookOpen,
  },
  { href: '/dashboard/billing', label: 'Pricing & Plans', icon: CreditCard },
];

export function SidebarNav() {
  const pathname = usePathname();

  return (
    <>
      <SidebarHeader>
        <Link href="/dashboard" className="flex items-center gap-2">
          <Icons.justiceBotLogo className="h-8 w-auto" />
          <span className="font-headline text-lg font-bold text-sidebar-foreground">
            JusticeBot.AI
          </span>
        </Link>
      </SidebarHeader>
      <SidebarContent>
        <SidebarMenu>
          {menuItems.map((item) => (
            <SidebarMenuItem key={item.href}>
              <Link href={item.href} passHref legacyBehavior>
                <SidebarMenuButton
                  isActive={pathname === item.href}
                  tooltip={item.label}
                >
                  <item.icon className="w-5 h-5" />
                  <span>{item.label}</span>
                </SidebarMenuButton>
              </Link>
            </SidebarMenuItem>
          ))}
        </SidebarMenu>
      </SidebarContent>
      <SidebarFooter>
        <SidebarSeparator />
        <div className="p-2 flex flex-col gap-2">
            <div className="p-4 rounded-lg bg-sidebar-accent/20 text-center text-sm">
                <p className="font-bold text-sidebar-foreground">Need Help?</p>
                <p className="text-sidebar-foreground/80 mt-1">Contact support or visit our help center.</p>
                <Button variant="link" size="sm" className="text-accent-foreground mt-2">Get Support</Button>
            </div>
        </div>
      </SidebarFooter>
    </>
  );
}
