import alpaca_trade_api as tradeapi
import os
from datetime import datetime

api = tradeapi.REST(
    os.getenv('APCA_API_KEY_ID'),
    os.getenv('APCA_API_SECRET_KEY'), 
    'https://paper-api.alpaca.markets'
)

# Get account info
account = api.get_account()
print(f'Portfolio Value: ${account.portfolio_value}')
print(f'Buying Power: ${account.buying_power}')
print(f'Total Equity: ${account.equity}')

# Get current positions
positions = api.list_positions()
print(f'\nCurrent Positions ({len(positions)}):')

if positions:
    total_market_value = 0
    total_unrealized_pnl = 0
    
    for pos in positions:
        market_value = float(pos.market_value) 
        unrealized_pnl = float(pos.market_value) - float(pos.cost_basis)
        total_market_value += market_value
        total_unrealized_pnl += unrealized_pnl
        
        print(f'{pos.symbol}: {pos.qty} shares')
        print(f'  Market Value: ${market_value:.2f}')
        print(f'  Cost Basis: ${float(pos.cost_basis):.2f}')
        print(f'  Unrealized P&L: ${unrealized_pnl:.2f}')
        print(f'  Current Price: ${float(pos.current_price):.2f}')
        print()
    
    print(f'Total Market Value: ${total_market_value:.2f}')
    print(f'Total Unrealized P&L: ${total_unrealized_pnl:.2f}')
else:
    print('No positions currently held')

print(f'\nPortfolio Summary for {datetime.now().strftime("%B %d, %Y")}:')
print(f'Account Status: Paper Trading (Virtual Money)')
print(f'Cash Available: ${float(account.cash):.2f}')
