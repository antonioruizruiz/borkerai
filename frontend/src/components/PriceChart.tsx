import { CandlestickSeries, LineSeries, createChart } from 'lightweight-charts'
import { useEffect, useRef } from 'react'

import type { PriceBar } from '@/lib/api'

function sma(bars: PriceBar[], periodo: number) {
  return bars.map((bar, i) => {
    if (i < periodo - 1) return { time: bar.date }
    const ventana = bars.slice(i - periodo + 1, i + 1)
    const media = ventana.reduce((acc, b) => acc + b.close, 0) / periodo
    return { time: bar.date, value: media }
  })
}

export function PriceChart({ bars }: { bars: PriceBar[] }) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const container = containerRef.current
    if (!container || bars.length === 0) return

    const chart = createChart(container, {
      width: container.clientWidth,
      height: 360,
      layout: {
        background: { color: 'transparent' },
        textColor: '#64748b',
      },
      grid: {
        vertLines: { color: '#e2e4e9' },
        horzLines: { color: '#e2e4e9' },
      },
      timeScale: { borderColor: '#e2e4e9' },
      rightPriceScale: { borderColor: '#e2e4e9' },
    })

    const velas = chart.addSeries(CandlestickSeries, {
      upColor: '#15803d',
      downColor: '#b91c1c',
      borderVisible: false,
      wickUpColor: '#15803d',
      wickDownColor: '#b91c1c',
    })
    velas.setData(bars.map((b) => ({ time: b.date, open: b.open, high: b.high, low: b.low, close: b.close })))

    if (bars.length >= 50) {
      const sma50 = chart.addSeries(LineSeries, { color: '#4338ca', lineWidth: 1, title: 'Media 50' })
      sma50.setData(sma(bars, 50).filter((p) => 'value' in p) as { time: string; value: number }[])
    }

    if (bars.length >= 200) {
      const sma200 = chart.addSeries(LineSeries, { color: '#c026d3', lineWidth: 1, title: 'Media 200' })
      sma200.setData(sma(bars, 200).filter((p) => 'value' in p) as { time: string; value: number }[])
    }

    chart.timeScale().fitContent()

    const onResize = () => chart.applyOptions({ width: container.clientWidth })
    window.addEventListener('resize', onResize)

    return () => {
      window.removeEventListener('resize', onResize)
      chart.remove()
    }
  }, [bars])

  return <div ref={containerRef} />
}
