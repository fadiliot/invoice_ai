import UploadInvoices from "../features/invoices/UploadInvoices";

export default function TopBar({ title, onUploadSuccess }) {
  return (
    <div className="flex justify-between items-center mb-8">
      <h1 className="text-2xl font-semibold">
        {title}
      </h1>

      <UploadInvoices onUploadSuccess={onUploadSuccess} />
    </div>
  );
}
