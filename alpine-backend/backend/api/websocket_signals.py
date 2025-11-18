"""
WebSocket endpoint for real-time signal streaming
Streams new signals to connected clients as they arrive
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Set, Any, Optional
from datetime import datetime
import json
import asyncio
import logging
from contextlib import asynccontextmanager

from backend.core.database import get_db
from backend.models.user import User, UserTier
from backend.models.signal import Signal
from backend.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])

# Active WebSocket connections
class ConnectionManager:
    """Manages WebSocket connections and broadcasts signals"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[int, Set[str]] = {}  # user_id -> set of connection_ids
        self.connection_users: Dict[str, int] = {}  # connection_id -> user_id
        self.user_tiers: Dict[int, UserTier] = {}  # user_id -> tier (cached)
        
    async def connect(self, websocket: WebSocket, user: User, connection_id: str):
        """Accept WebSocket connection and store it"""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        
        if user.id not in self.user_connections:
            self.user_connections[user.id] = set()
        self.user_connections[user.id].add(connection_id)
        self.connection_users[connection_id] = user.id
        # Cache user tier
        self.user_tiers[user.id] = user.tier
        
        logger.info(f"WebSocket connected: {connection_id} for user {user.id} ({user.email}, tier: {user.tier.value})")
        
    def disconnect(self, connection_id: str):
        """Remove WebSocket connection"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
            
        user_id = self.connection_users.get(connection_id)
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
                # Remove cached tier if user has no more connections
                if user_id in self.user_tiers:
                    del self.user_tiers[user_id]
                
        if connection_id in self.connection_users:
            del self.connection_users[connection_id]
            
        logger.info(f"WebSocket disconnected: {connection_id}")
        
    async def send_personal_message(self, message: dict, connection_id: str):
        """Send message to specific connection"""
        if connection_id in self.active_connections:
            try:
                await self.active_connections[connection_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to {connection_id}: {e}")
                self.disconnect(connection_id)
                
    async def broadcast_to_user(self, message: dict, user_id: int):
        """Broadcast message to all connections for a user"""
        if user_id in self.user_connections:
            disconnected = []
            for connection_id in self.user_connections[user_id]:
                try:
                    await self.active_connections[connection_id].send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to {connection_id}: {e}")
                    disconnected.append(connection_id)
                    
            # Clean up disconnected connections
            for connection_id in disconnected:
                self.disconnect(connection_id)
                
    async def broadcast_new_signal(self, signal: Signal, db: Session):
        """Broadcast new signal to all users who can access it"""
        # Check if signal is premium
        is_premium = signal.type and signal.type.upper() in ['PREMIUM', 'ELITE']
        
        signal_data = {
            "type": "new_signal",
            "data": {
                "id": signal.id,
                "symbol": signal.symbol,
                "action": signal.action,
                "entry_price": float(signal.entry_price) if signal.entry_price else None,
                "stop_loss": float(signal.stop_loss) if signal.stop_loss else None,
                "take_profit": float(signal.take_profit) if signal.take_profit else None,
                "confidence": float(signal.confidence) if signal.confidence else None,
                "type": signal.type,
                "timestamp": signal.timestamp.isoformat() if signal.timestamp else datetime.utcnow().isoformat(),
                "hash": signal.hash if signal.hash else None,
                "reasoning": signal.reasoning if signal.reasoning else None,
                "server_timestamp": datetime.utcnow().timestamp(),
            }
        }
        
        # Refresh user tiers for users not in cache (new connections)
        missing_user_ids = [
            user_id for user_id in self.user_connections.keys() 
            if user_id not in self.user_tiers
        ]
        
        if missing_user_ids:
            try:
                users = db.query(User).filter(User.id.in_(missing_user_ids)).all()
                for user in users:
                    self.user_tiers[user.id] = user.tier
            except Exception as e:
                logger.warning(f"Error refreshing user tiers: {e}")
        
        # Broadcast to all users who can access this signal
        for user_id, connection_ids in list(self.user_connections.items()):
            # Use cached tier, default to STARTER if not found
            user_tier = self.user_tiers.get(user_id, UserTier.STARTER)
            
            # Check tier access
            if is_premium:
                # Premium signals only for pro and elite tiers
                if user_tier in [UserTier.PRO, UserTier.ELITE]:
                    await self.broadcast_to_user(signal_data, user_id)
            else:
                # Regular signals for all tiers
                await self.broadcast_to_user(signal_data, user_id)
                
    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return len(self.active_connections)
        
    def get_user_connection_count(self, user_id: int) -> int:
        """Get number of connections for a specific user"""
        return len(self.user_connections.get(user_id, set()))


# Global connection manager
manager = ConnectionManager()


async def get_user_from_token(token: str, db: Session) -> Optional[User]:
    """Get user from JWT token"""
    try:
        from backend.core.config import settings
        from jose import jwt
        
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            return None
            
        user = db.query(User).filter(User.id == user_id).first()
        return user
    except Exception as e:
        logger.error(f"Error authenticating WebSocket user: {e}")
        return None


@router.websocket("/ws/signals")
async def websocket_signals_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time signal streaming
    
    Query Parameters:
    - token: JWT authentication token (required)
    
    Messages:
    - Client can send: {"type": "ping"} to keep connection alive
    - Server sends: {"type": "new_signal", "data": {...}} when new signal arrives
    - Server sends: {"type": "pong"} in response to ping
    """
    import uuid
    connection_id = str(uuid.uuid4())
    user = None
    db = None
    
    try:
        # Get database session
        db = next(get_db())
        
        # Authenticate user
        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication required")
            if db:
                db.close()
            return
            
        user = await get_user_from_token(token, db)
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid authentication")
            if db:
                db.close()
            return
            
        # Connect
        await manager.connect(websocket, user, connection_id)
        
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "WebSocket connected successfully",
            "user_tier": user.tier.value,
            "server_timestamp": datetime.utcnow().timestamp()
        })
        
        # Keep connection alive and handle messages
        while True:
            try:
                # Wait for message from client (with timeout for ping/pong)
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                
                try:
                    message = json.loads(data)
                    if message.get("type") == "ping":
                        await websocket.send_json({
                            "type": "pong",
                            "server_timestamp": datetime.utcnow().timestamp()
                        })
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from client {connection_id}: {data}")
                    
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                try:
                    await websocket.send_json({
                        "type": "ping",
                        "server_timestamp": datetime.utcnow().timestamp()
                    })
                except Exception:
                    # Connection likely closed
                    break
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in WebSocket loop for {connection_id}: {e}")
                break
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket error for {connection_id}: {e}")
    finally:
        manager.disconnect(connection_id)
        # Close database session
        if db:
            try:
                db.close()
            except Exception as e:
                logger.error(f"Error closing database session: {e}")


# Function to broadcast new signal (called from signal sync endpoint)
async def broadcast_signal_to_websockets(signal: Signal, db: Session):
    """Broadcast a new signal to all connected WebSocket clients"""
    try:
        await manager.broadcast_new_signal(signal, db)
        logger.info(f"Broadcasted signal {signal.id} to WebSocket clients")
    except Exception as e:
        logger.error(f"Error broadcasting signal to WebSocket clients: {e}", exc_info=True)


@router.get("/ws/stats")
async def websocket_stats():
    """Get WebSocket connection statistics"""
    return {
        "total_connections": manager.get_connection_count(),
        "active_users": len(manager.user_connections),
        "users_by_tier": {
            tier.value: sum(1 for uid in manager.user_connections.keys() 
                          if manager.user_tiers.get(uid) == tier)
            for tier in UserTier
        }
    }

