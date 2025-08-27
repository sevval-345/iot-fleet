import { useState } from 'react'
import { postAction, postImpact } from '../api'
import ImpactModal from './ImpactModal'
import SpinnerButton from './SpinnerButton'
import type { Action, ImpactResponse } from '../types'
import { useToast } from '../hooks/useToast'

const ACTIONS: Action[] = ['freeze_24h','throttle','notify']

export default function BulkActionPanel({ selected }: { selected: string[] }) {
  const toast = useToast()
  const [action, setAction] = useState<Action>('freeze_24h')
  const [reason, setReason] = useState('')
  const [loadingApply, setLoadingApply] = useState(false)
  const [loadingImpact, setLoadingImpact] = useState(false)

  // impact modal
  const [open, setOpen] = useState(false)
  const [impact, setImpact] = useState<ImpactResponse | null>(null)

  const disabled = selected.length === 0

  async function onApply() {
    if (disabled) return
    try {
      setLoadingApply(true)
      const res = await postAction(selected, action, reason.trim())
      toast.show(`Uygulandı ✔  Etkilenen SIM: ${res.applied_to}`, "success")
    } catch (e: any) {
      toast.show(e?.message || "İşlem başarısız", "error")
    } finally {
      setLoadingApply(false)
    }
  }

  async function onImpact() {
    if (disabled) return
    try {
      setLoadingImpact(true)
      setImpact(null); setOpen(true)
      const res = await postImpact(selected, action, 65)
      setImpact(res)
    } catch (e: any) {
      setOpen(false)
      toast.show(e?.message || "Hesaplama başarısız", "error")
    } finally {
      setLoadingImpact(false)
    }
  }

  return (
    <div className="rounded-2xl border dark:border-gray-800 p-3 space-y-2">
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-sm">Seçili: <b>{selected.length}</b></span>
        <select
          className="px-3 py-2 rounded-xl border dark:border-gray-700"
          value={action}
          onChange={e => setAction(e.target.value as Action)}
          aria-label="Aksiyon seç"
        >
          {ACTIONS.map(a => <option key={a} value={a}>{a}</option>)}
        </select>
        <input
          className="px-3 py-2 rounded-xl border dark:border-gray-700 w-64"
          placeholder="Neden (opsiyonel)"
          value={reason}
          onChange={e => setReason(e.target.value)}
        />

        <SpinnerButton
          onClick={onImpact}
          loading={loadingImpact}
          disabled={disabled}
          className="border dark:border-gray-700"
        >
          Etkisini Hesapla
        </SpinnerButton>

        <SpinnerButton
          onClick={onApply}
          loading={loadingApply}
          disabled={disabled}
          className="bg-blue-600 text-white"
        >
          Uygula
        </SpinnerButton>
      </div>

      <ImpactModal open={open} onClose={()=>setOpen(false)} data={impact} />
    </div>
  )
}
