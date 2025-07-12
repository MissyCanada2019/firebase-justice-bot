
'use client';

import { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { conversationalChat } from '@/ai/flows/conversational-chat';
import { useAuth } from '@/hooks/use-auth';
import { getLatestCaseAssessment, CaseDocument } from '@/lib/firestoreService';
import { MessageCircle, Send, User, Loader2, AlertCircle } from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Icons } from '@/components/icons';
import { cn } from '@/lib/utils';
import Link from 'next/link';
import { useToast } from '@/hooks/use-toast';

type ChatMessage = {
  role: 'user' | 'bot';
  content: string;
};

export default function AskJusticeBotPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [caseContext, setCaseContext] = useState<CaseDocument | null>(null);
  const [loadingContext, setLoadingContext] = useState(true);
  const { user } = useAuth();
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  useEffect(() => {
    if (user) {
      getLatestCaseAssessment(user.uid)
        .then(data => {
          if (data) {
            setCaseContext(data as CaseDocument);
            setMessages([
              {
                role: 'bot',
                content: `Hello! I'm JusticeBot. I've loaded the context from your latest case, "${data.caseName}". How can I help you today? You can ask me to explain parts of your timeline, suggest what to file next, or clarify legal terms.`,
              },
            ]);
          } else {
             setMessages([
              {
                role: 'bot',
                content: "Hello! I'm JusticeBot. It looks like you don't have a case submitted yet. You can ask me general questions about Canadian law, or submit a dispute to get personalized assistance.",
              },
            ]);
          }
        })
        .catch(e => {
          console.error('Error loading case context:', e);
          toast({
            title: 'Could not load case data',
            description: 'There was an error loading your case. You can still ask general questions.',
            variant: 'destructive',
          })
          setMessages([
              {
                role: 'bot',
                content: "Hello! I'm JusticeBot. I had some trouble loading your case data, but you can still ask me general questions about Canadian law.",
              },
            ]);
        })
        .finally(() => {
          setLoadingContext(false);
        });
    }
  }, [user, toast]);

  useEffect(() => {
    if (scrollAreaRef.current) {
        const scrollContainer = scrollAreaRef.current.querySelector('div:first-child');
        if (scrollContainer) {
            scrollContainer.scrollTop = scrollContainer.scrollHeight;
        }
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage: ChatMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await conversationalChat({
        question: input,
        caseContext: caseContext ?? undefined,
        chatHistory: messages,
      });

      const botMessage: ChatMessage = { role: 'bot', content: response.answer };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: ChatMessage = {
        role: 'bot',
        content: "I'm sorry, but I encountered an error and can't respond right now. Please try again later.",
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  if (loadingContext) {
      return <div className="flex justify-center items-center h-full"><Loader2 className="h-8 w-8 animate-spin" /></div>
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] space-y-4">
      <div className="flex items-center gap-4">
        <MessageCircle className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-3xl font-bold tracking-tight font-headline">Ask JusticeBot</h1>
          <p className="text-muted-foreground">Your AI legal assistant. Ask me anything about your case.</p>
        </div>
      </div>
      
      {!caseContext && !loadingContext && (
         <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>No Case Context Loaded</AlertTitle>
            <AlertDescription>
                You can ask general questions, but for personalized help, please submit a dispute first.
                <Button asChild variant="link" className="p-0 h-auto ml-1">
                    <Link href="/dashboard/submit-dispute">Submit a Dispute</Link>
                </Button>
            </AlertDescription>
        </Alert>
      )}

      <Card className="flex-grow flex flex-col">
        <CardContent className="flex-grow p-0">
          <ScrollArea className="h-full p-6" ref={scrollAreaRef}>
            <div className="space-y-6">
              {messages.map((message, index) => (
                <div key={index} className={cn('flex items-start gap-4', message.role === 'user' ? 'justify-end' : 'justify-start')}>
                  {message.role === 'bot' && (
                     <div className="flex-shrink-0 w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                        <Icons.justiceBotLogo className="w-6 h-6 text-primary" />
                    </div>
                  )}
                  <div className={cn('max-w-md p-3 rounded-lg', message.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted')}>
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  </div>
                   {message.role === 'user' && (
                    <div className="flex-shrink-0 w-10 h-10 rounded-full bg-muted flex items-center justify-center">
                        <User className="w-6 h-6 text-muted-foreground" />
                    </div>
                  )}
                </div>
              ))}
              {loading && (
                 <div className="flex items-start gap-4 justify-start">
                    <div className="flex-shrink-0 w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                        <Icons.justiceBotLogo className="w-6 h-6 text-primary" />
                    </div>
                    <div className="max-w-md p-3 rounded-lg bg-muted flex items-center">
                        <Loader2 className="h-5 w-5 animate-spin" />
                    </div>
                </div>
              )}
            </div>
          </ScrollArea>
        </CardContent>
        <div className="p-4 border-t">
          <div className="flex items-center gap-2">
            <Input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyPress={e => e.key === 'Enter' && handleSend()}
              placeholder="e.g., 'What is the next step after filing a T2 form?'"
              disabled={loading}
            />
            <Button onClick={handleSend} disabled={loading}>
              <Send className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
