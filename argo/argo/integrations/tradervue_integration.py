"""
Enhanced Tradervue Integration Service
Integrates with UnifiedPerformanceTracker for complete trade lifecycle tracking
"""
import logging
from typing import Optional, Dict
from datetime import datetime

from argo.tracking.unified_tracker import Trade, UnifiedPerformanceTracker
from argo.integrations.tradervue_client import TradervueClient, TradervueTrade, get_tradervue_client

logger = logging.getLogger(__name__)


class TradervueIntegration:
    """
    Enhanced Tradervue integration service
    
    Features:
    - Automatic sync of trade entries and exits
    - Complete trade lifecycle tracking
    - Performance metrics sync
    - Integration with UnifiedPerformanceTracker
    """
    
    def __init__(
        self,
        tracker: Optional[UnifiedPerformanceTracker] = None,
        client: Optional[TradervueClient] = None
    ):
        """
        Initialize Tradervue integration
        
        Args:
            tracker: UnifiedPerformanceTracker instance
            client: TradervueClient instance (optional, will create if not provided)
        """
        self.tracker = tracker or UnifiedPerformanceTracker()
        self.client = client or get_tradervue_client()
        self._trade_id_mapping = {}  # Map Argo trade IDs to Tradervue trade IDs
        
        if self.client.enabled:
            logger.info("✅ Tradervue integration initialized")
        else:
            logger.warning("⚠️  Tradervue integration disabled (credentials not configured)")
    
    def sync_trade_entry(self, trade: Trade) -> Optional[str]:
        """
        Sync trade entry to Tradervue
        
        Args:
            trade: Trade object from UnifiedPerformanceTracker
            
        Returns:
            Tradervue trade ID or None if failed
        """
        if not self.client.enabled:
            return None
        
        try:
            # Map signal type to Tradervue side
            side = "B" if trade.signal_type == "long" else "SS"
            
            # Format date
            entry_date = datetime.fromisoformat(trade.entry_timestamp).strftime("%Y-%m-%d")
            
            # Build notes with comprehensive trade information
            notes_parts = [
                f"Alpine Analytics | {trade.confidence}% confidence",
                f"SHA256: {trade.verification_hash[:8]}",
                f"Trade ID: {trade.id}",
                f"Signal ID: {trade.signal_id}"
            ]
            
            if trade.regime:
                notes_parts.append(f"Regime: {trade.regime}")
            
            if trade.stop_price:
                notes_parts.append(f"Stop: ${trade.stop_price:.2f}")
            
            if trade.target_price:
                notes_parts.append(f"Target: ${trade.target_price:.2f}")
            
            if trade.slippage_entry_pct:
                notes_parts.append(f"Entry Slippage: {trade.slippage_entry_pct:.2f}%")
            
            notes = " | ".join(notes_parts)
            
            # Create Tradervue trade
            tradervue_trade = TradervueTrade(
                symbol=trade.symbol,
                quantity=trade.quantity,
                date=entry_date,
                price=trade.actual_entry_price or trade.entry_price,
                side=side,
                notes=notes,
                commission=trade.commission
            )
            
            # Submit to Tradervue
            response = self.client.submit_trade(tradervue_trade)
            
            if response:
                tradervue_id = response.get("id") or response.get("trade_id")
                if tradervue_id:
                    # Store mapping for exit updates
                    self._trade_id_mapping[trade.id] = tradervue_id
                    logger.info(f"✅ Tradervue entry synced: {trade.symbol} (Tradervue ID: {tradervue_id})")
                    return tradervue_id
            
            logger.warning(f"⚠️  Tradervue entry sync failed: {trade.symbol}")
            return None
            
        except Exception as e:
            logger.error(f"Error syncing trade entry to Tradervue: {e}")
            return None
    
    def sync_trade_exit(self, trade: Trade) -> bool:
        """
        Sync trade exit to Tradervue
        
        Args:
            trade: Trade object with exit information
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client.enabled:
            return False
        
        if not trade.exit_price or not trade.exit_timestamp:
            logger.warning(f"Trade {trade.id} has no exit information")
            return False
        
        try:
            # Get Tradervue trade ID from mapping
            tradervue_id = self._trade_id_mapping.get(trade.id)
            
            if not tradervue_id:
                logger.warning(f"No Tradervue ID found for trade {trade.id}, syncing as new trade")
                # Fallback: submit as new trade (close position)
                return self._sync_exit_as_new_trade(trade)
            
            # Format exit date
            exit_date = datetime.fromisoformat(trade.exit_timestamp).strftime("%Y-%m-%d")
            
            # Map signal type to Tradervue side (opposite for exit)
            side = "S" if trade.signal_type == "long" else "B"
            
            # Build updated notes
            notes_parts = [
                f"Alpine Analytics | {trade.confidence}% confidence",
                f"SHA256: {trade.verification_hash[:8]}",
                f"Trade ID: {trade.id}",
                f"Signal ID: {trade.signal_id}",
                f"Exit Reason: {trade.exit_reason or 'unknown'}",
                f"Exit Method: {trade.exit_method or 'unknown'}"
            ]
            
            if trade.exit_regime:
                notes_parts.append(f"Exit Regime: {trade.exit_regime}")
            
            if trade.slippage_exit_pct:
                notes_parts.append(f"Exit Slippage: {trade.slippage_exit_pct:.2f}%")
            
            if trade.pnl_dollars is not None:
                notes_parts.append(f"P&L: ${trade.pnl_dollars:.2f} ({trade.pnl_percent:.2f}%)")
            
            notes = " | ".join(notes_parts)
            
            # Create exit trade
            exit_trade = TradervueTrade(
                symbol=trade.symbol,
                quantity=trade.quantity,
                date=exit_date,
                price=trade.actual_exit_price or trade.exit_price,
                side=side,
                notes=notes,
                commission=trade.commission,
                trade_id=tradervue_id  # Link to entry trade
            )
            
            # Update in Tradervue
            response = self.client.update_trade(tradervue_id, exit_trade)
            
            if response:
                logger.info(f"✅ Tradervue exit synced: {trade.symbol} (P&L: ${trade.pnl_dollars:.2f})")
                return True
            else:
                logger.warning(f"⚠️  Tradervue exit sync failed: {trade.symbol}")
                return False
                
        except Exception as e:
            logger.error(f"Error syncing trade exit to Tradervue: {e}")
            return False
    
    def _sync_exit_as_new_trade(self, trade: Trade) -> bool:
        """Fallback: sync exit as new trade if entry not found"""
        try:
            exit_date = datetime.fromisoformat(trade.exit_timestamp).strftime("%Y-%m-%d")
            side = "S" if trade.signal_type == "long" else "B"
            
            exit_trade = TradervueTrade(
                symbol=trade.symbol,
                quantity=trade.quantity,
                date=exit_date,
                price=trade.actual_exit_price or trade.exit_price,
                side=side,
                notes=f"Exit | Trade ID: {trade.id} | P&L: ${trade.pnl_dollars:.2f}" if trade.pnl_dollars else f"Exit | Trade ID: {trade.id}",
                commission=trade.commission
            )
            
            response = self.client.submit_trade(exit_trade)
            return response is not None
            
        except Exception as e:
            logger.error(f"Error syncing exit as new trade: {e}")
            return False
    
    def sync_complete_trade(self, trade: Trade) -> bool:
        """
        Sync complete trade (entry + exit) to Tradervue
        
        Args:
            trade: Complete trade object with entry and exit
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client.enabled:
            return False
        
        # Sync entry
        tradervue_id = self.sync_trade_entry(trade)
        
        if not tradervue_id:
            return False
        
        # If trade has exit, sync exit
        if trade.exit_price and trade.exit_timestamp:
            return self.sync_trade_exit(trade)
        
        return True
    
    def sync_recent_trades(self, days: int = 30) -> Dict[str, int]:
        """
        Sync recent trades from UnifiedPerformanceTracker to Tradervue
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dict with sync statistics
        """
        if not self.client.enabled:
            return {"synced": 0, "failed": 0, "skipped": 0}
        
        trades = self.tracker._get_recent_trades(days=days)
        stats = {"synced": 0, "failed": 0, "skipped": 0}
        
        for trade in trades:
            # Skip if already synced (check mapping)
            if trade.id in self._trade_id_mapping:
                stats["skipped"] += 1
                continue
            
            # Sync based on trade state
            if trade.exit_price and trade.exit_timestamp:
                # Complete trade
                if self.sync_complete_trade(trade):
                    stats["synced"] += 1
                else:
                    stats["failed"] += 1
            else:
                # Entry only
                if self.sync_trade_entry(trade):
                    stats["synced"] += 1
                else:
                    stats["failed"] += 1
        
        logger.info(f"✅ Tradervue sync complete: {stats['synced']} synced, {stats['failed']} failed, {stats['skipped']} skipped")
        return stats
    
    def get_performance_metrics(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Get performance metrics from Tradervue
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Performance metrics dict or None
        """
        return self.client.get_performance_metrics(start_date, end_date)
    
    def get_widget_url(self, widget_type: str = "equity") -> Optional[str]:
        """Get widget URL for embedding"""
        return self.client.get_widget_url(widget_type)
    
    def get_profile_url(self) -> Optional[str]:
        """Get public profile URL"""
        return self.client.get_profile_url()


# Singleton instance
_integration_instance: Optional[TradervueIntegration] = None

def get_tradervue_integration() -> TradervueIntegration:
    """Get singleton Tradervue integration instance"""
    global _integration_instance
    if _integration_instance is None:
        _integration_instance = TradervueIntegration()
    return _integration_instance

