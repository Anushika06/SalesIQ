import { useMutation } from "@tanstack/react-query";
import { auth } from "../lib/firebase";

const API_BASE = "http://localhost:8080/api/v1";

export function useModule<TData, TVariables>(moduleEndpoint: string) {
  return useMutation<TData, Error, TVariables>({
    mutationFn: async (variables) => {
      let token = "";
      if (auth.currentUser) {
        token = await auth.currentUser.getIdToken();
      }

      const response = await fetch(`${API_BASE}${moduleEndpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(variables),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || `API Error: ${response.statusText}`);
      }

      return response.json();
    }
  });
}
