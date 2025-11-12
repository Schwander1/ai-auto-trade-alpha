'use client'

import { useEffect, useRef, useState, useMemo } from 'react'

export function useIntersectionObserver(options?: IntersectionObserverInit) {
  const [isIntersecting, setIsIntersecting] = useState(false)
  const [hasIntersected, setHasIntersected] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  // Memoize options to prevent infinite loops when object is passed
  const stableOptions = useMemo(() => {
    return {
      threshold: options?.threshold ?? 0.1,
      rootMargin: options?.rootMargin ?? '50px',
      root: options?.root,
    }
  }, [options?.threshold, options?.rootMargin, options?.root])

  useEffect(() => {
    const element = ref.current
    if (!element) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsIntersecting(true)
          setHasIntersected(true)
        } else {
          setIsIntersecting(false)
        }
      },
      stableOptions
    )

    observer.observe(element)

    return () => {
      observer.disconnect()
    }
  }, [stableOptions])

  return { ref, isIntersecting, hasIntersected }
}

