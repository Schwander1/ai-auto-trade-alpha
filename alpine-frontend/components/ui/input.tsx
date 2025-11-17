import * as React from 'react'
import { cn } from '@/lib/utils'

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          'flex h-11 w-full rounded-lg border border-alpine-black-border bg-alpine-black-secondary px-4 py-2 text-sm text-alpine-text-primary placeholder:text-alpine-text-secondary focus:outline-none focus:ring-2 focus:ring-alpine-neon-cyan focus:ring-offset-2 focus:ring-offset-alpine-black-primary disabled:cursor-not-allowed disabled:opacity-50',
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = 'Input'

export { Input }

