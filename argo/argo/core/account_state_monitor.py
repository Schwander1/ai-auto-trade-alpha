"""
Account State Monitor
Monitors account state changes and triggers queue processing
"""
import asyncio
import logging
import httpx
from datetime import datetime
from typing import Dict, Optional, Callable, Any, List
from dataclasses import dataclass, field

logger = logging.getLogger("AccountStateMonitor")

@dataclass
class AccountState:
    """Represents account state at a point in time"""
    executor_id: str
    buying_power: float
    cash: float
    portfolio_value: float
    positions_count: int
    timestamp: str
    positions: Optional[List[Dict[str, Any]]] = None

class AccountStateMonitor:
    """Monitors account state and detects changes"""

    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval
        self._running = False
        self._last_states: Dict[str, AccountState] = {}
        self._callbacks: List[Callable] = []
        self._monitoring_task: Optional[asyncio.Task] = None

    def add_callback(self, callback: Callable):
        """Add callback for state changes"""
        self._callbacks.append(callback)

    async def start_monitoring(self):
        """Start monitoring account states"""
        self._running = True
        logger.info(f"🔄 Starting account state monitoring (check every {self.check_interval}s)")

        while self._running:
            try:
                await self._check_account_states()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"❌ Error monitoring account states: {e}")
                await asyncio.sleep(self.check_interval)

    async def _check_account_states(self):
        """Check all account states and detect changes"""
        current_states = await self._fetch_account_states()

        for executor_id, current_state in current_states.items():
            last_state = self._last_states.get(executor_id)

            if last_state:
                # Detect changes
                changes = self._detect_changes(last_state, current_state)
                if changes:
                    logger.info(f"📊 Account state changed for {executor_id}: {changes}")
                    await self._notify_callbacks(executor_id, current_state, changes)

            self._last_states[executor_id] = current_state

    def _detect_changes(self, old_state: AccountState, new_state: AccountState) -> Dict[str, Any]:
        """Detect what changed between states"""
        changes = {}

        if old_state.buying_power != new_state.buying_power:
            changes['buying_power'] = {
                'old': old_state.buying_power,
                'new': new_state.buying_power,
                'delta': new_state.buying_power - old_state.buying_power
            }

        if old_state.positions_count != new_state.positions_count:
            changes['positions'] = {
                'old': old_state.positions_count,
                'new': new_state.positions_count
            }

        if old_state.portfolio_value != new_state.portfolio_value:
            changes['portfolio_value'] = {
                'old': old_state.portfolio_value,
                'new': new_state.portfolio_value
            }

        return changes

    async def _fetch_account_states(self) -> Dict[str, AccountState]:
        """Fetch current account states from all executors"""
        states = {}
        executors = [
            ('argo', 8000),
            ('prop_firm', 8001)
        ]

        async with httpx.AsyncClient(timeout=5.0) as client:
            for executor_id, port in executors:
                try:
                    response = await client.get(f'http://localhost:{port}/api/v1/trading/status')
                    if response.status_code == 200:
                        data = response.json()
                        account = data.get('account', {})
                        states[executor_id] = AccountState(
                            executor_id=executor_id,
                            buying_power=account.get('buying_power', 0),
                            cash=account.get('cash', 0),
                            portfolio_value=account.get('portfolio_value', 0),
                            positions_count=data.get('positions_count', 0),
                            timestamp=datetime.now().isoformat()
                        )
                except Exception as e:
                    logger.debug(f"Could not fetch state for {executor_id}: {e}")

        return states

    async def _notify_callbacks(self, executor_id: str, state: AccountState, changes: Dict[str, Any]):
        """Notify all callbacks of state changes"""
        for callback in self._callbacks:
            try:
                await callback(executor_id, state, changes)
            except Exception as e:
                logger.error(f"❌ Error in callback: {e}")

    def stop_monitoring(self):
        """Stop monitoring"""
        self._running = False
        logger.info("🛑 Stopped account state monitoring")

    def get_current_states(self) -> Dict[str, AccountState]:
        """Get last known account states"""
        return self._last_states.copy()
