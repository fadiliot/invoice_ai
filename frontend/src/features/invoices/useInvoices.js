import { useEffect, useState, useCallback } from "react";
import { fetchInvoices } from "./api";

export default function useInvoices(query) {
  const [data, setData] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);

  const loadInvoices = useCallback(async () => {
    try {
      const res = await fetchInvoices(query);
      setData(res.data.data || []);
      setTotal(res.data.total || 0);
    } catch (err) {
      console.error("Invoice fetch error:", err);
    }
  }, [query]);

  // Initial + query change fetch
  useEffect(() => {
    let mounted = true;

    const fetchData = async () => {
      setLoading(true);
      await loadInvoices();
      if (mounted) setLoading(false);
    };

    fetchData();

    return () => {
      mounted = false;
    };
  }, [loadInvoices]);

  // Smart polling only when active processing exists
  useEffect(() => {
    const hasActive = data.some(
      (inv) =>
        inv.processing_stage === "PENDING" ||
        inv.processing_stage === "PROCESSING"
    );

    if (!hasActive) return;

    const interval = setInterval(() => {
      loadInvoices();
    }, 3000);

    return () => clearInterval(interval);
  }, [data, loadInvoices]);

  return { data, total, loading, refetch: loadInvoices };
}
