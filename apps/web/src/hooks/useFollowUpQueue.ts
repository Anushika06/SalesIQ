import { useState, useEffect } from "react";
import { collection, onSnapshot, query, orderBy } from "firebase/firestore";
import { db } from "../lib/firebase";

export function useFollowUpQueue() {
  const [queue, setQueue] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Assuming followups are stored in 'followups' collection when queued
    const q = query(collection(db, "followups"), orderBy("scheduled_time", "asc"));
    const unsubscribe = onSnapshot(q, (snapshot) => {
      const queueData = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      setQueue(queueData);
      setLoading(false);
    }, (error) => {
      console.error("Error fetching followup queue:", error);
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  return { queue, loading };
}
