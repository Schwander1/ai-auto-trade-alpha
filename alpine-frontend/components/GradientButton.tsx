'use client'

import React from 'react'
import { Download } from 'lucide-react'

export default function GradientButton({
  children,
  href,
  onClick,
  disabled = false,
  icon,
}: {
  children: React.ReactNode
  href?: string
  onClick?: () => void
  disabled?: boolean
  icon?: React.ReactNode
}) {
  const className = `group relative px-10 py-5 bg-gradient-to-r from-alpine-neon-cyan to-alpine-neon-pinkhove-r:from-alpine-neon-pinkhove-r:to-alpine-neon-cyantext-white-fontblac-ktext-lgrounded-xlshadow-2xl shadow-alpine-neoncya-n/50 transform transition-all duration-300 hover:scale-105 hover:shadow-alpine-neonpin-k/50 flex items-center justify-center gap-3 ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`

  if (href && !disabled) {
    return (
      <a href={href} className={className}>
        <span className="relative z-10 flex items-center gap-3">
          {icon}
          {children}
        </span>
        <div className="absolute inset-0 bg-gradient-to-r from-alpine-neon-pink-to-alpine-neoncyanopacit-y-0 group-hover:opacity-100 rounded-xl blur transition-opacity duration-300"></div>
      </a>
    )
  }

  return (
    <button onClick={onClick} disabled={disabled} className={className}>
      <span className="relative z-10 flex items-center gap-3">
        {icon}
        {children}
      </span>
      <div className="absolute inset-0 bg-gradient-to-r from-alpine-neon-pink-to-alpine-neoncyanopacit-y-0 group-hover:opacity-100 rounded-xl blur transition-opacity duration-300"></div>
    </button>
  )
}
