"""
Queue Processor
Automatically executes ready signals from the queue
"""
import asyncio
import logging
import httpx
from typing import Dict, Optional, Any
from datetime import datetime

from argo.core.signal_queue import SignalQueue, QueueStatus

logger = logging.getLogger("QueueProcessor")

class QueueProcessor:
    """Processes ready signals from the queue and executes them"""

    def __init__(self, signal_queue: SignalQueue, check_interval: int = 30):
        self.signal_queue = signal_queue
        self.check_interval = check_interval
        self._running = False
        self._processing_task = None

    async def start_processing(self):
        """Start processing ready signals"""
        self._running = True
        logger.info(f"🔄 Starting queue processor (check every {self.check_interval}s)")

        while self._running:
            try:
                await self._process_ready_signals()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"❌ Error in queue processor: {e}", exc_info=True)
                await asyncio.sleep(self.check_interval)

    async def _process_ready_signals(self):
        """Process signals that are ready to execute"""
        try:
            ready_signals = self.signal_queue.get_ready_signals(limit=10)

            if not ready_signals:
                return

            logger.info(f"📊 Processing {len(ready_signals)} ready signals")

            for queued_signal in ready_signals:
                try:
                    # Mark as executing
                    await self._mark_executing(queued_signal.signal_id)

                    # Execute signal
                    success = await self._execute_signal(queued_signal)

                    if success:
                        await self._mark_executed(queued_signal.signal_id)
                        logger.info(f"✅ Executed queued signal {queued_signal.signal_id}")
                    else:
                        # Increment retry count
                        await self._increment_retry(queued_signal.signal_id)
                        # Mark back as pending if retries not exhausted
                        if queued_signal.retry_count < 3:
                            await self._mark_pending(queued_signal.signal_id)
                        else:
                            await self._mark_failed(queued_signal.signal_id)
                            logger.warning(f"⚠️ Signal {queued_signal.signal_id} failed after 3 retries")

                except Exception as e:
                    logger.error(f"❌ Error processing signal {queued_signal.signal_id}: {e}")
                    await self._increment_retry(queued_signal.signal_id)
                    await self._mark_pending(queued_signal.signal_id)

        except Exception as e:
            logger.error(f"❌ Error processing ready signals: {e}", exc_info=True)

    async def _execute_signal(self, queued_signal) -> bool:
        """Execute a queued signal"""
        try:
            # Convert queued signal back to signal format
            signal = {
                'signal_id': queued_signal.signal_id,
                'symbol': queued_signal.symbol,
                'action': queued_signal.action,
                'entry_price': queued_signal.entry_price,
                'target_price': queued_signal.target_price,
                'stop_price': queued_signal.stop_price,
                'confidence': queued_signal.confidence,
                'timestamp': queued_signal.timestamp
            }

            # Determine executor
            executor_id = queued_signal.executor_id or 'argo'
            port = 8000 if executor_id == 'argo' else 8001

            # Send to executor
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f'http://localhost:{port}/api/v1/trading/execute',
                    json=signal
                )

                if response.status_code == 200:
                    result = response.json()
                    return result.get('success', False)
                else:
                    logger.warning(f"Executor returned {response.status_code} for signal {queued_signal.signal_id}")
                    return False

        except Exception as e:
            logger.error(f"Error executing signal {queued_signal.signal_id}: {e}")
            return False

    async def _mark_executing(self, signal_id: str):
        """Mark signal as executing"""
        import sqlite3
        conn = sqlite3.connect(str(self.signal_queue.db_path), timeout=10.0)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE signal_queue
            SET status = ?, last_checked = datetime('now')
            WHERE signal_id = ?
        ''', (QueueStatus.EXECUTING.value, signal_id))
        conn.commit()
        conn.close()

    async def _mark_executed(self, signal_id: str):
        """Mark signal as executed"""
        import sqlite3
        conn = sqlite3.connect(str(self.signal_queue.db_path), timeout=10.0)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE signal_queue
            SET status = ?, executed_at = datetime('now')
            WHERE signal_id = ?
        ''', (QueueStatus.EXECUTED.value, signal_id))
        conn.commit()
        conn.close()

    async def _mark_pending(self, signal_id: str):
        """Mark signal as pending"""
        import sqlite3
        conn = sqlite3.connect(str(self.signal_queue.db_path), timeout=10.0)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE signal_queue
            SET status = ?
            WHERE signal_id = ?
        ''', (QueueStatus.PENDING.value, signal_id))
        conn.commit()
        conn.close()

    async def _mark_failed(self, signal_id: str):
        """Mark signal as failed"""
        import sqlite3
        conn = sqlite3.connect(str(self.signal_queue.db_path), timeout=10.0)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE signal_queue
            SET status = ?, execution_error = 'Failed after retries'
            WHERE signal_id = ?
        ''', (QueueStatus.EXPIRED.value, signal_id))
        conn.commit()
        conn.close()

    async def _increment_retry(self, signal_id: str):
        """Increment retry count"""
        import sqlite3
        conn = sqlite3.connect(str(self.signal_queue.db_path), timeout=10.0)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE signal_queue
            SET retry_count = retry_count + 1
            WHERE signal_id = ?
        ''', (signal_id,))
        conn.commit()
        conn.close()

    def stop_processing(self):
        """Stop processing"""
        self._running = False
        logger.info("🛑 Stopped queue processor")
