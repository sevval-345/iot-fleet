import React, { createContext, useContext, useMemo, useState } from "react"

type ToastKind = "info" | "success" | "error"
type Toast = { id: number; kind: ToastKind; msg: string; ttl: number }

type Ctx = {
  show: (msg: string, kind?: ToastKind, ttlMs?: number) => void
}

const ToastCtx = createContext<Ctx | null>(null)

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [items, setItems] = useState<Toast[]>([])

  const show = (msg: string, kind: ToastKind = "info", ttlMs = 2500) => {
    const id = Date.now() + Math.random()
    setItems((s) => [...s, { id, kind, msg, ttl: ttlMs }])
    setTimeout(() => setItems((s) => s.filter((t) => t.id !== id)), ttlMs)
  }

  const value = useMemo(() => ({ show }), [])

  return (
    <ToastCtx.Provider value={value}>
      {children}
      {/* Viewport */}
      <div className="fixed z-50 bottom-4 right-4 space-y-2">
        {items.map((t) => (
          <div
            key={t.id}
            className={
              "rounded-xl px-3 py-2 text-sm shadow border " +
              (t.kind === "success"
                ? "bg-emerald-600 text-white border-emerald-700"
                : t.kind === "error"
                ? "bg-rose-600 text-white border-rose-700"
                : "bg-gray-800 text-white border-gray-700")
            }
            role="status"
          >
            {t.msg}
          </div>
        ))}
      </div>
    </ToastCtx.Provider>
  )
}

export function useToast() {
  const ctx = useContext(ToastCtx)
  if (!ctx) throw new Error("useToast must be used within <ToastProvider>")
  return ctx
}
