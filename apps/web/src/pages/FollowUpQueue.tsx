import { useFollowUpQueue } from "../hooks/useFollowUpQueue";

export default function FollowUpQueue() {
  const { queue, loading } = useFollowUpQueue();

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6 min-h-[600px]">
      <div className="mb-6 flex justify-between items-center">
        <h1 className="text-2xl font-bold">Follow-up Queue</h1>
        <button className="bg-slate-100 text-slate-700 px-4 py-2 rounded-lg font-medium hover:bg-slate-200">
          Refresh
        </button>
      </div>

      {loading ? (
        <p aria-live="polite">Loading queue...</p>
      ) : queue.length === 0 ? (
        <div className="text-center py-20 text-slate-500">
          <p>No follow-ups queued.</p>
        </div>
      ) : (
        <div className="border rounded-lg overflow-hidden">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b">
                <th className="p-4 font-semibold text-slate-600">Lead ID</th>
                <th className="p-4 font-semibold text-slate-600">Channel</th>
                <th className="p-4 font-semibold text-slate-600">Scheduled Time</th>
                <th className="p-4 font-semibold text-slate-600">Status</th>
                <th className="p-4 font-semibold text-slate-600">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {queue.map((item, i) => (
                <tr key={i} className="hover:bg-slate-50">
                  <td className="p-4">{item.lead_id}</td>
                  <td className="p-4 capitalize">{item.channel}</td>
                  <td className="p-4">{new Date(item.scheduled_time?.seconds * 1000).toLocaleString()}</td>
                  <td className="p-4">
                    <span className="inline-block px-3 py-1 bg-amber-100 text-amber-800 rounded-full text-sm font-medium">
                      Queued
                    </span>
                  </td>
                  <td className="p-4">
                    <button className="text-blue-600 hover:underline font-medium text-sm">
                      Send Now
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
