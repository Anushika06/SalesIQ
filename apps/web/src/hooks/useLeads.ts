import { useState, useEffect } from "react";
import { collection, onSnapshot, query, orderBy } from "firebase/firestore";
import { db } from "../lib/firebase";

export function useLeads() {
  const [leads, setLeads] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const q = query(collection(db, "leads"), orderBy("updated_at", "desc"));
    const unsubscribe = onSnapshot(q, (snapshot) => {
      const leadsData = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      console.log("Successfully fetched leads:", leadsData);
      setLeads(leadsData);
      setLoading(false);
    }, (error) => {
      console.error("Error fetching leads (Permission or network error):", error);
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  return { leads, loading };
}
