import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../shared/api/axios";

export default function ReviewPage() {
  const [invoices, setInvoices] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const load = async () => {
      try {
        const res = await api.get(
          "/invoices?page=1&limit=50&status=REVIEW"
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
      <h1 className="text-2xl font-semibold">
        Invoices Under Review
      </h1>

      {invoices.length === 0 ? (
        <div className="text-gray-500">
          No invoices currently under review.
        </div>
      ) : (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
          {invoices.map(inv => (
            <div
              key={inv.id}
              onClick={() => navigate(`/review/${inv.id}`)}
              className="border-b border-gray-800 py-4 cursor-pointer hover:bg-gray-800/40 transition"
            >
              <div className="font-medium">
                {inv.vendor || "Unknown Vendor"}
              </div>
              <div className="text-sm text-gray-400">
                Invoice #{inv.invoice_number} — ₹ {inv.total}
              </div>
              <div className="text-xs text-yellow-400 mt-1">
                Confidence: {(inv.confidence * 100).toFixed(1)}%
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
