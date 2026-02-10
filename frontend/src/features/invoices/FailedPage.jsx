import { useEffect, useState } from "react";
import api from "../../shared/api/axios";

export default function FailedPage() {
  const [invoices, setInvoices] = useState([]);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await api.get(
          "/invoices?page=1&limit=50&status=FAILED"
        );
        setInvoices(res.data.data || []);
      } catch (err) {
        console.error(err);
      }
    };

    load();
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-red-400">
        Failed Invoices
      </h1>

      {invoices.length === 0 ? (
        <div className="text-gray-500">
          No failed invoices.
        </div>
      ) : (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 space-y-4">
          {invoices.map(inv => (
            <div
              key={inv.id}
              className="border-b border-gray-800 pb-3"
            >
              <div className="font-medium">
                {inv.vendor || "Unknown Vendor"}
              </div>

              <div className="text-sm text-gray-400">
                Invoice #{inv.invoice_number}
              </div>

              <div className="text-xs text-red-400 mt-1">
                Failed Stage: {inv.processing_stage}
              </div>

              <div className="text-xs text-red-300 mt-1">
                Error: {inv.error_message || "Unknown error"}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
