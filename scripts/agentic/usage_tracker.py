#!/usr/bin/env python3
"""
Track Anthropic API usage and costs
Usage: python scripts/agentic/usage_tracker.py [command]
"""

import os
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

# Pricing per 1M tokens (as of 2025)
PRICING = {
    "claude-3-5-sonnet-20241022": {
        "input": 3.0,  # $3 per 1M input tokens
        "output": 15.0  # $15 per 1M output tokens
    },
    "claude-3-5-opus-20241022": {
        "input": 15.0,
        "output": 75.0
    },
    "claude-3-5-haiku-20241022": {
        "input": 0.8,
        "output": 4.0
    }
}

class UsageTracker:
    def __init__(self, log_file: Optional[Path] = None):
        if log_file is None:
            workspace_dir = Path(__file__).parent.parent.parent
            log_file = workspace_dir / "logs" / "agentic_usage.jsonl"
        
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log_request(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        operation: str = "unknown",
        success: bool = True
    ):
        """Log an API request"""
        # Calculate cost
        cost = self._calculate_cost(model, input_tokens, output_tokens)
        
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost": cost,
            "operation": operation,
            "success": success
        }
        
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        return entry
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on model and token usage"""
        if model not in PRICING:
            # Default to Sonnet pricing
            model = "claude-3-5-sonnet-20241022"
        
        pricing = PRICING[model]
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        return round(input_cost + output_cost, 6)
    
    def get_usage(self, days: int = 30) -> Dict:
        """Get usage statistics for the last N days"""
        if not self.log_file.exists():
            return {
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "by_model": {},
                "by_operation": {},
                "daily_average": 0.0
            }
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        total_requests = 0
        total_tokens = 0
        total_cost = 0.0
        by_model = defaultdict(lambda: {"requests": 0, "tokens": 0, "cost": 0.0})
        by_operation = defaultdict(lambda: {"requests": 0, "tokens": 0, "cost": 0.0})
        
        with open(self.log_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    entry_date_str = entry["timestamp"]
                    # Handle both timezone-aware and naive datetimes
                    if entry_date_str.endswith('Z'):
                        entry_date_str = entry_date_str[:-1] + '+00:00'
                    entry_date = datetime.fromisoformat(entry_date_str.replace('Z', '+00:00'))
                    # Make timezone-aware if needed
                    if entry_date.tzinfo is None:
                        entry_date = entry_date.replace(tzinfo=timezone.utc)
                    
                    if entry_date < cutoff_date:
                        continue
                    
                    total_requests += 1
                    total_tokens += entry["total_tokens"]
                    total_cost += entry["cost"]
                    
                    model = entry["model"]
                    by_model[model]["requests"] += 1
                    by_model[model]["tokens"] += entry["total_tokens"]
                    by_model[model]["cost"] += entry["cost"]
                    
                    operation = entry.get("operation", "unknown")
                    by_operation[operation]["requests"] += 1
                    by_operation[operation]["tokens"] += entry["total_tokens"]
                    by_operation[operation]["cost"] += entry["cost"]
                except (json.JSONDecodeError, KeyError):
                    continue
        
        return {
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "total_cost": round(total_cost, 2),
            "by_model": dict(by_model),
            "by_operation": dict(by_operation),
            "daily_average": round(total_cost / days, 2) if days > 0 else 0.0,
            "period_days": days
        }
    
    def report(self, days: int = 30):
        """Print usage report"""
        usage = self.get_usage(days)
        
        print("=" * 60)
        print(f"Agentic API Usage Report (Last {days} days)")
        print("=" * 60)
        print(f"Total Requests: {usage['total_requests']}")
        print(f"Total Tokens: {usage['total_tokens']:,}")
        print(f"Total Cost: ${usage['total_cost']:.2f}")
        print(f"Daily Average: ${usage['daily_average']:.2f}")
        print()
        
        if usage['by_model']:
            print("By Model:")
            for model, stats in usage['by_model'].items():
                print(f"  {model}:")
                print(f"    Requests: {stats['requests']}")
                print(f"    Tokens: {stats['tokens']:,}")
                print(f"    Cost: ${stats['cost']:.2f}")
            print()
        
        if usage['by_operation']:
            print("By Operation:")
            for operation, stats in usage['by_operation'].items():
                print(f"  {operation}:")
                print(f"    Requests: {stats['requests']}")
                print(f"    Tokens: {stats['tokens']:,}")
                print(f"    Cost: ${stats['cost']:.2f}")
        
        print("=" * 60)
        
        # Cost warnings
        if usage['total_cost'] > 50:
            print("⚠️  Warning: Monthly cost exceeds $50")
        if usage['daily_average'] > 2:
            print("⚠️  Warning: Daily average exceeds $2/day")


def main():
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        tracker = UsageTracker()
        
        if command == "report":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            tracker.report(days)
        elif command == "log":
            # Example: python usage_tracker.py log claude-3-5-sonnet-20241022 1000 500 refactor
            if len(sys.argv) < 5:
                print("Usage: python usage_tracker.py log <model> <input_tokens> <output_tokens> <operation>")
                sys.exit(1)
            
            model = sys.argv[2]
            input_tokens = int(sys.argv[3])
            output_tokens = int(sys.argv[4])
            operation = sys.argv[5] if len(sys.argv) > 5 else "unknown"
            
            entry = tracker.log_request(model, input_tokens, output_tokens, operation)
            print(f"✅ Logged: {entry['cost']:.6f} USD")
        else:
            print(f"Unknown command: {command}")
            print("Available commands: report, log")
            sys.exit(1)
    else:
        # Default: show report
        tracker = UsageTracker()
        tracker.report(30)


if __name__ == "__main__":
    main()

