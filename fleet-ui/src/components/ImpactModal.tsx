import type { ImpactResponse } from '../types'

export default function ImpactModal({
  open, onClose, data
}: { open: boolean; onClose: () => void; data: ImpactResponse | null }) {
  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />
      <div className="relative w-full max-w-2xl rounded-2xl border dark:border-gray-800 bg-white dark:bg-gray-900 p-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-semibold">Etkisini Hesapla</h3>
          <button onClick={onClose} className="px-2 py-1 rounded border dark:border-gray-700">Kapat</button>
        </div>

        {!data && <div>Yükleniyor…</div>}
        {data && (
          <div className="space-y-3">
            <div className="text-sm">
              <div>Aksiyon: <b>{data.action}</b></div>
              <div>Toplam 24s baz: <b>{data.total_baseline_mb_24h.toFixed(2)} MB</b></div>
              <div>Toplam 24s beklenen: <b>{data.total_expected_mb_24h.toFixed(2)} MB</b></div>
              <div>Toplam değişim: <b>{data.delta_pct.toFixed(1)}%</b></div>
            </div>

            <div className="overflow-auto rounded-xl border dark:border-gray-800">
              <table className="min-w-full text-sm">
                <thead className="bg-gray-50 dark:bg-gray-900">
                  <tr className="text-left">
                    <th className="p-2">SIM</th>
                    <th className="p-2">Baz (MB)</th>
                    <th className="p-2">Beklenen (MB)</th>
                    <th className="p-2">Δ%</th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map((it) => (
                    <tr key={it.sim_id} className="border-t dark:border-gray-800">
                      <td className="p-2 font-mono">{it.sim_id}</td>
                      <td className="p-2">{it.baseline_mb_24h.toFixed(2)}</td>
                      <td className="p-2">{it.expected_mb_24h.toFixed(2)}</td>
                      <td className="p-2">{it.delta_pct.toFixed(1)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

          </div>
        )}
      </div>
    </div>
  )
}
