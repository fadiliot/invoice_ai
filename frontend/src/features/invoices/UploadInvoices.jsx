import { useState } from "react";
import { uploadInvoices } from "./api";

export default function UploadInvoices({ onUploadSuccess }) {
  const [uploading, setUploading] = useState(false);

  const handleUpload = async (e) => {
    const files = e.target.files;
    if (!files.length) return;

    setUploading(true);

    try {
      await uploadInvoices(files);
      if (onUploadSuccess) {
        onUploadSuccess();
      }
    } catch (err) {
      console.error("Upload failed:", err);
    } finally {
      setUploading(false);
    }
  };

  return (
    <label className="cursor-pointer px-4 py-2 bg-blue-500/10 text-blue-400 rounded-md hover:bg-blue-500/20 transition text-sm">
      {uploading ? "Uploading..." : "Upload Invoices"}
      <input
        type="file"
        multiple
        accept=".pdf,.png,.jpg,.jpeg"
        className="hidden"
        onChange={handleUpload}
      />
    </label>
  );
}
