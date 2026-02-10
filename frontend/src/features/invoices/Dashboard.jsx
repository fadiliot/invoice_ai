import { useState, useEffect, useRef } from "react";
import useInvoices from "./useinvoices";
import { fetchDashboardStats } from "./api";
import InvoiceTable from "./InvoiceTable";
import Filters from "./Filters";
import StatsCards from "../../shared/components/StatsCards";
import Pagination from "../../shared/components/Pagination";
import TopBar from "../../app/TopBar";
import UploadInvoices from "./UploadInvoices";



export default function Dashboard() {
  const [query, setQuery] = useState({
    page: 1,
    limit: 10,
    search: "",
    stage: "",
    sort: "created_at",
    order: "desc",
  });

  const { data, total, loading, refetch } = useInvoices(query);

  const [stats, setStats] = useState(null);

  // Prevent double fetch in React StrictMode (dev only)
  const hasFetched = useRef(false);

  useEffect(() => {
    if (hasFetched.current) return;
    hasFetched.current = true;

    const loadStats = async () => {
      try {
        const res = await fetchDashboardStats();
        setStats(res.data);
      } catch (err) {
        console.error("Stats fetch error:", err);
      }
    };

    loadStats();
  }, []);

 return (
  <div className="min-h-screen bg-slate-900 text-gray-200 p-8 space-y-8">
    <TopBar
      title="Invoice AI Dashboard"
      onUploadSuccess={refetch}
    />

    <StatsCards stats={stats} />

    <Filters query={query} setQuery={setQuery} />

    <InvoiceTable
      invoices={data}
      loading={loading}
      refetch={refetch}
    />

    <Pagination
      page={query.page}
      limit={query.limit}
      total={total}
      setQuery={setQuery}
    />
  </div>
);
}