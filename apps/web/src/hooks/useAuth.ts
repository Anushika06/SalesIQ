import { useState, useEffect } from "react";
// Real Firebase imports commented out for Dev Mode bypass
// import { signInWithPopup, signOut, onAuthStateChanged, type User } from "firebase/auth";
// import { auth, googleProvider } from "../lib/firebase";

export function useAuth() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  // DEV MODE BYPASS: Auto-login disabled so you still see the login screen,
  // but clicking it logs you in instantly with a fake user.
  useEffect(() => {
    setLoading(false);
  }, []);

  const loginWithGoogle = async () => {
    try {
      // DEV MODE: Set a fake user with a fake token generator
      setUser({ 
        email: "demo-rep@salesiq.app", 
        uid: "dev-user",
        getIdToken: async () => "dev-token" 
      });
    } catch (error) {
      console.error("Login failed:", error);
    }
  };

  const logout = async () => {
    try {
      setUser(null);
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  return { user, loading, loginWithGoogle, logout };
}
