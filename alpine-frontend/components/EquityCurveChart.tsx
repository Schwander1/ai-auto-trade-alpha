'use client'

import { useEffect, useRef, useMemo } from 'react'
import { motion, useInView } from 'framer-motion'
import { createChart, IChartApi } from 'lightweight-charts'

export default function EquityCurveChart() {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const viewportOptions = useMemo(() => ({ once: true, amount: 0.3 }), [])
  const isInView = useInView(chartContainerRef, viewportOptions)

  useEffect(() => {
    if (!chartContainerRef.current || !isInView || chartRef.current) return

    const container = chartContainerRef.current
    if (!container || container.clientWidth === 0) return

    try {
      const chart = createChart(container, {
        width: container.clientWidth,
        height: 500,
        layout: {
          background: { color: '#12121a' },
          textColor: '#e4e4e7',
        },
        grid: {
          vertLines: { color: '#1e1e2e' },
          horzLines: { color: '#1e1e2e' },
        },
        rightPriceScale: {
          borderColor: '#1e1e2e',
        },
        timeScale: {
          borderColor: '#1e1e2e',
        },
      })

      if (!chart) {
        console.error('Chart creation failed')
        return
      }

      const alpineSeries = (chart as any).addLineSeries({
        color: '#4bffb5',
        lineWidth: 3,
        title: 'Alpine',
      })

      const spySeries = (chart as any).addLineSeries({
        color: '#2962ff',
        lineWidth: 2,
        lineStyle: 2,
        title: 'SPY',
      })

      // Sample data - 20 years
      const alpineData = [
        { time: '2006-01-03' as any, value: 10000 },
        { time: '2007-01-01' as any, value: 10800 },
        { time: '2008-01-01' as any, value: 11200 },
        { time: '2009-01-01' as any, value: 11200 },
        { time: '2010-01-01' as any, value: 12800 },
        { time: '2012-01-01' as any, value: 16500 },
        { time: '2015-01-01' as any, value: 24000 },
        { time: '2017-01-01' as any, value: 32000 },
        { time: '2020-01-01' as any, value: 42000 },
        { time: '2020-03-01' as any, value: 32000 },
        { time: '2021-01-01' as any, value: 48000 },
        { time: '2022-01-01' as any, value: 52000 },
        { time: '2023-01-01' as any, value: 58000 },
        { time: '2024-01-01' as any, value: 62000 },
        { time: '2025-11-10' as any, value: 66550 },
      ]

      const spyData = [
        { time: '2006-01-03' as any, value: 10000 },
        { time: '2007-01-01' as any, value: 11500 },
        { time: '2008-01-01' as any, value: 10500 },
        { time: '2009-01-01' as any, value: 4800 },
        { time: '2010-01-01' as any, value: 6500 },
        { time: '2012-01-01' as any, value: 8500 },
        { time: '2015-01-01' as any, value: 18000 },
        { time: '2017-01-01' as any, value: 22000 },
        { time: '2020-01-01' as any, value: 28000 },
        { time: '2020-03-01' as any, value: 24000 },
        { time: '2021-01-01' as any, value: 35000 },
        { time: '2022-01-01' as any, value: 38000 },
        { time: '2023-01-01' as any, value: 42000 },
        { time: '2024-01-01' as any, value: 46000 },
        { time: '2025-11-10' as any, value: 50000 },
      ]

      // Animate data loading (100ms per point)
      let i = 0
      const interval = setInterval(() => {
        if (i < alpineData.length) {
          alpineSeries.setData(alpineData.slice(0, i + 1))
          spySeries.setData(spyData.slice(0, i + 1))
          i++
        } else {
          clearInterval(interval)
        }
      }, 100)

      chartRef.current = chart

      const handleResize = () => {
        if (chartContainerRef.current && chart) {
          chart.applyOptions({
            width: chartContainerRef.current.clientWidth,
          })
        }
      }

      window.addEventListener('resize', handleResize)

      return () => {
        clearInterval(interval)
        window.removeEventListener('resize', handleResize)
        if (chart) {
          chart.remove()
          chartRef.current = null
        }
      }
    } catch (error) {
      console.error('Error creating chart:', error)
    }
  }, [isInView])

  return (
    <section className="py-24 bg-alpine-black-primary">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={viewportOptions}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
                  <h2 className="font-display text-4xl tracking-[0.15em] tracking-[0.15em] md:text-6xl font-black text-white mb-4">
                    20 Years of{' '}
                    <span className="bg-gradient-to-r from-alpine-neon-cyan to-alpine-neon-pink-bg-cliptex-ttext-transparent">
                      Backtested Performance
                    </span>
                  </h2>
                  <p className="text-xl text-alpine-text-secondary">
                    Alpine vs SPY - Historical simulation using real market data
                    <br />
                    <strong className="text-alpine-neon-cyan">Live verified tracking begins Wednesday, November 12, 2025 at 9:00 AM ET</strong>
                  </p>
        </motion.div>

        <div
          ref={chartContainerRef}
          className="w-full h-[500px] rounded-lg border border-alpine-black-border"
        />
      </div>
    </section>
  )
}

