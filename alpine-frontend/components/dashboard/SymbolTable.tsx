'use client'

import { useState } from 'react'
import { TrendingUp, TrendingDown, Minus, ArrowUpDown } from 'lucide-react'

interface SymbolData {
  symbol: string
  currentPrice: number
  change24h: number
  change24hPct: number
  winRate?: number
  totalTrades?: number
  avgReturn?: number
}

interface SymbolTableProps {
  symbols: SymbolData[]
  onSymbolClick?: (symbol: string) => void
  className?: string
}

type SortField = 'symbol' | 'price' | 'change' | 'winRate' | 'trades'
type SortDirection = 'asc' | 'desc'

/**
 * SymbolTable component displaying all symbols with performance stats
 * Supports sorting and filtering
 */
export default function SymbolTable({ symbols, onSymbolClick, className = '' }: SymbolTableProps) {
  const [sortField, setSortField] = useState<SortField>('symbol')
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc')
  const [searchQuery, setSearchQuery] = useState('')

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('asc')
    }
  }

  const sortedSymbols = [...symbols]
    .filter(s => s.symbol.toLowerCase().includes(searchQuery.toLowerCase()))
    .sort((a, b) => {
      let aVal: any = a[sortField]
      let bVal: any = b[sortField]

      if (sortField === 'symbol') {
        aVal = aVal.toLowerCase()
        bVal = bVal.toLowerCase()
      }

      if (aVal === undefined || aVal === null) return 1
      if (bVal === undefined || bVal === null) return -1

      const comparison = aVal > bVal ? 1 : aVal < bVal ? -1 : 0
      return sortDirection === 'asc' ? comparison : -comparison
    })

  const formatPrice = (price: number) => `$${price.toFixed(2)}`
  const formatPercent = (value: number) => `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`

  return (
    <div className={`bg-alpine-card border border-alpine-border rounded-lg overflow-hidden ${className}`}>
      {/* Search */}
      <div className="p-4 border-b border-alpine-border">
        <input
          type="text"
          placeholder="Search symbols..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-4 py-2 bg-alpine-bg border border-alpine-border rounded-lg text-alpine-text placeholder-alpine-text-dim focus:outline-none focus:border-alpine-accent"
        />
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-alpine-bg border-b border-alpine-border">
            <tr>
              <th
                className="px-4 py-3 text-left text-xs font-semibold text-alpine-text-dim uppercase cursor-pointer hover:text-alpine-text transition-colors"
                onClick={() => handleSort('symbol')}
              >
                <div className="flex items-center gap-2">
                  Symbol
                  <ArrowUpDown className="w-3 h-3" />
                </div>
              </th>
              <th
                className="px-4 py-3 text-right text-xs font-semibold text-alpine-text-dim uppercase cursor-pointer hover:text-alpine-text transition-colors"
                onClick={() => handleSort('price')}
              >
                <div className="flex items-center justify-end gap-2">
                  Price
                  <ArrowUpDown className="w-3 h-3" />
                </div>
              </th>
              <th
                className="px-4 py-3 text-right text-xs font-semibold text-alpine-text-dim uppercase cursor-pointer hover:text-alpine-text transition-colors"
                onClick={() => handleSort('change')}
              >
                <div className="flex items-center justify-end gap-2">
                  24h Change
                  <ArrowUpDown className="w-3 h-3" />
                </div>
              </th>
              <th
                className="px-4 py-3 text-right text-xs font-semibold text-alpine-text-dim uppercase cursor-pointer hover:text-alpine-text transition-colors"
                onClick={() => handleSort('winRate')}
              >
                <div className="flex items-center justify-end gap-2">
                  Win Rate
                  <ArrowUpDown className="w-3 h-3" />
                </div>
              </th>
              <th
                className="px-4 py-3 text-right text-xs font-semibold text-alpine-text-dim uppercase cursor-pointer hover:text-alpine-text transition-colors"
                onClick={() => handleSort('trades')}
              >
                <div className="flex items-center justify-end gap-2">
                  Trades
                  <ArrowUpDown className="w-3 h-3" />
                </div>
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-alpine-text-dim uppercase">
                Avg Return
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-alpine-border">
            {sortedSymbols.map((symbol) => (
              <tr
                key={symbol.symbol}
                className="hover:bg-alpine-bg/50 cursor-pointer transition-colors"
                onClick={() => onSymbolClick?.(symbol.symbol)}
              >
                <td className="px-4 py-3">
                  <div className="font-semibold text-alpine-text">{symbol.symbol}</div>
                </td>
                <td className="px-4 py-3 text-right text-alpine-text font-semibold">
                  {formatPrice(symbol.currentPrice)}
                </td>
                <td className="px-4 py-3 text-right">
                  <div className={`flex items-center justify-end gap-1 ${
                    symbol.change24h >= 0 ? 'text-alpine-accent' : 'text-alpine-red'
                  }`}>
                    {symbol.change24h >= 0 ? (
                      <TrendingUp className="w-4 h-4" />
                    ) : (
                      <TrendingDown className="w-4 h-4" />
                    )}
                    <span className="font-semibold">{formatPercent(symbol.change24hPct)}</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-right">
                  {symbol.winRate !== undefined ? (
                    <span className="text-alpine-text">{symbol.winRate.toFixed(1)}%</span>
                  ) : (
                    <span className="text-alpine-text-dim">-</span>
                  )}
                </td>
                <td className="px-4 py-3 text-right text-alpine-text">
                  {symbol.totalTrades ?? '-'}
                </td>
                <td className="px-4 py-3 text-right">
                  {symbol.avgReturn !== undefined ? (
                    <span className={`font-semibold ${
                      symbol.avgReturn >= 0 ? 'text-alpine-accent' : 'text-alpine-red'
                    }`}>
                      {formatPercent(symbol.avgReturn)}
                    </span>
                  ) : (
                    <span className="text-alpine-text-dim">-</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {sortedSymbols.length === 0 && (
        <div className="p-8 text-center text-alpine-text-dim">
          No symbols found
        </div>
      )}
    </div>
  )
}

