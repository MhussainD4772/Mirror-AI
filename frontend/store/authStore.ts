import { User, Session } from "@supabase/supabase-js";
import { supabase } from "../utils/supabase";
import { useState, useEffect } from "react";

interface AuthStore {
  user: User | null;
  session: Session | null;
  loading: boolean;
  setUser: (user: User | null) => void;
  clearUser: () => void;
}

// Simple store implementation using React state
// Note: This is a basic implementation. For production, consider using Zustand or Context API
// The AuthContext in contexts/AuthContext.tsx provides a more complete solution

let authStore: AuthStore = {
  user: null,
  session: null,
  loading: true,
  setUser: () => {},
  clearUser: () => {},
};

// Initialize auth state
export const initializeAuthStore = () => {
  supabase.auth.getSession().then(({ data: { session } }) => {
    authStore.session = session;
    authStore.user = session?.user ?? null;
    authStore.loading = false;
  });

  // Listen for auth changes
  supabase.auth.onAuthStateChange((_event, session) => {
    authStore.session = session;
    authStore.user = session?.user ?? null;
    authStore.loading = false;
  });
};

// Hook to use auth store (for compatibility, but AuthContext is preferred)
export const useAuthStore = (): AuthStore => {
  const [user, setUserState] = useState<User | null>(authStore.user);
  const [session, setSessionState] = useState<Session | null>(
    authStore.session
  );
  const [loading, setLoading] = useState(authStore.loading);

  useEffect(() => {
    // Initialize on mount
    initializeAuthStore();

    // Subscribe to auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, newSession) => {
      authStore.session = newSession;
      authStore.user = newSession?.user ?? null;
      authStore.loading = false;
      setSessionState(newSession);
      setUserState(newSession?.user ?? null);
      setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, []);

  const setUser = (newUser: User | null) => {
    authStore.user = newUser;
    setUserState(newUser);
  };

  const clearUser = () => {
    authStore.user = null;
    authStore.session = null;
    setUserState(null);
    setSessionState(null);
  };

  return {
    user,
    session,
    loading,
    setUser,
    clearUser,
  };
};

export default authStore;
