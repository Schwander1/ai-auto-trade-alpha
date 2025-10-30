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
print(f'Daily P&L: ${account.day_trade_pnl}')

# Get current positions
positions = api.list_positions()
print(f'\nCurrent Positions ({len(positions)}):')
for pos in positions:
    pnl = float(pos.unrealized_pnl)
    print(f'{pos.symbol}: {pos.qty} shares, P&L: ${pnl:.2f}')
