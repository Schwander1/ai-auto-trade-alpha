#!/usr/bin/env python3
"""
Wrapper to add compliance logging to existing signals
Run this to automatically add compliance to your signal files
"""
import os
import sys

def add_compliance_to_signal(signal_file):
    """Add compliance import and logging to signal file"""
    
    # Read original file
    with open(signal_file, 'r') as f:
        content = f.read()
    
    # Check if already has compliance
    if 'from compliance.signal_logger import log_signal_with_compliance' in content:
        print(f"✅ {signal_file} already has compliance logging")
        return
    
    # Add import at top (after other imports)
    import_line = "\nfrom compliance.signal_logger import log_signal_with_compliance\n"
    
    # Find where to insert (after imports)
    lines = content.split('\n')
    insert_index = 0
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            insert_index = i + 1
    
    lines.insert(insert_index, import_line.strip())
    
    # Add logging call (you'll need to customize based on your signal structure)
    # This is a placeholder - adjust based on actual signal return format
    logging_template = """
    # Compliance logging
    if signal_data:  # Assuming your signal returns signal_data dict
        log_signal_with_compliance(signal_data)
"""
    
    # Write back
    with open(signal_file, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ Added compliance logging to {signal_file}")
    print(f"⚠️  Please manually add log_signal_with_compliance(signal_data) call where signals are generated")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 add_compliance_wrapper.py <signal_file.py>")
        print("\nExample: python3 add_compliance_wrapper.py signals/signal_rsi.py")
        sys.exit(1)
    
    signal_file = sys.argv[1]
    if not os.path.exists(signal_file):
        print(f"❌ File not found: {signal_file}")
        sys.exit(1)
    
    add_compliance_to_signal(signal_file)
