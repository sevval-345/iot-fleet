import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts'

function makeClientFallback(days = 30) {
  const out: { ts: string; mb: number; roam: number }[] = []
  const today = new Date()
  let base = 20 + Math.random() * 20
  for (let i = days; i >= 1; i--) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    const jitter = (Math.random() - 0.5) * base * 0.4
    const mb = Math.max(0, base + jitter)
    const roam = Math.max(0, mb * 0.05 + (Math.random() - 0.5) * 2)
    out.push({ ts: d.toISOString().slice(0, 10), mb: +mb.toFixed(2), roam: +roam.toFixed(2) })
  }
  return out
}

export default function UsageChart({ data }: { data: { ts: string; mb_used: number; roaming_mb: number }[] }) {
  const hasData = Array.isArray(data) && data.length > 0
  const chart = hasData
    ? data.map(d => ({ ts: d.ts.slice(0, 10), mb: d.mb_used, roam: d.roaming_mb }))
    : makeClientFallback(30)

  return (
    <div className="p-3 rounded-2xl border dark:border-gray-800">
      <div className="mb-2 font-medium">
        Son 30 gün kullanım{' '}
        {!hasData && <span className="opacity-60">(demo verisi)</span>}
      </div>
      <div style={{ width: '100%', height: 260 }}>
        <ResponsiveContainer>
          <LineChart data={chart}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="ts" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="mb" dot={false} />
            <Line type="monotone" dataKey="roam" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="text-xs opacity-60 mt-1">nokta sayısı: {chart.length}</div>
    </div>
  )
}
