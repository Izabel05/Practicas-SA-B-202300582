import {
  createContext,
  type ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import type { RoleName } from "../types/auth";

interface WelcomeData {
  firstName: string;
  role: RoleName;
}

interface AuthFeedbackContextValue {
  sessionExpired: boolean;
  welcomeData: WelcomeData | null;
  showSessionExpired: () => void;
  hideSessionExpired: () => void;
  showWelcome: (data: WelcomeData) => void;
  hideWelcome: () => void;
}

interface AuthFeedbackProviderProps {
  children: ReactNode;
}

const AuthFeedbackContext =
  createContext<AuthFeedbackContextValue | null>(null);

export function AuthFeedbackProvider({
  children,
}: AuthFeedbackProviderProps) {
  const [sessionExpired, setSessionExpired] = useState(false);

  const [welcomeData, setWelcomeData] =
    useState<WelcomeData | null>(null);
  useEffect(() => {
    function handleSessionExpired(): void {
      setSessionExpired(true);
    }

    window.addEventListener(
      "auth:session-expired",
      handleSessionExpired,
    );

    return () => {
      window.removeEventListener(
        "auth:session-expired",
        handleSessionExpired,
      );
    };
  }, []);
  const showSessionExpired = useCallback(() => {
    setSessionExpired(true);
  }, []);

  const hideSessionExpired = useCallback(() => {
    setSessionExpired(false);
  }, []);

  const showWelcome = useCallback((data: WelcomeData) => {
    setWelcomeData(data);
  }, []);

  const hideWelcome = useCallback(() => {
    setWelcomeData(null);
  }, []);

  const value = useMemo<AuthFeedbackContextValue>(
    () => ({
      sessionExpired,
      welcomeData,
      showSessionExpired,
      hideSessionExpired,
      showWelcome,
      hideWelcome,
    }),
    [
      sessionExpired,
      welcomeData,
      showSessionExpired,
      hideSessionExpired,
      showWelcome,
      hideWelcome,
    ],
  );

  return (
    <AuthFeedbackContext.Provider value={value}>
      {children}
    </AuthFeedbackContext.Provider>
  );
}

export function useAuthFeedback(): AuthFeedbackContextValue {
  const context = useContext(AuthFeedbackContext);

  if (!context) {
    throw new Error(
      "useAuthFeedback debe utilizarse dentro de AuthFeedbackProvider.",
    );
  }

  return context;
}