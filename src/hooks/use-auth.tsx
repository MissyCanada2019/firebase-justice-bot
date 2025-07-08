'use client';

import { useState, useEffect, createContext, useContext, ReactNode } from 'react';
import { onAuthStateChanged, User, GoogleAuthProvider, signInWithPopup, signOut, getAdditionalUserInfo } from 'firebase/auth';
import { auth } from '@/lib/firebase';
import { useRouter } from 'next/navigation';
import { useToast } from './use-toast';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  signInWithGoogle: () => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const { toast } = useToast();

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user);
      setLoading(false);
    });
    return () => unsubscribe();
  }, []);

  const signInWithGoogle = async () => {
    const isFreeTierEnabled = process.env.NEXT_PUBLIC_FREE_TIER_ENABLED === 'true';

    if (isFreeTierEnabled) {
      // TODO: In a production environment, this check must be done on the server
      // using the Firebase Admin SDK to securely get the total number of users.
      // This client-side check is for demonstration purposes only.
      const isLimitReached = false; // Placeholder for the real server-side check.
      
      if (isLimitReached) {
        toast({
          title: 'Registration Closed',
          description: 'We have reached our limit for free sign-ups. Please check back later!',
          variant: 'destructive',
        });
        return;
      }
    }

    const provider = new GoogleAuthProvider();
    try {
      const result = await signInWithPopup(auth, provider);
      const additionalUserInfo = getAdditionalUserInfo(result);
      
      if (additionalUserInfo?.isNewUser) {
        router.push('/dashboard/welcome');
      } else {
        router.push('/dashboard');
      }
    } catch (error: any) {
      console.error("Error signing in with Google", error);
      if (error.code === 'auth/auth-domain-config-required') {
        // Force the user to the troubleshooting page to fix the issue.
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
    <AuthContext.Provider value={{ user, loading, signInWithGoogle, logout }}>
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
