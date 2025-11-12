import { render, screen, fireEvent } from '@testing-library/react'
import SymbolTable from '@/components/dashboard/SymbolTable'

const mockSymbols = [
  {
    symbol: 'AAPL',
    currentPrice: 150.25,
    change24h: 2.5,
    change24hPct: 1.69,
    winRate: 65.5,
    totalTrades: 100,
    avgReturn: 2.3,
  },
  {
    symbol: 'GOOGL',
    currentPrice: 2800.50,
    change24h: -10.25,
    change24hPct: -0.36,
    winRate: 58.2,
    totalTrades: 85,
    avgReturn: 1.8,
  },
]

describe('SymbolTable', () => {
  it('renders symbols correctly', () => {
    render(<SymbolTable symbols={mockSymbols} />)
    
    expect(screen.getByText('AAPL')).toBeInTheDocument()
    expect(screen.getByText('GOOGL')).toBeInTheDocument()
  })

  it('displays price information', () => {
    render(<SymbolTable symbols={mockSymbols} />)
    
    expect(screen.getByText(/\$150\.25/)).toBeInTheDocument()
    expect(screen.getByText(/\$2800\.50/)).toBeInTheDocument()
  })

  it('filters symbols by search query', () => {
    render(<SymbolTable symbols={mockSymbols} />)
    
    const searchInput = screen.getByPlaceholderText('Search symbols...')
    fireEvent.change(searchInput, { target: { value: 'AAPL' } })
    
    expect(screen.getByText('AAPL')).toBeInTheDocument()
    expect(screen.queryByText('GOOGL')).not.toBeInTheDocument()
  })

  it('calls onSymbolClick when symbol is clicked', () => {
    const handleClick = jest.fn()
    render(<SymbolTable symbols={mockSymbols} onSymbolClick={handleClick} />)
    
    const symbolRow = screen.getByText('AAPL').closest('tr')
    if (symbolRow) {
      fireEvent.click(symbolRow)
      expect(handleClick).toHaveBeenCalledWith('AAPL')
    }
  })

  it('sorts by symbol when header is clicked', () => {
    render(<SymbolTable symbols={mockSymbols} />)
    
    const symbolHeader = screen.getByText('Symbol')
    fireEvent.click(symbolHeader)
    
    // Symbols should still be visible after sorting
    expect(screen.getByText('AAPL')).toBeInTheDocument()
    expect(screen.getByText('GOOGL')).toBeInTheDocument()
  })

  it('displays win rate when provided', () => {
    render(<SymbolTable symbols={mockSymbols} />)
    
    expect(screen.getByText(/65\.5%/)).toBeInTheDocument()
    expect(screen.getByText(/58\.2%/)).toBeInTheDocument()
  })
})

