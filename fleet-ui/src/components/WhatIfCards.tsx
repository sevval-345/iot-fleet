export default function WhatIfCards({ top3 }: { top3: any }) {
  if (!top3) return null
  return (
    <div className="grid sm:grid-cols-3 gap-3">
      <Card title="Mevcut" body={
        <>
          <div className="text-2xl font-semibold">{top3.current_total.toFixed(2)} ₺</div>
          <div className="text-xs opacity-70">Aylık tahmini maliyet</div>
        </>
      }/>
      {top3.options?.slice(0,2).map((opt:any) => (
        <Card key={opt.plan_id} title={opt.label} body={
          <>
            <div className="text-2xl font-semibold">{opt.total.toFixed(2)} ₺</div>
            <div className="text-xs opacity-70">Tasarruf: {opt.saving.toFixed(2)} ₺</div>
          </>
        }/>
      ))}
    </div>
  )
}

function Card({ title, body }:{ title:string; body:React.ReactNode }) {
  return (
    <div className="p-3 rounded-2xl border dark:border-gray-800">
      <div className="font-medium mb-1">{title}</div>
      {body}
    </div>
  )
}
