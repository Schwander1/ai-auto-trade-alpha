#!/usr/bin/env python3
"""Check which Alpaca account is active"""
import sys
import logging
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from argo.core.environment import detect_environment, get_environment_info
    from argo.core.paper_trading_engine import PaperTradingEngine
except ImportError as e:
    logger.error(f"Could not import required modules: {e}")
    print(f"❌ Error: Could not import required modules: {e}")
    sys.exit(1)

def main():
    try:
        print('\n' + '='*70)
        print('🔍 ALPACA ACCOUNT STATUS CHECK')
        print('='*70)

        # Environment info
        try:
            env_info = get_environment_info()
            print(f'\n🌍 Environment: {env_info["environment"].upper()}')
            print(f'   Hostname: {env_info["hostname"]}')
            print(f'   Working Directory: {env_info["cwd"]}')
        except Exception as e:
            logger.error(f"Error getting environment info: {e}")
            print(f'\n⚠️  Could not get environment info: {e}')

        # Trading engine
        try:
            engine = PaperTradingEngine()
        except Exception as e:
            logger.error(f"Error initializing trading engine: {e}")
            print(f'\n❌ Error initializing trading engine: {e}')
            sys.exit(1)

        if engine.alpaca_enabled:
            try:
                account = engine.get_account_details()
                print(f'\n✅ Connected to Alpaca')
                print(f'   Account Name: {engine.account_name}')
                print(f'   Environment: {engine.environment}')
                print(f'   Portfolio Value: ${account["portfolio_value"]:,.2f}')
                print(f'   Buying Power: ${account["buying_power"]:,.2f}')
                print(f'   Account Number: {account["account_number"]}')
                
                # Verify this is the correct account for environment
                if engine.environment == "production":
                    print(f'\n✅ Using PRODUCTION paper account')
                else:
                    print(f'\n✅ Using DEV paper account')
                
                # Show positions
                try:
                    positions = engine.get_positions()
                    print(f'\n📊 Open Positions: {len(positions)}')
                    if positions:
                        print(f'\n{"Symbol":<10} {"Side":<6} {"Qty":<8} {"Entry":<10} {"Current":<10} {"P&L %":<10}')
                        print("-" * 60)
                        for pos in positions:
                            pnl_sign = "+" if pos['pnl_pct'] >= 0 else ""
                            print(f"{pos['symbol']:<10} {pos['side']:<6} {pos['qty']:<8} "
                                  f"${pos['entry_price']:<9.2f} ${pos['current_price']:<9.2f} "
                                  f"{pnl_sign}{pos['pnl_pct']:<9.2f}%")
                except Exception as e:
                    logger.error(f"Error getting positions: {e}")
                    print(f'\n⚠️  Could not get positions: {e}')
            except Exception as e:
                logger.error(f"Error getting account details: {e}")
                print(f'\n❌ Error getting account details: {e}')
        else:
            print(f'\n❌ Alpaca not connected')

        print('\n' + '='*70 + '\n')
    except KeyboardInterrupt:
        logger.warning("Account check interrupted by user")
        print("\n⚠️  Account check interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f'\n❌ Unexpected error: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()

