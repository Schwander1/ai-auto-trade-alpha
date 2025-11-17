import * as React from 'react'
import { Slot } from '@radix-ui/react-slot'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const buttonVariants = cva(
  'inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-semibold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-alpine-neon-cyanfocusvisibl-e:ring-offset-2 focus-visible:ring-offset-alpine-blackprimarydisable-d:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-gradient-to-r from-alpine-neon-cyan to-alpine-neon-pink-textblac-khover:scale-105 shadow-glow-cyan',
        outline: 'border-2 border-alpine-neon-cyantext-alpine-neoncyanhove-r:bg-alpine-neoncya-n/10 hover:shadow-glow-cyan',
        ghost: 'hover:bg-alpine-neoncya-n/10 text-alpine-text-primary',
        secondary: 'bg-alpine-black-secondary text-alpine-text-primary hover:bg-alpine-black-secondary/80',
      },
      size: {
        default: 'h-11 px-6',
        sm: 'h-9 px-4',
        lg: 'h-14 px-8 text-base',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button'
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = 'Button'

export { Button, buttonVariants }

