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
print(f'Daytrade Buying Power: ${account.daytrading_buying_power}')

# Calculate daily P&L from positions
positions = api.list_positions()
total_unrealized_pnl = sum(float(pos.unrealized_pl) for pos in positions)
print(f'Total Unrealized P&L: ${total_unrealized_pnl:.2f}')

print(f'\nCurrent Positions ({len(positions)}):')
for pos in positions:
    pnl = float(pos.unrealized_pl)
    pnl_pct = float(pos.unrealized_plpc) * 100
    print(f'{pos.symbol}: {pos.qty} shares, P&L: ${pnl:.2f} ({pnl_pct:.1f}%)')
    print(f'  Market Value: ${float(pos.market_value):.2f}, Cost Basis: ${float(pos.cost_basis):.2f}')
