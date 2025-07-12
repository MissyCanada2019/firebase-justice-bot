
import Image from 'next/image';
import SiteHeader from '@/components/site-header';
import { Icons } from '@/components/icons';

export default function AboutPage() {
  return (
    <div className="bg-background min-h-screen">
      <SiteHeader />
      <main className="relative py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl lg:mx-0">
            <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-6xl font-headline">
              Our Story
            </h1>
            <p className="mt-6 text-lg leading-8 text-foreground/80">
              The journey of a Canadian mom turned legal self-advocate, and the creation of JusticeBot.AI.
            </p>
          </div>
          <div className="mx-auto mt-16 grid max-w-2xl grid-cols-1 gap-x-8 gap-y-16 lg:mx-0 lg:mt-24 lg:max-w-none lg:grid-cols-2">
            <div className="lg:pr-8 lg:pt-4">
              <div className="lg:max-w-lg">
                <h2 className="text-base font-semibold leading-7 text-accent font-body">Teresa's Journey</h2>
                <p className="mt-2 text-3xl font-bold tracking-tight text-foreground sm:text-4xl font-headline">
                  From Personal Struggle to Public Service
                </p>
                <p className="mt-6 text-lg leading-8 text-foreground/70">
                  Teresa's journey into the world of Canadian law was not by choice, but by necessity. As a mother navigating a complex legal system to protect her family, she faced firsthand the daunting challenges of self-representation. The legal jargon, procedural complexities, and the sheer volume of information were overwhelming barriers.
                </p>
                <div className="mt-8 space-y-6 text-foreground/70 text-base">
                  <p>
                    Determined and resilient, Teresa dedicated herself to understanding the law. She spent countless hours in libraries and online, poring over statutes, case law, and legal guides. Her fight was not just for her own family, but became a mission to empower others in similar situations.
                  </p>
                  <p>
                    This experience ignited a passion to make justice more accessible for all Canadians. Teresa envisioned a tool that could demystify the law, a partner that could help people understand their rights and build their cases. This vision is now JusticeBot.AI.
                  </p>
                </div>
              </div>
            </div>
            <div className="space-y-8">
              <Image
                src="https://placehold.co/600x400.png"
                data-ai-hint="woman working laptop"
                alt="Teresa working on her legal case, with a quote from the Charter of Rights and Freedoms."
                className="w-full rounded-2xl object-cover shadow-xl"
                width={600}
                height={400}
              />
               <Image
                src="https://placehold.co/600x400.png"
                data-ai-hint="happy family outdoors"
                alt="Teresa with her family, with a quote from the Charter of Rights and Freedoms."
                className="w-full rounded-2xl object-cover shadow-xl"
                width={600}
                height={400}
              />
            </div>
          </div>

          <div className="mt-24 text-center">
             <Icons.mapleLeaf className="text-accent h-12 w-12 mx-auto mb-4" />
             <h3 className="font-headline text-2xl font-bold text-foreground">Built for Canadians, by a Canadian</h3>
             <p className="mt-4 max-w-3xl mx-auto text-lg text-foreground/80">
                JusticeBot.AI is more than just an application; it's the culmination of a personal battle for justice, designed to ensure no Canadian has to walk their legal path alone.
             </p>
          </div>

        </div>
      </main>
    </div>
  );
}
