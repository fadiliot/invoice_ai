export default function Filters({ query, setQuery }) {
  return (
    <div className="flex gap-4">
      <input
        className="bg-gray-950 border border-gray-800 rounded-lg px-4 py-2"
        placeholder="Search vendor..."
        onChange={(e) =>
          setQuery({ ...query, search: e.target.value, page: 1 })
        }
      />

      <select
        className="bg-gray-950 border border-gray-800 rounded-lg px-4 py-2"
        value={query.stage}
        onChange={(e) =>
          setQuery({ ...query, stage: e.target.value, page: 1 })  // ✅ fixed
        }
      >
        <option value="">All</option>
        <option value="PENDING">Pending</option>
        <option value="PROCESSING">Processing</option>
        <option value="REVIEW">Review</option>
        <option value="QB_SYNCED">Approved</option>
        <option value="FAILED">Failed</option>
      </select>
    </div>
  );
}
