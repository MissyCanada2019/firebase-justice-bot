import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  BookOpen,
  Gavel,
  Landmark,
  Scale,
  ShieldCheck,
  FileText,
  ArrowRight,
  CalendarClock,
  FilePlus2,
  FileSearch,
} from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

const features = [
  {
    title: 'Submit a Dispute',
    description: 'Upload your case documents and evidence for analysis.',
    icon: FileText,
    href: '/dashboard/submit-dispute',
  },
  {
    title: 'Legal Timeline',
    description: 'Get a step-by-step timeline for your legal process.',
    icon: CalendarClock,
    href: '/dashboard/timeline',
  },
  {
    title: 'Generate Legal Form',
    description: 'Auto-fill legal forms based on your case details.',
    icon: FilePlus2,
    href: '/dashboard/generate-form',
  },
  {
    title: 'Charter Analysis',
    description: 'Analyze documents against the Charter of Rights and Freedoms.',
    icon: Gavel,
    href: '/dashboard/charter-analysis',
  },
  {
    title: 'Document Explainer',
    description: 'Get plain-language explanations for any legal document or form.',
    icon: FileSearch,
    href: '/dashboard/document-explainer',
  },
  {
    title: 'Family Law',
    description: 'Get summaries of family law for any province or territory.',
    icon: ShieldCheck,
    href: '/dashboard/family-law',
  },
  {
    title: 'Criminal Law',
    description: 'Access summaries of criminal law across Canada.',
    icon: Scale,
    href: '/dashboard/criminal-law',
  },
  {
    title: 'LTB Law',
    description: 'Understand Landlord and Tenant Board laws and regulations.',
    icon: Landmark,
    href: '/dashboard/ltb-law',
  },
  {
    title: 'Litigation Law',
    description: 'Explore litigation procedures and generate arguments.',
    icon: BookOpen,
    href: '/dashboard/litigation-law',
  },
];

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight font-headline">
          Welcome to your Dashboard
        </h1>
        <p className="text-muted-foreground">
          Here are the tools to help you navigate your legal journey.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {features.map((feature) => (
          <Card key={feature.title} className="flex flex-col">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-lg font-medium font-headline">
                {feature.title}
              </CardTitle>
              <feature.icon className="h-6 w-6 text-muted-foreground" />
            </CardHeader>
            <CardContent className="flex-grow">
              <p className="text-sm text-muted-foreground">
                {feature.description}
              </p>
            </CardContent>
            <div className="p-6 pt-0">
              <Button asChild className="w-full">
                <Link href={feature.href}>
                  Go to Tool <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
