import { useParams } from "react-router-dom";
import { useState, useEffect, useCallback } from "react";
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
  const [error, setError] = useState<string | null>(null);

  // Dedicated useEffect for Call Briefs
  useEffect(() => {
    if (!id) return;
    
    const briefsQ = query(collection(db, "leads", id, "call_briefs"));
    const unsubscribeBriefs = onSnapshot(briefsQ, (snap) => {
      const data = snap.docs.map(d => d.data());
      setBriefs(data);
    }, (error) => { 
      console.error('Fetch failed:', error); 
    });

    return () => {
      unsubscribeBriefs();
    };
  }, [id]);

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
    const historyQ = query(collection(db, "leads", id, "history"), orderBy("timestamp", "desc"));
    const unsubscribeHistory = onSnapshot(historyQ, (snap) => {
      setHistory(snap.docs.map(d => d.data()));
    }, (error) => { console.error("History fetch error:", error); });
    
    return () => {
      unsubscribeResearch();
      unsubscribeHistory();
    };
  }, [id]);

  const handleOptimize = useCallback(async () => {
    try {
      setError(null);
      const result = await optimizeMutation.mutateAsync({
        draft_message: draft,
        prospect_brief_id: id,
        channel: "email"
      });
      setOptimized(result);
    } catch (e) {
      console.error(e);
      setError("Failed to optimize message. Please try again.");
    }
  }, [draft, id, optimizeMutation]);

  return (
    <main className="flex gap-6 h-full">
      <aside className="w-1/3 flex flex-col gap-6">
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
      </aside>

      <section className="w-2/3 bg-white rounded-xl shadow-sm border flex flex-col overflow-hidden">
        <nav aria-label="Lead profile tabs" className="flex p-3 bg-slate-50/50 border-b gap-2">
          {["overview", "history", "optimizer", "call_briefs"].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-5 py-2.5 font-medium text-sm capitalize rounded-lg transition-all duration-200 ${
                activeTab === tab 
                  ? "bg-white text-blue-600 shadow-sm border border-slate-200" 
                  : "text-slate-500 hover:text-slate-800 hover:bg-slate-100/50"
              }`}
            >
              {tab.replace("_", " ")}
            </button>
          ))}
        </nav>
        
        <div className="p-8 flex-1 overflow-auto animate-in fade-in duration-300">
          {activeTab === "optimizer" && (
            <div className="animate-in fade-in duration-300">
              <h3 className="text-xl font-bold mb-6 text-slate-800">Message Optimizer</h3>
              {error && <div className="p-3 mb-4 text-sm text-red-600 bg-red-50 rounded-lg border border-red-100">{error}</div>}
              <div className="relative">
                <textarea
                  aria-label="Draft message"
                  value={draft}
                  onChange={(e) => setDraft(e.target.value)}
                  className="w-full h-40 p-5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 outline-none resize-none mb-6 transition-all text-slate-700 placeholder-slate-400 shadow-inner"
                  placeholder="Paste your draft message here to let AI enhance it..."
                />
              </div>
              <button 
                onClick={handleOptimize}
                disabled={optimizeMutation.isPending || !draft}
                aria-disabled={optimizeMutation.isPending || !draft}
                className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-8 py-3 rounded-xl font-medium hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 transition-all shadow-md hover:shadow-lg hover:shadow-blue-500/25 flex items-center gap-2 focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
              >
                {optimizeMutation.isPending ? "✨ Optimizing..." : "✨ Optimize Message"}
              </button>

              {optimized && (
                <div className="mt-8 p-6 bg-gradient-to-br from-indigo-50 to-blue-50 rounded-xl border border-indigo-100 shadow-sm animate-in fade-in slide-in-from-bottom-4 duration-500">
                  <h4 className="font-bold mb-4 text-indigo-900 flex items-center gap-2">
                    <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                    Optimized Result
                  </h4>
                  <p className="whitespace-pre-wrap mb-6 text-slate-800 text-lg leading-relaxed bg-white/60 p-5 rounded-lg border border-indigo-50">{optimized.rewritten}</p>
                  
                  <h5 className="font-bold text-sm text-indigo-800/80 mb-3 uppercase tracking-wider">Changes Made</h5>
                  <ul className="space-y-2 text-indigo-900/80">
                    {optimized.changes?.map((c: string, i: number) => (
                      <li key={i} className="flex gap-2 items-start">
                        <span className="text-indigo-400 mt-1">•</span>
                        <span>{c}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
          
          {activeTab === "overview" && (
            <div className="animate-in fade-in duration-300">
              <h3 className="text-xl font-bold mb-6 text-slate-800">Company Overview</h3>
              {researchData ? (
                <div className="space-y-6">
                  <div className="p-6 bg-white rounded-xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                    <h4 className="font-bold mb-3 flex items-center gap-2 text-slate-800">
                      <svg className="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h7" /></svg>
                      Summary
                    </h4>
                    <p className="text-slate-600 leading-relaxed">{researchData.summary}</p>
                  </div>
                  <div className="p-6 bg-white rounded-xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                    <h4 className="font-bold mb-3 flex items-center gap-2 text-slate-800">
                      <svg className="w-5 h-5 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" /></svg>
                      Recent News
                    </h4>
                    <p className="text-slate-600 leading-relaxed">{researchData.recent_news}</p>
                  </div>
                  <div className="p-6 bg-white rounded-xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                    <h4 className="font-bold mb-3 flex items-center gap-2 text-slate-800">
                      <svg className="w-5 h-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                      Key Value Proposition
                    </h4>
                    <p className="text-slate-600 leading-relaxed">{researchData.key_value_proposition}</p>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center p-16 bg-slate-50/50 rounded-2xl border border-dashed border-slate-200">
                  <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mb-4"></div>
                  <p className="text-slate-500 font-medium">Gemini is researching this prospect...</p>
                </div>
              )}
            </div>
          )}
          
          {activeTab === "history" && (
            <div className="animate-in fade-in duration-300">
              <h3 className="text-xl font-bold mb-8 text-slate-800">Activity History</h3>
              <div className="relative border-l-2 border-slate-200 ml-4 space-y-8">
                {history.length > 0 ? history.map((item, i) => {
                  const dateObj = item.timestamp?.seconds 
                    ? new Date(item.timestamp.seconds * 1000) 
                    : new Date(item.timestamp || Date.now());
                  return (
                    <div key={i} className="pl-8 relative group">
                      <div className="absolute w-4 h-4 bg-white border-4 border-blue-500 rounded-full -left-[9px] top-1 group-hover:scale-125 transition-transform shadow-sm"></div>
                      <div className="p-5 bg-white border border-slate-100 shadow-sm rounded-xl hover:shadow-md transition-shadow">
                        <div className="flex justify-between items-center mb-3">
                          <span className="font-bold text-slate-800 text-lg">{item.title}</span>
                          <span className="text-xs font-bold text-slate-500 bg-slate-100 px-3 py-1 rounded-full uppercase tracking-wider">
                            {item.type}
                          </span>
                        </div>
                        <p className="text-slate-600 mb-4 leading-relaxed">{item.content}</p>
                        <span className="text-xs font-medium text-slate-400 flex items-center gap-1.5">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                          {dateObj.toLocaleString()}
                        </span>
                      </div>
                    </div>
                  );
                }) : (
                  <p className="pl-8 text-slate-500 italic">No history available yet.</p>
                )}
              </div>
            </div>
          )}
          
          {activeTab === "call_briefs" && (
            <div className="space-y-4">
              <h3 className="text-lg font-bold mb-4">Call Briefs</h3>
              {briefs.length > 0 ? briefs.map((item, i) => (
                <div key={i} className="p-6 bg-white border shadow-sm rounded-xl space-y-6 hover:shadow-md transition-shadow">
                  <div>
                    <h4 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-2">
                      <span className="w-2 h-2 bg-blue-600 rounded-full"></span>
                      Objective
                    </h4>
                    <p className="text-slate-800 font-medium text-lg leading-relaxed bg-blue-50/50 p-4 rounded-lg border border-blue-100">{item.objective}</p>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="bg-slate-50 p-5 rounded-lg border">
                      <h4 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-3">Talking Points</h4>
                      <ul className="space-y-2 text-slate-700">
                        {item.talking_points?.map((point: string, idx: number) => (
                          <li key={idx} className="flex gap-2">
                            <span className="text-blue-500 mt-1">•</span>
                            <span>{point}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    <div className="bg-slate-50 p-5 rounded-lg border">
                      <h4 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-3">Questions to Ask</h4>
                      <ul className="space-y-2 text-slate-700">
                        {item.questions?.map((q: string, idx: number) => (
                          <li key={idx} className="flex gap-2">
                            <span className="text-purple-500 mt-1">?</span>
                            <span>{q}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  <div className="bg-rose-50/50 p-6 rounded-xl border border-rose-100">
                    <h4 className="text-sm font-bold text-rose-800/70 uppercase tracking-wider mb-4 flex items-center gap-2">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                      Potential Objections
                    </h4>
                    <ul className="space-y-4">
                      {item.objections?.map((obj: any, idx: number) => (
                        <li key={idx} className="flex gap-4 bg-white p-4 rounded-xl border border-rose-100/60 shadow-sm">
                          <span className="text-rose-500 mt-1 font-bold text-lg leading-none">×</span>
                          <div className="flex-1">
                            <p className="font-semibold text-slate-800 text-lg">{typeof obj === 'string' ? obj : obj.objection}</p>
                            {typeof obj === 'object' && obj.rebuttal && (
                              <div className="mt-4 p-4 bg-emerald-50 rounded-lg border border-emerald-100">
                                <p className="text-sm text-emerald-900 leading-relaxed"><span className="font-bold text-emerald-700 flex items-center gap-1.5 mb-1">
                                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                                  Suggested Rebuttal
                                </span> {obj.rebuttal}</p>
                              </div>
                            )}
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="text-xs text-slate-400 mt-4 pt-4 border-t flex justify-between items-center">
                    <span>Generated on {item.created_at?.seconds ? new Date(item.created_at.seconds * 1000).toLocaleString() : new Date(item.created_at || Date.now()).toLocaleString()}</span>
                  </div>
                </div>
              )) : (
                <div className="flex flex-col items-center justify-center p-12 bg-slate-50 rounded-lg border border-dashed">
                  <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mb-4">
                    <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                  </div>
                  <p className="text-slate-500 font-medium text-lg">No call briefs generated yet.</p>
                  <p className="text-slate-400 text-sm mt-1 mb-6">Generate a call brief to see it here.</p>
                  <button className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors shadow-sm">
                    Generate Call Brief
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </section>
    </main>
  );
}
