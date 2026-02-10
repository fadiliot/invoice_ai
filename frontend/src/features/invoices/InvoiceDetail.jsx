import { useParams, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import api from "../../shared/api/axios";

export default function InvoiceDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [invoice, setInvoice] = useState(null);
  const [form, setForm] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [approving, setApproving] = useState(false);

  useEffect(() => {
    const loadInvoice = async () => {
      try {
        const res = await api.get(`/invoice/${id}`);
        setInvoice(res.data);
        setForm({
          vendor: res.data.vendor || "",
          invoice_number: res.data.invoice_number || "",
          invoice_date: res.data.invoice_date || "",
          total: res.data.total || 0,
          tax: res.data.tax || 0,
        });
      } catch (err) {
        console.error("Invoice load error:", err);
      } finally {
        setLoading(false);
      }
    };

    loadInvoice();
  }, [id]);

  const handleChange = (e) => {
    setForm((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await api.put(`/invoice/${id}`, form);
      setInvoice(res.data);
      alert("Invoice updated successfully");
    } catch (err) {
      console.error("Update error:", err);
    } finally {
      setSaving(false);
    }
  };

  const handleApprove = async () => {
    setApproving(true);
    try {
      await api.post(`/invoice/${id}/approve`);
      alert("Invoice approved and synced");
      navigate("/review");
    } catch (err) {
      console.error("Approve error:", err);
    } finally {
      setApproving(false);
    }
  };

  if (loading) {
    return <div className="text-gray-400">Loading invoice...</div>;
  }

  if (!invoice) {
    return <div className="text-red-400">Invoice not found</div>;
  }

  const isReview = invoice.processing_stage === "REVIEW";

  return (
    <div className="space-y-6 max-w-3xl">
      <h1 className="text-2xl font-semibold">
        Invoice #{invoice.invoice_number}
      </h1>

      <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl space-y-4">

        <div>
          <label className="block text-sm text-gray-400 mb-1">
            Vendor
          </label>
          <input
            name="vendor"
            value={form.vendor}
            onChange={handleChange}
            disabled={!isReview}
            className="w-full bg-gray-950 border border-gray-800 rounded-md px-3 py-2"
          />
        </div>

        <div>
          <label className="block text-sm text-gray-400 mb-1">
            Invoice Number
          </label>
          <input
            name="invoice_number"
            value={form.invoice_number}
            onChange={handleChange}
            disabled={!isReview}
            className="w-full bg-gray-950 border border-gray-800 rounded-md px-3 py-2"
          />
        </div>

        <div>
          <label className="block text-sm text-gray-400 mb-1">
            Invoice Date
          </label>
          <input
            name="invoice_date"
            value={form.invoice_date}
            onChange={handleChange}
            disabled={!isReview}
            className="w-full bg-gray-950 border border-gray-800 rounded-md px-3 py-2"
          />
        </div>

        <div>
          <label className="block text-sm text-gray-400 mb-1">
            Total
          </label>
          <input
            name="total"
            type="number"
            value={form.total}
            onChange={handleChange}
            disabled={!isReview}
            className="w-full bg-gray-950 border border-gray-800 rounded-md px-3 py-2"
          />
        </div>

        <div>
          <label className="block text-sm text-gray-400 mb-1">
            Tax
          </label>
          <input
            name="tax"
            type="number"
            value={form.tax}
            onChange={handleChange}
            disabled={!isReview}
            className="w-full bg-gray-950 border border-gray-800 rounded-md px-3 py-2"
          />
        </div>

        <div className="flex justify-between items-center pt-4 border-t border-gray-800">
          <div className="text-sm text-gray-400">
            Confidence: {(invoice.confidence * 100).toFixed(1)}%
          </div>

          {isReview && (
            <div className="space-x-3">
              <button
                onClick={handleSave}
                disabled={saving}
                className="px-4 py-2 bg-blue-500/10 text-blue-400 rounded-md hover:bg-blue-500/20"
              >
                {saving ? "Saving..." : "Save"}
              </button>

              <button
                onClick={handleApprove}
                disabled={approving}
                className="px-4 py-2 bg-green-500/10 text-green-400 rounded-md hover:bg-green-500/20"
              >
                {approving ? "Approving..." : "Approve"}
              </button>
            </div>
          )}
        </div>

        {invoice.error_message && (
          <div className="text-red-400 text-sm pt-4 border-t border-gray-800">
            Error: {invoice.error_message}
          </div>
        )}

      </div>
    </div>
  );
}
