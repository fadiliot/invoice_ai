export default function Pagination({ page, limit, total, setQuery }) {
  const totalPages = Math.ceil(total / limit) || 1;

  return (
    <div className="flex justify-between items-center">
      <span className="text-gray-400 text-sm">
        Page {page} of {totalPages}
      </span>

      <div className="space-x-2">
        <button
          disabled={page === 1}
          onClick={() =>
            setQuery((prev) => ({ ...prev, page: prev.page - 1 }))
          }
          className="px-3 py-1 bg-gray-800 rounded disabled:opacity-40"
        >
          Prev
        </button>

        <button
          disabled={page === totalPages}
          onClick={() =>
            setQuery((prev) => ({ ...prev, page: prev.page + 1 }))
          }
          className="px-3 py-1 bg-gray-800 rounded disabled:opacity-40"
        >
          Next
        </button>
      </div>
    </div>
  );
}
