#!/usr/bin/env python3
"""
Signal Distribution Service
Distributes signals from unified generator to multiple trading executors
"""
import asyncio
import logging
import httpx
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger("SignalDistributor")


class TradingExecutorClient:
    """Client for communicating with trading executors"""
    
    def __init__(self, executor_id: str, port: int, host: str = "localhost", config: Optional[Dict] = None):
        self.executor_id = executor_id
        self.base_url = f"http://{host}:{port}"
        self.config = config or {}
        # OPTIMIZATION: Reduced timeout for faster failure detection
        self.client = httpx.AsyncClient(timeout=10.0)  # Reduced from 30.0s
        self._enabled = True
    
    async def execute_signal(self, signal: Dict) -> Dict:
        """Send signal to executor for execution"""
        if not self._enabled:
            return {'success': False, 'error': 'Executor disabled'}
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/trading/execute",
                json=signal
            )
            response.raise_for_status()
            result = response.json()
            result['executor_id'] = self.executor_id
            return result
        except httpx.TimeoutException:
            logger.warning(f"Timeout sending signal to {self.executor_id}")
            return {'success': False, 'executor_id': self.executor_id, 'error': 'Timeout'}
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error sending signal to {self.executor_id}: {e}")
            return {'success': False, 'executor_id': self.executor_id, 'error': f'HTTP {e.response.status_code}'}
        except Exception as e:
            logger.error(f"Error sending signal to {self.executor_id}: {e}")
            return {'success': False, 'executor_id': self.executor_id, 'error': str(e)}
    
    async def get_status(self) -> Dict:
        """Get executor status"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/trading/status")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.debug(f"Error getting status from {self.executor_id}: {e}")
            return {'status': 'unavailable', 'executor_id': self.executor_id}
    
    async def close(self):
        """Close client"""
        await self.client.aclose()
    
    def disable(self):
        """Disable executor"""
        self._enabled = False
    
    def enable(self):
        """Enable executor"""
        self._enabled = True


class SignalDistributor:
    """
    Signal Distribution Service
    Distributes signals from unified generator to multiple trading executors
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.executors: Dict[str, TradingExecutorClient] = {}
        self._init_executors()
    
    def _init_executors(self):
        """Initialize trading executors"""
        # Argo executor
        self.executors['argo'] = TradingExecutorClient(
            executor_id='argo',
            port=8000,
            config={
                'min_confidence': 75.0,
                'service_type': 'argo',
            }
        )
        
        # Prop Firm executor
        self.executors['prop_firm'] = TradingExecutorClient(
            executor_id='prop_firm',
            port=8001,
            config={
                'min_confidence': 82.0,
                'service_type': 'prop_firm',
            }
        )
    
    def add_executor(self, executor_id: str, port: int, config: Optional[Dict] = None):
        """Add a new executor"""
        self.executors[executor_id] = TradingExecutorClient(
            executor_id=executor_id,
            port=port,
            config=config or {}
        )
        logger.info(f"✅ Added executor: {executor_id} on port {port}")
    
    def remove_executor(self, executor_id: str):
        """Remove an executor"""
        if executor_id in self.executors:
            asyncio.create_task(self.executors[executor_id].close())
            del self.executors[executor_id]
            logger.info(f"✅ Removed executor: {executor_id}")
    
    async def distribute_signal(self, signal: Dict) -> List[Dict]:
        """
        Distribute signal to appropriate executors - OPTIMIZED with parallel execution
        Returns list of execution results
        """
        # Determine which executors should receive this signal
        service_type = signal.get('service_type', 'both')
        
        # OPTIMIZATION: Collect eligible executors first, then execute in parallel
        eligible_executors = []
        for executor_id, executor in self.executors.items():
            if not executor._enabled:
                continue
            
            executor_config = executor.config
            
            # Check service type match
            if service_type not in ['both', executor_config.get('service_type', executor_id)]:
                continue
            
            # Check confidence threshold
            min_confidence = executor_config.get('min_confidence', 0.0)
            if signal.get('confidence', 0) < min_confidence:
                logger.debug(f"Skipping {executor_id}: confidence {signal.get('confidence')} < {min_confidence}")
                continue
            
            # Prop firm specific checks
            if executor_id == 'prop_firm':
                # Skip crisis signals for prop firm
                if signal.get('regime') == 'CRISIS':
                    logger.debug(f"Skipping {executor_id}: CRISIS regime")
                    continue
                
                # Additional prop firm filters can go here
                if signal.get('confidence', 0) < 82.0:
                    continue
            
            eligible_executors.append((executor_id, executor))
        
        if not eligible_executors:
            return []
        
        # OPTIMIZATION: Execute all eligible executors in parallel
        async def send_to_executor(executor_id: str, executor: TradingExecutorClient) -> Dict:
            try:
                result = await executor.execute_signal(signal)
                return result
            except Exception as e:
                logger.error(f"Error distributing to {executor_id}: {e}")
                return {
                    'executor_id': executor_id,
                    'success': False,
                    'error': str(e)
                }
        
        # Execute all in parallel
        tasks = [send_to_executor(executor_id, executor) for executor_id, executor in eligible_executors]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                executor_id = eligible_executors[i][0]
                logger.error(f"Exception distributing to {executor_id}: {result}")
                final_results.append({
                    'executor_id': executor_id,
                    'success': False,
                    'error': str(result)
                })
            else:
                final_results.append(result)
        
        return final_results
    
    async def check_executor_health(self) -> Dict[str, Dict]:
        """Check health of all executors"""
        health_status = {}
        
        for executor_id, executor in self.executors.items():
            try:
                status = await executor.get_status()
                health_status[executor_id] = status
            except Exception as e:
                health_status[executor_id] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        return health_status
    
    async def close_all(self):
        """Close all executor connections"""
        for executor in self.executors.values():
            await executor.close()

