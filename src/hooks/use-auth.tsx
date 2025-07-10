'use client';

import { useState, useEffect, createContext, useContext, ReactNode } from 'react';
import { onAuthStateChanged, User, GoogleAuthProvider, signInWithPopup, signOut, getAdditionalUserInfo } from 'firebase/auth';
import { auth } from '@/lib/firebase';
import { useRouter } from 'next/navigation';
import { useToast } from './use-toast';
import { verifyRecaptchaToken } from '@/ai/flows/verify-recaptcha';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  isFreeTier: boolean;
  signInWithGoogle: (recaptchaToken: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const { toast } = useToast();

  // This setting simulates the "first 1000 users" free tier.
  // In a production app, this would be determined by checking the total user count on a secure backend.
  const isFreeTier = process.env.NEXT_PUBLIC_FREE_TIER_ENABLED === 'true';

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user);
      setLoading(false);
    });
    return () => unsubscribe();
  }, []);

  const signInWithGoogle = async (recaptchaToken: string) => {
    try {
      const verification = await verifyRecaptchaToken({ 
        token: recaptchaToken,
        expectedAction: 'LOGIN'
      });

      if (!verification.isValid) {
        toast({
            title: 'Security Check Failed',
            description: `Could not verify you are human. Score: ${verification.score}. Reason: ${verification.reason}`,
            variant: 'destructive',
          });
        return;
      }

      const provider = new GoogleAuthProvider();
      const result = await signInWithPopup(auth, provider);
      const additionalUserInfo = getAdditionalUserInfo(result);
      
      if (additionalUserInfo?.isNewUser) {
        router.push('/dashboard/welcome');
      } else {
        router.push('/dashboard');
      }
    } catch (error: any) {
      if (error.code === 'auth/cancelled-popup-request') {
        // User cancelled the popup, so we do nothing. This is not an error.
        console.log('Sign-in popup closed by user.');
        return;
      }
      
      console.error("Error signing in with Google", error);

      if (error.code === 'auth/unauthorized-domain') {
        router.push('/troubleshooting');
      } else {
         toast({
            title: 'Sign-in Failed',
            description: `An unexpected error occurred: ${error.message || 'Please try again.'}`,
            variant: 'destructive',
        });
      }
    }
  };

  const logout = async () => {
    try {
      await signOut(auth);
      router.push('/');
    } catch (error) {
      console.error("Error signing out", error);
      toast({
          title: 'Sign-out Failed',
          description: 'An error occurred while signing out. Please try again.',
          variant: 'destructive',
      });
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, isFreeTier, signInWithGoogle, logout }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
