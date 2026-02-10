import useInvoices from "./useinvoices";
import InvoiceTable from "./InvoiceTable";
import { useState } from "react";

export default function AllInvoicesPage() {
  const [query] = useState({
    page: 1,
    limit: 20,
    search: "",
    status: "",
    sort: "created_at",
    order: "desc",
  });

  const { data, total, loading } = useInvoices(query);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">All Invoices</h1>

      <InvoiceTable invoices={data} loading={loading} />

      <div className="text-sm text-gray-400">
        Total: {total}
      </div>
    </div>
  );
}
