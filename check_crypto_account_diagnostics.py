#!/usr/bin/env python3
"""
Check crypto account diagnostics - crypto status and non-marginable buying power
"""
import subprocess
import sys
import json
from datetime import datetime

PRODUCTION_SERVER = "178.156.194.174"
PRODUCTION_USER = "root"

def run_remote_command(cmd):
    """Run a command on the production server"""
    try:
        result = subprocess.run(
            f'ssh {PRODUCTION_USER}@{PRODUCTION_SERVER} "{cmd}"',
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return None, str(e), 1

def check_crypto_diagnostics():
    """Check crypto account diagnostics"""
    print("="*70)
    print("CRYPTO ACCOUNT DIAGNOSTICS")
    print("="*70)
    print(f"Server: {PRODUCTION_SERVER}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    script_content = '''import sys
import os
sys.path.insert(0, '/root/argo-production-prop-firm')
os.chdir('/root/argo-production-prop-firm')
from argo.core.paper_trading_engine import PaperTradingEngine
import json

try:
    engine = PaperTradingEngine('/root/argo-production-prop-firm/config.json')
    account_obj = engine.alpaca.get_account()
    
    result = {
        'crypto_status': getattr(account_obj, 'crypto_status', 'UNKNOWN'),
        'cash': float(account_obj.cash),
        'buying_power': float(account_obj.buying_power),
        'non_marginable_buying_power': float(getattr(account_obj, 'non_marginable_buying_power', 0)),
        'account_number': account_obj.account_number,
        'account_type': 'PAPER' if account_obj.account_number.startswith('PA') else 'LIVE',
        'portfolio_value': float(account_obj.portfolio_value),
        'equity': float(account_obj.equity),
    }
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({'error': str(e)}))
'''
    
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script_content)
        temp_script = f.name
    
    try:
        import subprocess
        copy_cmd = f'scp {temp_script} {PRODUCTION_USER}@{PRODUCTION_SERVER}:/tmp/check_crypto_diagnostics.py'
        subprocess.run(copy_cmd, shell=True, capture_output=True, check=True)
        stdout, stderr, code = run_remote_command('python3 /tmp/check_crypto_diagnostics.py')
    finally:
        os.unlink(temp_script)
    
    if code == 0 and stdout:
        try:
            data = json.loads(stdout)
            if 'error' in data:
                print(f"❌ Error: {data['error']}")
                return None
            
            print(f"Account Number: {data['account_number']}")
            print(f"Account Type: {data['account_type']}")
            print()
            print(f"💰 Cash: ${data['cash']:,.2f}")
            print(f"💵 Buying Power: ${data['buying_power']:,.2f}")
            print(f"💵 Non-Marginable Buying Power: ${data['non_marginable_buying_power']:,.2f} ⭐ (for crypto)")
            print(f"📊 Portfolio Value: ${data['portfolio_value']:,.2f}")
            print(f"📈 Equity: ${data['equity']:,.2f}")
            print()
            print(f"🪙 Crypto Status: {data['crypto_status']}")
            print()
            
            # Status checks
            crypto_status = data['crypto_status']
            non_marginable_bp = data['non_marginable_buying_power']
            
            print("="*70)
            print("STATUS CHECKS")
            print("="*70)
            
            if crypto_status == 'ACTIVE':
                print("✅ Crypto Status: ACTIVE")
            else:
                print(f"❌ Crypto Status: {crypto_status} (needs to be ACTIVE)")
                print("   → Sign crypto agreement in Alpaca dashboard")
            
            if non_marginable_bp > 0:
                print(f"✅ Non-Marginable Buying Power: ${non_marginable_bp:,.2f} (sufficient for crypto)")
            else:
                print(f"❌ Non-Marginable Buying Power: ${non_marginable_bp:,.2f} (need settled cash)")
                print("   → Wait for cash to settle (T+1 for stock sales)")
                print("   → Crypto-to-crypto trades settle immediately")
            
            if crypto_status == 'ACTIVE' and non_marginable_bp > 0:
                print()
                print("✅ Crypto trading is READY!")
            elif crypto_status != 'ACTIVE':
                print()
                print("⚠️  Crypto trading NOT ready: Crypto status not ACTIVE")
            elif non_marginable_bp <= 0:
                print()
                print("⚠️  Crypto trading NOT ready: No non-marginable buying power (need settled cash)")
            
            return data
        except json.JSONDecodeError:
            print(f"❌ Could not parse results: {stdout}")
            return None
    else:
        print(f"❌ Error running diagnostics: {stderr}")
        return None
    
    print("="*70)

if __name__ == "__main__":
    check_crypto_diagnostics()

