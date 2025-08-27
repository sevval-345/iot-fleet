// src/pages/SimDetail.tsx
import { useEffect, useMemo, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { fetchAnomalies, fetchUsage, fetchWhatIfTop3 } from '../api'
import type { Anomaly, UsagePoint, WhatIfTop3 } from '../types'
import {
  LineChart, Line, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid
} from 'recharts'

const Badge = ({ label, title }: { label: string; title: string }) => (
  <span title={title} className="text-xs px-2 py-1 rounded bg-gray-100 dark:bg-white/10">
    {label}
  </span>
)

export default function SimDetail() {
  const { simId = '' } = useParams()
  const [usage, setUsage] = useState<UsagePoint[]>([])
  const [anoms, setAnoms] = useState<Anomaly[]>([])
  const [whatif, setWhatif] = useState<WhatIfTop3 | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!simId) return
    let alive = true
    ;(async () => {
      try {
        setLoading(true); setError('')
        const [u, a, w] = await Promise.all([
          fetchUsage(simId, 30, 'day'),
          fetchAnomalies(simId),
          fetchWhatIfTop3(simId),
        ])
        if (!alive) return
        setUsage(Array.isArray(u) ? u : [])
        setAnoms(Array.isArray(a) ? a : [])
        setWhatif(w || null)
      } catch (e: any) {
        if (!alive) return
        setError(e?.message || 'Detaylar alınamadı')
      } finally {
        if (alive) setLoading(false)
      }
    })()
    return () => { alive = false }
  }, [simId])

  const data = useMemo(() =>
    (usage ?? []).map(u => ({
      ts: (u.ts || '').slice(0, 10),
      MB: Number(u.mb_used ?? 0),
      Roaming: Number(u.roaming_mb ?? 0),
    })), [usage])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">SIM {simId || '-'}</h2>
        <Link to="/" className="text-sm underline">← Listeye dön</Link>
      </div>

      {error && (
        <div className="p-2 rounded bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300">
          {error}
        </div>
      )}
      {loading && <div>Yükleniyor…</div>}

      {/* 30 Günlük Kullanım */}
      {!loading && (
        <section className="space-y-2">
          <h3 className="font-medium">
            30 Günlük Kullanım {data.length === 0 && <span className="opacity-60 text-sm">(veri yok)</span>}
          </h3>
          <div className="h-72 w-full rounded-2xl border dark:border-gray-800 p-3">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="ts" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Line type="monotone" dataKey="MB" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="Roaming" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </section>
      )}

      {/* Anomali Rozetleri */}
      {!loading && (
        <section className="space-y-2">
          <h3 className="font-medium">Anomali Rozetleri</h3>
          <div className="flex flex-wrap gap-2">
            {anoms.length === 0 && <span className="text-sm">Anomali yok</span>}
            {anoms.map((a, i) => (
              <Badge key={i} label={a.type} title={`${a.ts}: ${a.reason}`} />
            ))}
          </div>
        </section>
      )}

      {/* What-If Kartları (Top 3) */}
      {!loading && (
        <section className="space-y-2">
          <h3 className="font-medium">What-If Kartları (Top 3)</h3>
          <div className="grid md:grid-cols-3 gap-3">
            {whatif?.options?.map((opt, i) => (
              <div key={i} className="rounded-2xl border dark:border-gray-800 p-4">
                <div className="text-sm opacity-70">Seçenek</div>
                <div className="text-lg font-semibold">{opt.label}</div>
                <div className="mt-2 text-sm">
                  Toplam: <strong>{opt.total.toFixed(2)}</strong>
                </div>
                <div className={`mt-1 text-sm ${opt.saving > 0 ? 'text-green-600' : 'text-red-600'}`}>
                  Tasarruf: {opt.saving.toFixed(2)}
                </div>
              </div>
            ))}
            {!whatif && <div className="text-sm">Yükleniyor…</div>}
          </div>
        </section>
      )}
    </div>
  )
}
