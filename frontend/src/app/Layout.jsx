import { Link, Outlet } from "react-router-dom";

export default function Layout() {
  return (
    <div className="flex min-h-screen bg-slate-900 text-gray-200">
      <aside className="w-64 bg-gray-950 border-r border-gray-800 p-6 space-y-4">
        <h2 className="text-lg font-semibold mb-6">
          Invoice AI
        </h2>

        <nav className="flex flex-col space-y-2 text-sm">
          <Link to="/" className="hover:text-blue-400">
            Dashboard
          </Link>

          <Link to="/invoices" className="hover:text-blue-400">
            All Invoices
          </Link>

          <Link to="/review" className="hover:text-blue-400">
            Needs Review
          </Link>

          <Link to="/failed" className="hover:text-blue-400">
            Failed
          </Link>
        </nav>
      </aside>

      <main className="flex-1 p-8">
        <Outlet />
      </main>
    </div>
  );
}
