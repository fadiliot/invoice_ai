import { retryInvoice } from "./api";

export default function RetryButton({ id, onSuccess }) {
  const handleRetry = async () => {
    try {
      await retryInvoice(id);
      onSuccess();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <button
      onClick={handleRetry}
      className="px-3 py-1 text-xs rounded-md 
                 bg-red-500/10 text-red-400 
                 hover:bg-red-500/20 transition"
    >
      Retry
    </button>
  );
}
