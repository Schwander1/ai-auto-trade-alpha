#!/usr/bin/env python3
"""
Add Better Execution Logging
Enhance logging to understand why trades aren't executing
"""
import sys
from pathlib import Path

# Add paths
argo_path = Path(__file__).parent / "argo"
if str(argo_path) not in sys.path:
    sys.path.insert(0, str(argo_path))

def enhance_execution_logging():
    """Add better logging to signal generation service"""
    print("\n" + "="*70)
    print("🔧 ENHANCING EXECUTION LOGGING")
    print("="*70)
    
    service_file = Path("argo/argo/core/signal_generation_service.py")
    
    if not service_file.exists():
        print(f"   ❌ File not found: {service_file}")
        return False
    
    try:
        with open(service_file, 'r') as f:
            content = f.read()
        
        # Check if logging already enhanced
        if "logger.info(f\"🔍 Execution check:" in content:
            print("   ✅ Execution logging already enhanced")
            return True
        
        # Find the execution check location
        old_code = """        # Execute trade if enabled
        if self.auto_execute and self.trading_engine and account and not self._paused:
            executed = await self._execute_trade_if_valid(
                signal, account, existing_positions, symbol
            )
            self._track_trade_execution(signal, signal_id, executed)
        else:
            self._track_signal_skipped(signal_id)"""
        
        new_code = """        # Execute trade if enabled
        # Enhanced logging for execution debugging
        execution_conditions = {
            'auto_execute': self.auto_execute,
            'trading_engine': self.trading_engine is not None,
            'account': account is not None,
            'not_paused': not self._paused,
        }
        
        if all(execution_conditions.values()):
            logger.debug(f"🔍 Execution check for {symbol}: All conditions met, attempting execution")
            executed = await self._execute_trade_if_valid(
                signal, account, existing_positions, symbol
            )
            self._track_trade_execution(signal, signal_id, executed)
            if not executed:
                logger.warning(f"⚠️  Trade execution returned False for {symbol} - check risk validation logs")
        else:
            failed_conditions = [k for k, v in execution_conditions.items() if not v]
            logger.warning(f"⏭️  Skipping {symbol} - Failed conditions: {', '.join(failed_conditions)}")
            self._track_signal_skipped(signal_id)"""
        
        if old_code in content:
            content = content.replace(old_code, new_code)
            
            with open(service_file, 'w') as f:
                f.write(content)
            
            print("   ✅ Enhanced execution logging added")
            print("   ⚠️  Service needs to be restarted for changes to take effect")
            return True
        else:
            print("   ⚠️  Could not find exact code pattern to replace")
            print("   The code may have been modified already")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main execution"""
    enhanced = enhance_execution_logging()
    
    print("\n" + "="*70)
    if enhanced:
        print("✅ Logging enhancement complete")
        print("   The service will now log detailed execution conditions")
        print("   ⚠️  Restart the service to see the new logs")
    else:
        print("⚠️  Could not enhance logging")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()

