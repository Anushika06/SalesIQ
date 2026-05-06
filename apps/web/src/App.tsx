import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useAuth } from "./hooks/useAuth";
import Dashboard from "./pages/Dashboard";
import LeadProfile from "./pages/LeadProfile";

const queryClient = new QueryClient();

function Layout({ children }: { children: React.ReactNode }) {
  const { user, loginWithGoogle, logout, loading } = useAuth();

  if (loading) return <div className="p-8 text-center" aria-live="polite">Loading...</div>;

  if (!user) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50">
        <div className="text-center">
          <h1 className="text-4xl font-bold mb-4">SalesIQ</h1>
          <button 
            onClick={loginWithGoogle}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 font-medium"
          >
            Sign in with Google
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <header className="bg-white border-b px-6 py-4 flex justify-between items-center shadow-sm">
        <div className="flex items-center gap-6">
          <h1 className="text-2xl font-bold text-blue-600">SalesIQ</h1>
          <nav className="flex gap-4">
            <Link to="/" className="text-slate-600 hover:text-slate-900 font-medium">Dashboard</Link>
            {/* MVP Scope: Hidden for now
            <Link to="/simulator" className="text-slate-600 hover:text-slate-900 font-medium">Simulator</Link>
            <Link to="/ab-tester" className="text-slate-600 hover:text-slate-900 font-medium">A/B Tester</Link>
            <Link to="/followups" className="text-slate-600 hover:text-slate-900 font-medium">Queue</Link>
            */}
          </nav>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm font-medium text-slate-600">{user.email}</span>
          <button onClick={logout} className="text-sm text-slate-500 hover:text-slate-700">Logout</button>
        </div>
      </header>
      <main className="flex-1 p-6 max-w-7xl mx-auto w-full">
        {children}
      </main>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/leads/:id" element={<LeadProfile />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
