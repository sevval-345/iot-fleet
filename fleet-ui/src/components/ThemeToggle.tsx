import { useEffect, useState } from 'react'

export default function ThemeToggle() {
  const [dark, setDark] = useState(() => localStorage.getItem('theme') === 'dark')
  useEffect(() => {
    const el = document.documentElement
    if (dark) { el.classList.add('dark'); localStorage.setItem('theme','dark') }
    else { el.classList.remove('dark'); localStorage.setItem('theme','light') }
  }, [dark])
  return (
    <button
      aria-label="Tema değiştir"
      onClick={() => setDark(v=>!v)}
      className="px-3 py-2 rounded-xl border dark:border-gray-700 shadow-sm"
    >
      {dark ? '🌙 Koyu' : '☀️ Açık'}
    </button>
  )
}
