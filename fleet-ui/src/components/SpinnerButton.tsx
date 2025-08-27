import React from "react"

type Props = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  loading?: boolean
}

export default function SpinnerButton({ loading, children, className = "", disabled, ...rest }: Props) {
  return (
    <button
      {...rest}
      disabled={disabled || loading}
      className={
        "inline-flex items-center gap-2 rounded-xl px-3 py-2 disabled:opacity-50 " +
        className
      }
    >
      {loading && (
        <span
          aria-hidden
          className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-r-transparent"
        />
      )}
      <span>{children}</span>
    </button>
  )
}
