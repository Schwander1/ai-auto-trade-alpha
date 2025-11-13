#!/usr/bin/env python3
"""
Argo-Alpine Signal Verification CLI Tool
Standalone tool for customers/auditors/regulators to verify signal integrity

Purpose:
- Works completely offline (no backend required)
- Independent verification of signal integrity
- Customer-facing compliance tool
"""
import argparse
import csv
import json
import hashlib
import sys
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import os

# Color support for terminal output
try:
    from colorama import init, Fore, Style
    init()
    HAS_COLORS = True
except ImportError:
    HAS_COLORS = False
    # Fallback for no colorama
    class Fore:
        GREEN = ''
        RED = ''
        YELLOW = ''
        BLUE = ''
        RESET = ''
    class Style:
        RESET_ALL = ''

def print_success(msg: str):
    """Print success message in green"""
    print(f"{Fore.GREEN}✅ {msg}{Style.RESET_ALL}")

def print_error(msg: str):
    """Print error message in red"""
    print(f"{Fore.RED}❌ {msg}{Style.RESET_ALL}")

def print_warning(msg: str):
    """Print warning message in yellow"""
    print(f"{Fore.YELLOW}⚠️  {msg}{Style.RESET_ALL}")

def print_info(msg: str):
    """Print info message in blue"""
    print(f"{Fore.BLUE}ℹ️  {msg}{Style.RESET_ALL}")


class SignalVerifier:
    """Verifies signal integrity"""
    
    @staticmethod
    def verify_hash(signal_data: Dict) -> tuple[bool, str, str]:
        """
        Verify SHA-256 hash of signal
        
        Returns:
            (is_valid, stored_hash, calculated_hash)
        """
        stored_hash = signal_data.get('verification_hash') or signal_data.get('sha256', '')
        
        # Calculate expected hash
        hash_fields = {
            'signal_id': signal_data.get('signal_id'),
            'symbol': signal_data.get('symbol'),
            'action': signal_data.get('action'),
            'entry_price': signal_data.get('entry_price'),
            'target_price': signal_data.get('target_price'),
            'stop_loss': signal_data.get('stop_loss'),
            'confidence': signal_data.get('confidence'),
            'strategy': signal_data.get('strategy'),
            'timestamp': signal_data.get('timestamp')
        }
        
        hash_string = json.dumps(hash_fields, sort_keys=True, default=str)
        calculated_hash = hashlib.sha256(hash_string.encode('utf-8')).hexdigest()
        
        is_valid = calculated_hash == stored_hash
        return is_valid, stored_hash, calculated_hash


def verify_hash_command(args):
    """Verify hash for a single signal"""
    signal_id = args.signal_id
    
    # Load signal data (from file or API)
    if args.file:
        # Load from CSV file
        signals = load_signals_from_csv(args.file)
        signal = next((s for s in signals if s.get('signal_id') == signal_id), None)
        
        if not signal:
            print_error(f"Signal {signal_id} not found in {args.file}")
            return False
    else:
        print_error("--file required for verify-hash command")
        return False
    
    # Verify hash
    is_valid, stored_hash, calculated_hash = SignalVerifier.verify_hash(signal)
    
    if is_valid:
        print_success(f"Hash verification PASSED for signal {signal_id}")
        print_info(f"Stored hash: {stored_hash[:16]}...")
        return True
    else:
        print_error(f"Hash verification FAILED for signal {signal_id}")
        print_error(f"Stored:    {stored_hash[:32]}...")
        print_error(f"Calculated: {calculated_hash[:32]}...")
        return False


def verify_backup_command(args):
    """Verify all signals in a backup file"""
    backup_file = args.file
    key_file = args.key  # Not used (encryption removed)
    
    print_info(f"Loading backup: {backup_file}")
    
    # Load signals from CSV
    signals = load_signals_from_csv(backup_file)
    
    if not signals:
        print_error("No signals found in backup file")
        return False
    
    print_info(f"Loaded {len(signals)} signals")
    print_info("Verifying SHA-256 hashes...")
    
    # Verify each signal
    results = {
        'total': len(signals),
        'valid': 0,
        'failed': 0,
        'failed_ids': []
    }
    
    for idx, signal in enumerate(signals):
        is_valid, stored_hash, calculated_hash = SignalVerifier.verify_hash(signal)
        
        if is_valid:
            results['valid'] += 1
        else:
            results['failed'] += 1
            signal_id = signal.get('signal_id', f'row_{idx+1}')
            results['failed_ids'].append(signal_id)
            
            if results['failed'] <= 10:  # Show first 10 failures
                print_error(f"  Signal {signal_id}: Hash mismatch")
    
    # Summary
    print("\n" + "=" * 60)
    print_info(f"Verification Summary:")
    print(f"  Total signals: {results['total']}")
    print_success(f"  Valid: {results['valid']}")
    if results['failed'] > 0:
        print_error(f"  Failed: {results['failed']}")
    print("=" * 60)
    
    # Output results
    if args.output:
        output_format = args.output.split('.')[-1].lower()
        
        if output_format == 'json':
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print_info(f"Results saved to: {args.output}")
        elif output_format == 'csv':
            with open(args.output, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['signal_id', 'status'])
                for signal in signals:
                    signal_id = signal.get('signal_id', 'unknown')
                    is_valid, _, _ = SignalVerifier.verify_hash(signal)
                    writer.writerow([signal_id, 'VALID' if is_valid else 'FAILED'])
            print_info(f"Results saved to: {args.output}")
        else:
            print_warning(f"Unknown output format: {output_format}, using JSON")
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print_info(f"Results saved to: {args.output}")
    
    return results['failed'] == 0


def batch_verify_command(args):
    """Verify multiple signals efficiently"""
    input_file = args.file
    output_file = args.output
    
    print_info(f"Loading signals from: {input_file}")
    
    signals = load_signals_from_csv(input_file)
    
    if not signals:
        print_error("No signals found")
        return False
    
    print_info(f"Verifying {len(signals)} signals...")
    
    # Progress tracking
    results = []
    failed_count = 0
    
    for idx, signal in enumerate(signals):
        is_valid, stored_hash, calculated_hash = SignalVerifier.verify_hash(signal)
        
        signal_id = signal.get('signal_id', f'row_{idx+1}')
        result = {
            'signal_id': signal_id,
            'symbol': signal.get('symbol'),
            'timestamp': signal.get('timestamp'),
            'valid': is_valid,
            'stored_hash': stored_hash[:16] if stored_hash else None,
            'calculated_hash': calculated_hash[:16] if not is_valid else None
        }
        results.append(result)
        
        if not is_valid:
            failed_count += 1
        
        # Progress indicator
        if (idx + 1) % 100 == 0:
            print_info(f"  Verified {idx + 1}/{len(signals)} signals...")
    
    # Summary
    print("\n" + "=" * 60)
    print_info(f"Batch Verification Summary:")
    print(f"  Total: {len(signals)}")
    print_success(f"  Valid: {len(signals) - failed_count}")
    if failed_count > 0:
        print_error(f"  Failed: {failed_count}")
    print("=" * 60)
    
    # Save results
    if output_file:
        with open(output_file, 'w') as f:
            json.dump({
                'summary': {
                    'total': len(signals),
                    'valid': len(signals) - failed_count,
                    'failed': failed_count
                },
                'results': results
            }, f, indent=2)
        print_info(f"Results saved to: {output_file}")
    
    return failed_count == 0


def generate_report_command(args):
    """Generate comprehensive verification report"""
    start_date = args.start
    end_date = args.end
    output_file = args.output
    
    print_info(f"Generating report for {start_date} to {end_date}")
    print_warning("Report generation requires signal data file")
    print_info("Use verify-backup or batch-verify commands first")
    
    # This would generate a PDF report
    # For now, create a JSON report
    report = {
        'report_type': 'Signal Integrity Verification',
        'date_range': {
            'start': start_date,
            'end': end_date
        },
        'generated_at': datetime.utcnow().isoformat(),
        'summary': {
            'total_signals': 0,
            'verified': 0,
            'failed': 0,
            'integrity_score': 0.0
        },
        'notes': 'Use verify-backup or batch-verify to populate this report'
    }
    
    if output_file.endswith('.json'):
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        print_info(f"Report saved to: {output_file}")
    else:
        print_warning("PDF generation not implemented, saving as JSON")
        json_file = output_file.replace('.pdf', '.json')
        with open(json_file, 'w') as f:
            json.dump(report, f, indent=2)
        print_info(f"Report saved to: {json_file}")
    
    return True


def load_signals_from_csv(csv_file: str) -> List[Dict]:
    """Load signals from CSV file"""
    signals = []
    
    try:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                signals.append(row)
    except FileNotFoundError:
        print_error(f"File not found: {csv_file}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error reading CSV: {e}")
        sys.exit(1)
    
    return signals


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Argo-Alpine Signal Verification CLI Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Verify hash for a specific signal
  python argo-verify-cli.py verify-hash --signal-id SIG-123 --file backup.csv
  
  # Verify all signals in a backup
  python argo-verify-cli.py verify-backup --file backup.csv --output results.json
  
  # Batch verify with progress
  python argo-verify-cli.py batch-verify --file signals.csv --output results.json
  
  # Generate report
  python argo-verify-cli.py generate-report --start 2024-01-01 --end 2024-01-31 --output report.json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # verify-hash command
    hash_parser = subparsers.add_parser('verify-hash', help='Verify hash for a single signal')
    hash_parser.add_argument('--signal-id', required=True, help='Signal ID to verify')
    hash_parser.add_argument('--file', help='CSV file containing signals')
    
    # verify-backup command
    backup_parser = subparsers.add_parser('verify-backup', help='Verify all signals in a backup file')
    backup_parser.add_argument('--file', required=True, help='Backup CSV file')
    backup_parser.add_argument('--key', help='Encryption key file (not used - encryption removed)')
    backup_parser.add_argument('--output', help='Output file for results (JSON or CSV)')
    
    # batch-verify command
    batch_parser = subparsers.add_parser('batch-verify', help='Verify multiple signals efficiently')
    batch_parser.add_argument('--file', required=True, help='Input CSV file')
    batch_parser.add_argument('--output', required=True, help='Output JSON file')
    
    # generate-report command
    report_parser = subparsers.add_parser('generate-report', help='Generate comprehensive verification report')
    report_parser.add_argument('--start', required=True, help='Start date (YYYY-MM-DD)')
    report_parser.add_argument('--end', required=True, help='End date (YYYY-MM-DD)')
    report_parser.add_argument('--output', required=True, help='Output file (JSON or PDF)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    success = False
    if args.command == 'verify-hash':
        success = verify_hash_command(args)
    elif args.command == 'verify-backup':
        success = verify_backup_command(args)
    elif args.command == 'batch-verify':
        success = batch_verify_command(args)
    elif args.command == 'generate-report':
        success = generate_report_command(args)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

