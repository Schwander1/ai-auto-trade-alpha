#!/usr/bin/env python3
"""
Rate limiting and usage caps for Anthropic API
Usage: python scripts/agentic/rate_limiter.py check
"""

import os
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

# Add scripts/agentic to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from usage_tracker import UsageTracker


class RateLimiter:
    """
    Rate limiter for Anthropic API usage
    """
    
    def __init__(
        self,
        daily_limit: int = 100,
        monthly_limit: int = 2000,
        daily_cost_limit: float = 10.0,
        monthly_cost_limit: float = 50.0
    ):
        self.daily_limit = daily_limit
        self.monthly_limit = monthly_limit
        self.daily_cost_limit = daily_cost_limit
        self.monthly_cost_limit = monthly_cost_limit
        
        workspace_dir = Path(__file__).parent.parent.parent
        self.usage_file = workspace_dir / "logs" / "agentic_usage.jsonl"
        self.tracker = UsageTracker(self.usage_file)
    
    def check_limit(self, raise_on_exceed: bool = True) -> Dict[str, bool]:
        """
        Check if usage is within limits
        
        Returns:
            Dict with limit status for each limit type
        """
        daily_usage = self.tracker.get_usage(days=1)
        monthly_usage = self.tracker.get_usage(days=30)
        
        results = {
            "daily_requests_ok": daily_usage["total_requests"] < self.daily_limit,
            "monthly_requests_ok": monthly_usage["total_requests"] < self.monthly_limit,
            "daily_cost_ok": daily_usage["total_cost"] < self.daily_cost_limit,
            "monthly_cost_ok": monthly_usage["total_cost"] < self.monthly_cost_limit,
            "daily_requests": daily_usage["total_requests"],
            "monthly_requests": monthly_usage["total_requests"],
            "daily_cost": daily_usage["total_cost"],
            "monthly_cost": monthly_usage["total_cost"]
        }
        
        if raise_on_exceed:
            errors = []
            
            if not results["daily_requests_ok"]:
                errors.append(
                    f"Daily request limit exceeded: {results['daily_requests']}/{self.daily_limit}"
                )
            
            if not results["monthly_requests_ok"]:
                errors.append(
                    f"Monthly request limit exceeded: {results['monthly_requests']}/{self.monthly_limit}"
                )
            
            if not results["daily_cost_ok"]:
                errors.append(
                    f"Daily cost limit exceeded: ${results['daily_cost']:.2f}/${self.daily_cost_limit:.2f}"
                )
            
            if not results["monthly_cost_ok"]:
                errors.append(
                    f"Monthly cost limit exceeded: ${results['monthly_cost']:.2f}/${self.monthly_cost_limit:.2f}"
                )
            
            if errors:
                raise Exception("Rate limit exceeded:\n" + "\n".join(f"  - {e}" for e in errors))
        
        return results
    
    def status(self) -> str:
        """Get human-readable status"""
        try:
            results = self.check_limit(raise_on_exceed=False)
            
            status_lines = [
                "Rate Limit Status:",
                f"  Daily Requests: {results['daily_requests']}/{self.daily_limit} {'✅' if results['daily_requests_ok'] else '❌'}",
                f"  Monthly Requests: {results['monthly_requests']}/{self.monthly_limit} {'✅' if results['monthly_requests_ok'] else '❌'}",
                f"  Daily Cost: ${results['daily_cost']:.2f}/${self.daily_cost_limit:.2f} {'✅' if results['daily_cost_ok'] else '❌'}",
                f"  Monthly Cost: ${results['monthly_cost']:.2f}/${self.monthly_cost_limit:.2f} {'✅' if results['monthly_cost_ok'] else '❌'}"
            ]
            
            return "\n".join(status_lines)
        except Exception as e:
            return f"Error checking limits: {e}"


def main():
    limiter = RateLimiter()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "check":
            try:
                limiter.check_limit()
                print("✅ All limits OK")
            except Exception as e:
                print(f"❌ {e}")
                sys.exit(1)
        elif command == "status":
            print(limiter.status())
        else:
            print(f"Unknown command: {command}")
            print("Available commands: check, status")
            sys.exit(1)
    else:
        # Default: show status
        print(limiter.status())


if __name__ == "__main__":
    main()

