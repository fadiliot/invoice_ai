import RetryButton from "./RetryButton";

export default function InvoiceTable({ invoices = [], loading, refetch }) {
  if (loading) {
    return (
      <div className="text-gray-400 animate-pulse">
        Loading invoices...
      </div>
    );
  }

  if (!invoices || invoices.length === 0) {
    return (
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 text-gray-500">
        No invoices found.
      </div>
    );
  }

  const getConfidenceStyle = (confidence) => {
    if (confidence == null) return "bg-gray-700 text-gray-400";
    if (confidence >= 0.9) return "bg-green-500/10 text-green-400";
    if (confidence >= 0.7) return "bg-yellow-500/10 text-yellow-400";
    return "bg-red-500/10 text-red-400";
  };

  const stageStyles = {
    PENDING: "bg-blue-500/10 text-blue-400",
    PROCESSING: "bg-yellow-500/10 text-yellow-400",
    REVIEW: "bg-orange-500/10 text-orange-400",
    QB_SYNCED: "bg-green-500/10 text-green-400",
    FAILED: "bg-red-500/10 text-red-400",
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
      <table className="min-w-full text-sm">
        <thead className="bg-gray-950 text-gray-400 uppercase text-xs">
          <tr>
            <th className="p-3 text-left">Vendor</th>
            <th className="p-3 text-left">Invoice #</th>
            <th className="p-3 text-left">Total</th>
            <th className="p-3 text-left">Stage</th>
            <th className="p-3 text-left">Confidence</th>
            <th className="p-3 text-left">Processing Time</th>
            <th className="p-3 text-left">QB ID</th>
          </tr>
        </thead>

        <tbody>
          {invoices.map((inv) => (
            <tr
              key={inv.id}
              className="border-t border-gray-800 hover:bg-gray-800/40 transition"
            >
              <td className="p-3">{inv.vendor || "-"}</td>

              <td className="p-3">
                {inv.invoice_number || "-"}
              </td>

              <td className="p-3">
                ₹ {inv.total != null ? inv.total : "-"}
              </td>

              <td className="p-3">
                <span
                  className={`px-2 py-1 rounded-md text-xs ${
                    stageStyles[inv.processing_stage] ||
                    "bg-gray-700 text-gray-400"
                  }`}
                >
                  {inv.processing_stage || "-"}
                </span>
              </td>

              <td className="p-3">
                {inv.confidence != null ? (
                  <span
                    className={`px-2 py-1 rounded-md text-xs ${getConfidenceStyle(
                      inv.confidence
                    )}`}
                  >
                    {(inv.confidence * 100).toFixed(1)}%
                  </span>
                ) : (
                  "-"
                )}
              </td>

              <td className="p-3">
                {inv.completed_at != null
                  ? `${Number(inv.completed_at).toFixed(2)}s`
                  : "-"}
              </td>

              <td className="p-3">
                {inv.quickbooks_id ? (
                  <span className="px-2 py-1 bg-green-500/10 text-green-400 rounded-md text-xs font-mono">
                    {inv.quickbooks_id}
                  </span>
                ) : inv.processing_stage === "FAILED" ? (
                  <RetryButton id={inv.id} onSuccess={refetch} />
                ) : (
                  "-"
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
