#!/usr/bin/env python3
"""Win Rate Calculator - Trading signal statistics"""
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class WinRateStats:
    total_signals: int
    wins: int
    losses: int
    expired: int
    win_rate: float
    loss_rate: float
    total_traded: int

def calculate_win_rate(signals: List[Dict[str, Any]], outcome_key: str = 'outcome', 
                      exclude_expired: bool = True) -> WinRateStats:
    """
    Calculate win rate statistics from signals.
    
    Args:
        signals: List of signal dictionaries
        outcome_key: Key to use for outcome in signal dict
        exclude_expired: Whether to exclude expired signals from win rate calculation
    
    Returns:
        WinRateStats with calculated metrics
    """
    if not signals:
        return WinRateStats(
            total_signals=0,
            wins=0,
            losses=0,
            expired=0,
            win_rate=0.0,
            loss_rate=0.0,
            total_traded=0
        )
    
    wins = losses = expired = 0
    
    for signal in signals:
        outcome = signal.get(outcome_key)
        if outcome == 'win':
            wins += 1
        elif outcome == 'loss':
            losses += 1
        elif outcome in ('expired', None):
            expired += 1
    
    total_traded = wins + losses
    
    # Calculate win/loss rates with zero-division protection
    if exclude_expired:
        win_rate = (wins / total_traded * 100) if total_traded > 0 else 0.0
        loss_rate = (losses / total_traded * 100) if total_traded > 0 else 0.0
    else:
        total_with_expired = total_traded + expired
        win_rate = (wins / total_with_expired * 100) if total_with_expired > 0 else 0.0
        loss_rate = ((losses + expired) / total_with_expired * 100) if total_with_expired > 0 else 0.0
    
    return WinRateStats(
        total_signals=len(signals),
        wins=wins,
        losses=losses,
        expired=expired,
        win_rate=round(win_rate, 2),
        loss_rate=round(loss_rate, 2),
        total_traded=total_traded
    )
