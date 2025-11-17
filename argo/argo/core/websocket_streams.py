#!/usr/bin/env python3
"""
WebSocket Streams v5.0 - Phase 4
Real-time data streaming for Alpaca and Polygon
Replaces polling with WebSocket streams for 70-80% API cost reduction
"""
import asyncio
import logging
import json
from typing import Dict, Optional, Callable, List
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WebSocketStreams")

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    logger.warning("⚠️  websockets library not available. Install with: pip install websockets")


class AlpacaWebSocketStream:
    """
    Alpaca WebSocket stream for real-time market data
    Replaces polling API calls with persistent WebSocket connection
    """
    
    def __init__(self, api_key: str, api_secret: str, base_url: str = "wss://stream.data.alpaca.markets/v2/iex"):
        if not WEBSOCKETS_AVAILABLE:
            raise ImportError("websockets library required for WebSocket streams")
        
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.websocket = None
        self.running = False
        self.price_callbacks: Dict[str, Callable] = {}
        self.reconnect_delay = 5
        self.max_reconnect_delay = 60
    
    async def connect(self):
        """Connect to Alpaca WebSocket stream"""
        try:
            auth_message = {
                "action": "auth",
                "key": self.api_key,
                "secret": self.api_secret
            }
            
            self.websocket = await websockets.connect(self.base_url)
            await self.websocket.send(json.dumps(auth_message))
            
            # Wait for auth confirmation
            response = await self.websocket.recv()
            auth_response = json.loads(response)
            
            if auth_response.get('T') == 'success' and auth_response.get('msg') == 'authenticated':
                logger.info("✅ Connected to Alpaca WebSocket stream")
                self.running = True
                return True
            else:
                logger.error(f"❌ Alpaca WebSocket authentication failed: {auth_response}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to connect to Alpaca WebSocket: {e}")
            return False
    
    async def subscribe(self, symbols: List[str]):
        """Subscribe to price updates for symbols"""
        if not self.websocket or not self.running:
            await self.connect()
        
        subscribe_message = {
            "action": "subscribe",
            "trades": symbols
        }
        
        try:
            await self.websocket.send(json.dumps(subscribe_message))
            logger.info(f"✅ Subscribed to {len(symbols)} symbols: {symbols}")
        except Exception as e:
            logger.error(f"❌ Failed to subscribe to symbols: {e}")
    
    def register_price_callback(self, symbol: str, callback: Callable):
        """Register callback for price updates"""
        self.price_callbacks[symbol] = callback
    
    async def listen(self):
        """Listen for incoming messages and trigger callbacks"""
        if not self.websocket:
            return
        
        try:
            while self.running:
                try:
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=30.0)
                    data = json.loads(message)
                    
                    # Handle trade updates
                    if data.get('T') == 't':  # Trade update
                        symbol = data.get('S')  # Symbol
                        price = data.get('p')   # Price
                        timestamp = data.get('t')  # Timestamp
                        
                        if symbol and price and symbol in self.price_callbacks:
                            self.price_callbacks[symbol]({
                                'symbol': symbol,
                                'price': price,
                                'timestamp': timestamp,
                                'source': 'alpaca_websocket'
                            })
                    
                except asyncio.TimeoutError:
                    # Send ping to keep connection alive
                    await self.websocket.ping()
                except websockets.exceptions.ConnectionClosed:
                    logger.warning("⚠️  WebSocket connection closed, reconnecting...")
                    await self.reconnect()
                except Exception as e:
                    logger.error(f"❌ Error processing WebSocket message: {e}")
                    
        except Exception as e:
            logger.error(f"❌ WebSocket listen error: {e}")
    
    async def reconnect(self):
        """Reconnect to WebSocket stream"""
        self.running = False
        if self.websocket:
            try:
                await self.websocket.close()
            except (ConnectionError, RuntimeError, AttributeError) as e:
                # Ignore errors when closing websocket during reconnect
                logger.debug(f"Error closing websocket during reconnect: {e}")
                pass
        
        await asyncio.sleep(self.reconnect_delay)
        self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)
        
        await self.connect()
        self.reconnect_delay = 5  # Reset on successful reconnect
    
    async def disconnect(self):
        """Disconnect from WebSocket stream"""
        self.running = False
        if self.websocket:
            try:
                await self.websocket.close()
            except (ConnectionError, RuntimeError, AttributeError) as e:
                # Ignore errors when closing websocket
                logger.debug(f"Error closing websocket: {e}")
                pass
        logger.info("✅ Disconnected from Alpaca WebSocket stream")


class PolygonWebSocketStream:
    """
    Polygon.io WebSocket stream for real-time market data
    Alternative to Alpaca for additional data sources
    """
    
    def __init__(self, api_key: str, base_url: str = "wss://socket.polygon.io/stocks"):
        if not WEBSOCKETS_AVAILABLE:
            raise ImportError("websockets library required for WebSocket streams")
        
        self.api_key = api_key
        self.base_url = base_url
        self.websocket = None
        self.running = False
        self.price_callbacks: Dict[str, Callable] = {}
    
    async def connect(self):
        """Connect to Polygon WebSocket stream"""
        try:
            self.websocket = await websockets.connect(f"{self.base_url}?apiKey={self.api_key}")
            
            # Authenticate
            auth_message = {
                "action": "auth",
                "params": self.api_key
            }
            await self.websocket.send(json.dumps(auth_message))
            
            response = await self.websocket.recv()
            auth_response = json.loads(response)
            
            if auth_response[0].get('ev') == 'status' and auth_response[0].get('status') == 'auth_success':
                logger.info("✅ Connected to Polygon WebSocket stream")
                self.running = True
                return True
            else:
                logger.error(f"❌ Polygon WebSocket authentication failed: {auth_response}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to connect to Polygon WebSocket: {e}")
            return False
    
    async def subscribe(self, symbols: List[str]):
        """Subscribe to trades for symbols"""
        if not self.websocket or not self.running:
            await self.connect()
        
        subscribe_message = {
            "action": "subscribe",
            "params": ",".join([f"T.{symbol}" for symbol in symbols])
        }
        
        try:
            await self.websocket.send(json.dumps(subscribe_message))
            logger.info(f"✅ Subscribed to {len(symbols)} symbols on Polygon: {symbols}")
        except Exception as e:
            logger.error(f"❌ Failed to subscribe to Polygon symbols: {e}")
    
    def register_price_callback(self, symbol: str, callback: Callable):
        """Register callback for price updates"""
        self.price_callbacks[symbol] = callback
    
    async def listen(self):
        """Listen for incoming messages"""
        if not self.websocket:
            return
        
        try:
            while self.running:
                try:
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=30.0)
                    data = json.loads(message)
                    
                    # Handle trade updates (T = trade)
                    for event in data:
                        if event.get('ev') == 'T':  # Trade event
                            symbol = event.get('sym')  # Symbol
                            price = event.get('p')     # Price
                            timestamp = event.get('t')  # Timestamp
                            
                            if symbol and price and symbol in self.price_callbacks:
                                self.price_callbacks[symbol]({
                                    'symbol': symbol,
                                    'price': price,
                                    'timestamp': timestamp,
                                    'source': 'polygon_websocket'
                                })
                    
                except asyncio.TimeoutError:
                    await self.websocket.ping()
                except websockets.exceptions.ConnectionClosed:
                    logger.warning("⚠️  Polygon WebSocket connection closed, reconnecting...")
                    await self.reconnect()
                except Exception as e:
                    logger.error(f"❌ Error processing Polygon WebSocket message: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Polygon WebSocket listen error: {e}")
    
    async def reconnect(self):
        """Reconnect to Polygon WebSocket"""
        self.running = False
        if self.websocket:
            try:
                await self.websocket.close()
            except (ConnectionError, RuntimeError, AttributeError) as e:
                # Ignore errors when closing websocket during reconnect
                logger.debug(f"Error closing Polygon websocket during reconnect: {e}")
                pass
        
        await asyncio.sleep(5)
        await self.connect()
    
    async def disconnect(self):
        """Disconnect from Polygon WebSocket"""
        self.running = False
        if self.websocket:
            try:
                await self.websocket.close()
            except (ConnectionError, RuntimeError, AttributeError) as e:
                # Ignore errors when closing websocket
                logger.debug(f"Error closing Polygon websocket: {e}")
                pass
        logger.info("✅ Disconnected from Polygon WebSocket stream")


class WebSocketStreamManager:
    """
    Manager for multiple WebSocket streams
    Handles connection management, reconnection, and failover
    """
    
    def __init__(self):
        self.streams: List = []
        self.price_cache: Dict[str, Dict] = {}
        self.running = False
    
    def add_alpaca_stream(self, api_key: str, api_secret: str, base_url: str = None):
        """Add Alpaca WebSocket stream"""
        if not WEBSOCKETS_AVAILABLE:
            logger.warning("⚠️  WebSockets not available, skipping Alpaca stream")
            return None
        
        stream = AlpacaWebSocketStream(api_key, api_secret, base_url)
        self.streams.append(stream)
        return stream
    
    def add_polygon_stream(self, api_key: str, base_url: str = None):
        """Add Polygon WebSocket stream"""
        if not WEBSOCKETS_AVAILABLE:
            logger.warning("⚠️  WebSockets not available, skipping Polygon stream")
            return None
        
        stream = PolygonWebSocketStream(api_key, base_url)
        self.streams.append(stream)
        return stream
    
    async def start(self, symbols: List[str]):
        """Start all streams and subscribe to symbols"""
        self.running = True
        
        for stream in self.streams:
            try:
                await stream.connect()
                await stream.subscribe(symbols)
                
                # Register callback to update price cache
                for symbol in symbols:
                    stream.register_price_callback(symbol, self._update_price_cache)
                
                # Start listening in background
                asyncio.create_task(stream.listen())
            except Exception as e:
                logger.error(f"❌ Failed to start stream: {e}")
    
    def _update_price_cache(self, price_data: Dict):
        """Update price cache with new price data"""
        symbol = price_data['symbol']
        self.price_cache[symbol] = {
            'price': price_data['price'],
            'timestamp': price_data['timestamp'],
            'source': price_data['source']
        }
    
    def get_latest_price(self, symbol: str) -> Optional[float]:
        """Get latest price from cache"""
        if symbol in self.price_cache:
            return self.price_cache[symbol]['price']
        return None
    
    async def stop(self):
        """Stop all streams"""
        self.running = False
        for stream in self.streams:
            try:
                await stream.disconnect()
            except (ConnectionError, RuntimeError, AttributeError, Exception) as e:
                # Ignore errors when stopping streams
                logger.debug(f"Error stopping stream: {e}")
                pass
        logger.info("✅ All WebSocket streams stopped")

