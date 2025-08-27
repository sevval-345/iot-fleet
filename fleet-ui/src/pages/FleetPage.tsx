// src/pages/FleetPage.tsx
import { useEffect, useMemo, useState } from 'react'
import FleetTable from '../components/FleetTable'
import BulkActionPanel from '../components/BulkActionPanel'
import { fetchFleet } from '../api'
import type { FleetItem } from '../types'

export default function FleetPage() {
  const [selected, setSelected] = useState<string[]>([])
  const [ids, setIds] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    let alive = true
    ;(async () => {
      try {
        setLoading(true); setError('')
        const raw = await fetchFleet({ limit: 200, offset: 0 })
        if (!alive) return
        let arr: FleetItem[] = Array.isArray(raw) ? raw : []
        // Safe mode: backend boşsa örnek ID listesi
        if (!arr.length) {
          arr = [
            { sim_id: '2001' } as FleetItem,
            { sim_id: '2002' } as FleetItem,
            { sim_id: '2003' } as FleetItem,
            { sim_id: '2004' } as FleetItem,
            { sim_id: '2005' } as FleetItem,
          ]
        }
        const uniq = Array.from(new Set(arr.map(r => String(r.sim_id || '')))).filter(Boolean)
        // sayısal sıralama (string fallback)
        uniq.sort((a, b) => (Number(a) || 0) - (Number(b) || 0) || a.localeCompare(b))
        setIds(uniq)
      } catch (e: any) {
        if (!alive) return
        console.error('fetchFleet(ids) failed:', e)
        setError(e?.message || 'Filo listesi alınamadı')
        setIds([])
      } finally {
        if (alive) setLoading(false)
      }
    })()
    return () => { alive = false }
  }, [])

  const allChecked = useMemo(
    () => ids.length > 0 && selected.length === ids.length,
    [ids, selected]
  )

  function toggle(id: string) {
    setSelected(prev => (prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]))
  }
  function toggleAll(on: boolean) {
    setSelected(on ? ids : [])
  }
  function clearSelection() {
    setSelected([])
  }

  return (
    <div className="space-y-4">
      <BulkActionPanel selected={selected} />

      <div className="rounded-2xl border dark:border-gray-800 p-3">
        <div className="flex items-center justify-between mb-2">
          <div className="text-sm">Toplu seçim</div>
          <div className="text-xs opacity-70">Seçili: {selected.length}</div>
        </div>

        {loading && <div className="text-sm opacity-70">Yükleniyor…</div>}
        {error && (
          <div className="text-sm rounded px-2 py-1 bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300">
            {error}
          </div>
        )}

        <div className="flex flex-wrap gap-3 items-center mt-1">
          <label className="inline-flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={allChecked}
              onChange={e => toggleAll(e.target.checked)}
              aria-label="Hepsini seç"
              disabled={ids.length === 0}
            />
            <span>Hepsi</span>
          </label>

          {selected.length > 0 && (
            <button
              type="button"
              onClick={clearSelection}
              className="text-xs px-2 py-1 rounded border dark:border-gray-700"
              aria-label="Seçimi temizle"
            >
              Temizle
            </button>
          )}

          {ids.length === 0 && !loading && !error && (
            <span className="text-sm opacity-70">Gösterilecek SIM bulunamadı</span>
          )}

          {ids.map(id => (
            <label key={id} className="inline-flex items-center gap-2 text-sm">
              <input
                aria-label={`Seç ${id}`}
                type="checkbox"
                checked={selected.includes(id)}
                onChange={() => toggle(id)}
              />
              <span className="font-mono">{id}</span>
            </label>
          ))}
        </div>
      </div>

      <FleetTable />
    </div>
  )
}
