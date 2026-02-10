export default function StatsCards({ stats }) {
  if (!stats) return null;

  const cards = [
    { label: "Total", value: stats.total },
    { label: "Approved", value: stats.approved },
    { label: "Review", value: stats.review },
    { label: "Synced", value: stats.synced },
    { label: "Failed", value: stats.failed },
  ];

  return (
    <div className="grid grid-cols-5 gap-6">
      {cards.map((card) => (
        <div
          key={card.label}
          className="bg-gray-900 border border-gray-800 p-5 rounded-xl"
        >
          <p className="text-gray-400 text-sm">{card.label}</p>
          <p className="text-2xl font-semibold mt-2">
            {card.value || 0}
          </p>
        </div>
      ))}
    </div>
  );
}
