import type { RiskBadge } from '../types'  // ← type-only

export default function RiskTag({ badge }: { badge: RiskBadge }) {
  const color =
    badge === 'green'
      ? 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300'
      : badge === 'orange'
      ? 'bg-orange-100 text-orange-800 dark:bg-orange-900/40 dark:text-orange-300'
      : 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300'
  return <span className={`text-xs px-2 py-1 rounded ${color}`}>{badge}</span>
}