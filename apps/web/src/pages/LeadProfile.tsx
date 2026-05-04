import { useParams } from "react-router-dom";
import { useState, useEffect } from "react";
import { useModule } from "../hooks/useModule";
import { doc, collection, onSnapshot, query, orderBy } from "firebase/firestore";
import { db } from "../lib/firebase";

export default function LeadProfile() {
  const { id } = useParams<{ id: string }>();
  const [activeTab, setActiveTab] = useState("overview");

  // Example of using useModule for Message Optimizer
  const optimizeMutation = useModule<any, any>("/message/optimize");
  const [draft, setDraft] = useState("");
  const [optimized, setOptimized] = useState<any>(null);
  const [researchData, setResearchData] = useState<any>(null);
  
  const [history, setHistory] = useState<any[]>([]);
  const [briefs, setBriefs] = useState<any[]>([]);

  useEffect(() => {
    if (!id) return;
    
    // Trigger background research task on mount
    fetch(`http://localhost:8080/api/v1/leads/${id}`).catch(console.error);

    // Research Listener
    const docRef = doc(db, "leads", id, "research", "data");
    const unsubscribeResearch = onSnapshot(docRef, (snap) => {
      if (snap.exists()) {
        setResearchData(snap.data());
      }
    });
    
    // History Listener
    const historyQ = query(collection(db, "leads", id, "history"), orderBy("created_at", "desc"));
    const unsubscribeHistory = onSnapshot(historyQ, (snap) => {
      setHistory(snap.docs.map(d => d.data()));
    }, () => {}); // ignore permission errors locally
    
    // Briefs Listener
    const briefsQ = query(collection(db, "leads", id, "briefs"), orderBy("created_at", "desc"));
    const unsubscribeBriefs = onSnapshot(briefsQ, (snap) => {
      setBriefs(snap.docs.map(d => d.data()));
    }, () => {});

    return () => {
      unsubscribeResearch();
      unsubscribeHistory();
      unsubscribeBriefs();
    };
  }, [id]);

  const handleOptimize = async () => {
    try {
      const result = await optimizeMutation.mutateAsync({
        draft_message: draft,
        prospect_brief_id: id,
        channel: "email"
      });
      setOptimized(result);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="flex gap-6 h-full">
      <div className="w-1/3 flex flex-col gap-6">
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h2 className="text-2xl font-bold mb-2">Lead Profile</h2>
          <p className="text-slate-500 mb-4">ID: {id}</p>
          <div className="space-y-4">
            <div>
              <h4 className="font-semibold text-sm text-slate-500">Confidence Score</h4>
              <p className="font-medium">85%</p>
            </div>
            {/* Example static data, would normally come from useLeads + Lead object */}
          </div>
        </div>
      </div>

      <div className="w-2/3 bg-white rounded-xl shadow-sm border flex flex-col overflow-hidden">
        <div className="flex border-b">
          {["overview", "history", "optimizer", "call_briefs"].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-6 py-4 font-medium text-sm capitalize ${activeTab === tab ? "border-b-2 border-blue-600 text-blue-600" : "text-slate-500 hover:text-slate-800"}`}
            >
              {tab.replace("_", " ")}
            </button>
          ))}
        </div>
        
        <div className="p-6 flex-1 overflow-auto">
          {activeTab === "optimizer" && (
            <div>
              <h3 className="text-lg font-bold mb-4">Message Optimizer</h3>
              <textarea
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                className="w-full h-32 p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none resize-none mb-4"
                placeholder="Paste your draft message here..."
              />
              <button 
                onClick={handleOptimize}
                disabled={optimizeMutation.isPending || !draft}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50"
              >
                {optimizeMutation.isPending ? "Optimizing..." : "Optimize Message"}
              </button>

              {optimized && (
                <div className="mt-8 p-4 bg-slate-50 rounded-lg border">
                  <h4 className="font-bold mb-2">Optimized Result</h4>
                  <p className="whitespace-pre-wrap mb-4">{optimized.rewritten}</p>
                  
                  <h5 className="font-bold text-sm text-slate-600 mb-2">Changes Made:</h5>
                  <ul className="list-disc list-inside text-sm text-slate-600">
                    {optimized.changes?.map((c: string, i: number) => <li key={i}>{c}</li>)}
                  </ul>
                </div>
              )}
            </div>
          )}
          
          {activeTab === "overview" && (
            <div>
              <h3 className="text-lg font-bold mb-4">Company Overview</h3>
              {researchData ? (
                <div className="space-y-4">
                  <div className="p-4 bg-slate-50 rounded-lg border">
                    <h4 className="font-bold mb-2">Summary</h4>
                    <p className="text-slate-700 text-sm leading-relaxed">{researchData.summary}</p>
                  </div>
                  <div className="p-4 bg-slate-50 rounded-lg border">
                    <h4 className="font-bold mb-2">Recent News</h4>
                    <p className="text-slate-700 text-sm leading-relaxed">{researchData.recent_news}</p>
                  </div>
                  <div className="p-4 bg-slate-50 rounded-lg border">
                    <h4 className="font-bold mb-2">Key Value Proposition</h4>
                    <p className="text-slate-700 text-sm leading-relaxed">{researchData.key_value_proposition}</p>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center p-12 bg-slate-50 rounded-lg border border-dashed">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
                  <p className="text-slate-500 font-medium">Gemini is researching this prospect...</p>
                </div>
              )}
            </div>
          )}
          
          {activeTab === "history" && (
            <div className="space-y-4">
              <h3 className="text-lg font-bold mb-4">Activity History</h3>
              {history.length > 0 ? history.map((item, i) => (
                <div key={i} className="p-4 bg-slate-50 border rounded-lg">
                  <pre className="text-sm">{JSON.stringify(item, null, 2)}</pre>
                </div>
              )) : (
                <p className="text-slate-500">No history available.</p>
              )}
            </div>
          )}
          
          {activeTab === "call_briefs" && (
            <div className="space-y-4">
              <h3 className="text-lg font-bold mb-4">Call Briefs</h3>
              {briefs.length > 0 ? briefs.map((item, i) => (
                <div key={i} className="p-4 bg-slate-50 border rounded-lg">
                  <pre className="text-sm">{JSON.stringify(item, null, 2)}</pre>
                </div>
              )) : (
                <p className="text-slate-500">No call briefs generated yet.</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
