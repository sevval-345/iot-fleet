const colors: Record<string,string> = {
  spike: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
  drain: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300',
  inactivity: 'bg-gray-200 text-gray-800 dark:bg-gray-700/50 dark:text-gray-200',
  roaming: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
}

export default function AnomalyBadges({ items }:{ items: {type:string; ts:string; reason:string}[] }) {
  if (!items?.length) return <div className="text-sm opacity-70">Anomali yok</div>
  return (
    <div className="flex flex-wrap gap-2">
      {items.map((a,i) => (
        <span key={i} className={`text-xs px-2 py-1 rounded ${colors[a.type] || 'bg-gray-100 dark:bg-gray-800'}`}>
          {a.type} — {a.ts}
        </span>
      ))}
    </div>
  )
}
