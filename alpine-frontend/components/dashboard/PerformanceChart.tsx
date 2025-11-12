'use client'

import { useEffect, useRef, useState } from 'react'
import { TrendingUp, TrendingDown, BarChart3 } from 'lucide-react'

interface PerformanceChartProps {
  data: Array<{ date: string; equity: number; drawdown: number }>
  type?: 'equity' | 'winrate' | 'roi'
  className?: string
}

/**
 * PerformanceChart component for displaying equity curves, win rates, and ROI
 * Uses lightweight-charts for rendering
 */
export default function PerformanceChart({ data, type = 'equity', className = '' }: PerformanceChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const [chart, setChart] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (!chartContainerRef.current || data.length === 0) return

    const loadChart = async () => {
      try {
        const { createChart } = await import('lightweight-charts')
        
        if (chartContainerRef.current) {
          const chartInstance = createChart(chartContainerRef.current, {
            width: chartContainerRef.current.clientWidth,
            height: 300,
            layout: {
              background: { color: '#0f0f1a' },
              textColor: '#a1a1aa',
            },
            grid: {
              vertLines: { color: '#1a1a2e' },
              horzLines: { color: '#1a1a2e' },
            },
            timeScale: {
              timeVisible: true,
              secondsVisible: false,
            },
          })

          const lineSeries = chartInstance.addLineSeries({
            color: type === 'equity' ? '#00d9ff' : type === 'winrate' ? '#00ff88' : '#ff0080',
            lineWidth: 2,
            priceFormat: {
              type: 'price',
              precision: 2,
              minMove: 0.01,
            },
          })

          const chartData = data.map(point => ({
            time: new Date(point.date).getTime() / 1000 as any,
            value: type === 'equity' ? point.equity : type === 'winrate' ? point.drawdown : point.equity,
          }))

          lineSeries.setData(chartData)
          chartInstance.timeScale().fitContent()

          setChart(chartInstance)
          setIsLoading(false)

          // Handle resize
          const handleResize = () => {
            if (chartContainerRef.current) {
              chartInstance.applyOptions({ width: chartContainerRef.current.clientWidth })
            }
          }
          window.addEventListener('resize', handleResize)

          return () => {
            window.removeEventListener('resize', handleResize)
            chartInstance.remove()
          }
        }
      } catch (error) {
        console.error('Error loading chart:', error)
        setIsLoading(false)
      }
    }

    loadChart()

    return () => {
      if (chart) {
        chart.remove()
      }
    }
  }, [data, type])

  if (isLoading) {
    return (
      <div className={`bg-alpine-card border border-alpine-border rounded-lg p-6 ${className}`}>
        <div className="flex items-center justify-center h-[300px]">
          <BarChart3 className="w-8 h-8 text-alpine-text-dim animate-pulse" />
        </div>
      </div>
    )
  }

  const getTitle = () => {
    switch (type) {
      case 'equity': return 'Equity Curve'
      case 'winrate': return 'Win Rate'
      case 'roi': return 'ROI'
      default: return 'Performance'
    }
  }

  const getIcon = () => {
    switch (type) {
      case 'equity': return <TrendingUp className="w-5 h-5" />
      case 'winrate': return <BarChart3 className="w-5 h-5" />
      case 'roi': return <TrendingDown className="w-5 h-5" />
      default: return <BarChart3 className="w-5 h-5" />
    }
  }

  return (
    <div className={`bg-alpine-card border border-alpine-border rounded-lg p-6 ${className}`}>
      <div className="flex items-center gap-2 mb-4">
        {getIcon()}
        <h3 className="text-lg font-bold text-alpine-text">{getTitle()}</h3>
      </div>
      <div ref={chartContainerRef} className="w-full h-[300px]" />
    </div>
  )
}

