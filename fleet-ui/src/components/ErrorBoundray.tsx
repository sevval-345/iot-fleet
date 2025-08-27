// src/components/ErrorBoundary.tsx
import React from 'react'

type State = { hasError: boolean; error?: any }

export default class ErrorBoundary extends React.Component<{children: React.ReactNode}, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError(error: any) {
    return { hasError: true, error }
  }

  componentDidCatch(error: any, info: any) {
    console.error('ErrorBoundary', error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-4 text-red-300">
          <h2 className="text-lg font-semibold">UI hata verdi</h2>
          <pre className="mt-2 whitespace-pre-wrap text-sm">
            {String(this.state.error?.message || this.state.error || 'Bilinmeyen hata')}
          </pre>
        </div>
      )
    }
    return this.props.children
  }
}
