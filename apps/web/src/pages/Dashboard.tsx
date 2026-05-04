import { Link } from "react-router-dom";
import { useLeads } from "../hooks/useLeads";

export default function Dashboard() {
  const { leads, loading } = useLeads();

  return (
    <div>
      <div className="mb-8 flex justify-between items-center">
        <h1 className="text-3xl font-bold">Dashboard</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        {[
          { title: "Total Leads", value: leads.length },
          { title: "Messages Sent", value: "142" },
          { title: "Avg Response", value: "24%" },
          { title: "Queued Follow-ups", value: "12" }
        ].map((stat, i) => (
          <div key={i} className="bg-white rounded-xl shadow-sm border p-6">
            <h3 className="text-slate-500 text-sm font-medium mb-2">{stat.title}</h3>
            <p className="text-3xl font-bold">{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h2 className="text-xl font-bold mb-4">Recent Leads</h2>
        {loading ? (
          <p aria-live="polite">Loading leads...</p>
        ) : leads.length === 0 ? (
          <p className="text-slate-500">No leads found. Set up some data in Firestore.</p>
        ) : (
          <div className="divide-y">
            {leads.map((lead) => (
              <div key={lead.id} className="py-4 flex justify-between items-center">
                <div>
                  <h3 className="font-semibold">{lead.name || "Unknown"}</h3>
                  <p className="text-sm text-slate-500">{lead.company || "Unknown Company"}</p>
                </div>
                <Link 
                  to={`/leads/${lead.id}`} 
                  className="text-blue-600 hover:bg-blue-50 px-4 py-2 rounded-lg font-medium transition-colors"
                >
                  View Profile
                </Link>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
