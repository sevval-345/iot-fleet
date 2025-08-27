// src/components/FleetTable.tsx  (GEÇİCİ DEBUG SÜRÜMÜ)
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchFleet } from '../api'
import type { FleetItem } from '../types'

export default function FleetTable() {
  const [data, setData] = useState<FleetItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    let alive = true
    ;(async () => {
      setLoading(true); setError('')
      try {
        const rows = await fetchFleet({})  // filtre paramı YOK (sade)
        if (!alive) return
        console.log('[FleetTable] /api/fleet response:', rows)
        setData(Array.isArray(rows) ? rows : [])
      } catch (e: any) {
        console.error('[FleetTable] error:', e)
        if (alive) setError(e?.message || 'Liste alınamadı')
      } finally {
        if (alive) setLoading(false)
      }
    })()
    return () => { alive = false }
  }, [])

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Filo</h2>
        <div className="text-xs opacity-70">Kayıt: {data.length}</div>
      </div>

      {error && <div className="p-2 rounded bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300">{error}</div>}
      {loading && <div>Yükleniyor…</div>}

      <div className="overflow-auto rounded-2xl border dark:border-gray-800">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50 dark:bg-gray-900">
            <tr className="text-left">
              <th className="p-3">SIM</th>
              <th className="p-3">Risk</th>
              <th className="p-3">Son sinyal</th>
              <th className="p-3">Şehir</th>
              <th className="p-3">Plan</th>
              <th className="p-3">Durum</th>
              <th className="p-3">Roaming?</th>
            </tr>
          </thead>
          <tbody>
            {!loading && data.length === 0 && (
              <tr><td className="p-3" colSpan={7}>Kayıt yok (UI)</td></tr>
            )}
            {data.map((row) => (
              <tr key={row.sim_id} className="border-t dark:border-gray-800 hover:bg-gray-50/50 dark:hover:bg-white/5">
                <td className="p-3 font-mono">
                  <Link className="underline" to={`/sim/${row.sim_id}`}>{row.sim_id}</Link>
                </td>
                <td className="p-3">{row.risk_badge}</td>
                <td className="p-3">{row.last_seen_at ?? '-'}</td>
                <td className="p-3">{row.city ?? '-'}</td>
                <td className="p-3">{row.plan ?? '-'}</td>
                <td className="p-3">{row.status ?? '-'}</td>
                <td className="p-3">{row.has_roaming ? 'Evet' : 'Hayır'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Ham JSON'u hızlı teşhis için göster (geçici) */}
      <pre className="text-xs p-2 bg-gray-50 dark:bg-black/30 rounded-2xl overflow-auto">
        {/* <pre>{JSON.stringify(data, null, 2)}</pre> */}
      </pre>
    </div>
  )
}
