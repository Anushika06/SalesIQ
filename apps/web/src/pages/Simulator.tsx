export default function Simulator() {
  return (
    <div className="bg-white rounded-xl shadow-sm border p-6 min-h-[600px] flex flex-col">
      <h1 className="text-2xl font-bold mb-6">Objection Simulator</h1>
      <p className="text-slate-600 mb-8">Roleplay with an AI prospect to hone your objection handling skills.</p>
      
      <div className="flex-1 flex items-center justify-center border-2 border-dashed border-slate-200 rounded-lg bg-slate-50">
        <div className="text-center">
          <p className="text-slate-500 mb-4">Start a new session to begin simulation.</p>
          <button className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700">
            Start Session
          </button>
        </div>
      </div>
    </div>
  );
}
