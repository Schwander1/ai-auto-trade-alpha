"""
WebSocket endpoint for real-time signal streaming
Streams new signals to connected clients as they arrive

PATENT-PENDING TECHNOLOGY
Patent Application: [Application Number]
Filing Date: [Date]

This code implements patent-pending technology.
Unauthorized use may infringe on pending patent rights.

PATENT CLAIM: Real-Time Signal Delivery System
- Sub-500ms signal delivery system
- Real-time signal verification
- WebSocket-based signal distribution
See: docs/SystemDocs/PATENT_PENDING_TECHNOLOGY.md for patent details
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Set, Any, Optional
from datetime import datetime, timezone
import json
import asyncio
import logging
from contextlib import asynccontextmanager

from backend.core.database import get_db, get_session_local
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
        
    def disconnect(self, connection_id: str) -> None:
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
        
    async def send_personal_message(self, message: dict, connection_id: str) -> None:
        """Send message to specific connection"""
        if connection_id in self.active_connections:
            try:
                await self.active_connections[connection_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to {connection_id}: {e}")
                self.disconnect(connection_id)
                
    async def broadcast_to_user(self, message: dict, user_id: int) -> None:
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
                
    async def broadcast_new_signal(self, signal: Signal, db: Optional[Session] = None) -> None:
        """Broadcast new signal to all users who can access it"""
        # Check if signal is premium (confidence >= 85% or 0.85)
        confidence_pct = signal.confidence * 100 if signal.confidence <= 1 else signal.confidence
        is_premium = confidence_pct >= 85
        
        # Handle enum serialization
        action_value = signal.action.value if hasattr(signal.action, 'value') else str(signal.action)
        
        signal_data = {
            "type": "new_signal",
            "data": {
                "id": signal.id,
                "symbol": signal.symbol,
                "action": action_value,
                "entry_price": float(signal.price) if signal.price else None,
                "stop_loss": float(signal.stop_loss) if signal.stop_loss else None,
                "take_profit": float(signal.target_price) if signal.target_price else None,
                "confidence": confidence_pct,  # Convert to 0-100 range for API
                "type": "PREMIUM" if is_premium else "STANDARD",
                "timestamp": signal.created_at.isoformat() if signal.created_at else datetime.now(timezone.utc).isoformat(),
                "hash": signal.verification_hash if signal.verification_hash else None,
                "reasoning": signal.rationale if signal.rationale else None,
                "server_timestamp": datetime.now(timezone.utc).timestamp(),
            }
        }
        
        # Refresh user tiers for users not in cache (new connections)
        missing_user_ids = [
            user_id for user_id in self.user_connections
            if user_id not in self.user_tiers
        ]
        
        if missing_user_ids and db is not None:
            try:
                # OPTIMIZATION: Use batch query for large user lists to avoid large IN clauses
                from backend.core.query_optimizer import batch_query_by_ids
                users = batch_query_by_ids(db, User, missing_user_ids, batch_size=100)
                for user in users:
                    self.user_tiers[user.id] = user.tier
            except Exception as e:
                logger.warning(f"Error refreshing user tiers: {e}")
        elif missing_user_ids:
            # If no db session provided, default missing users to STARTER tier
            logger.debug(f"Missing user tiers for {len(missing_user_ids)} users, defaulting to STARTER (no db session)")
        
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
        from jose import jwt, JWTError
        
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        # JWT token uses email as "sub" field (consistent with auth.py)
        email = payload.get("sub")
        if email is None:
            return None
            
        user = db.query(User).filter(User.email == email).first()
        return user
    except JWTError as e:
        logger.error(f"JWT error authenticating WebSocket user: {e}")
        return None
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
    
    # Get database session (WebSocket endpoints can't use Depends, so create session directly)
    SessionLocal = get_session_local()
    db = SessionLocal()
    
    try:
        # Authenticate user
        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication required")
            return
            
        user = await get_user_from_token(token, db)
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid authentication")
            return
        
        # Close database session after authentication (we don't need it for the WebSocket connection)
        db.close()
        db = None
        
        # Connect
        await manager.connect(websocket, user, connection_id)
        
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "WebSocket connected successfully",
            "user_tier": user.tier.value,
            "server_timestamp": datetime.now(timezone.utc).timestamp()
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
                            "server_timestamp": datetime.now(timezone.utc).timestamp()
                        })
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from client {connection_id}: {data}")
                    
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                try:
                    await websocket.send_json({
                        "type": "ping",
                        "server_timestamp": datetime.now(timezone.utc).timestamp()
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
        logger.error(f"Error in WebSocket authentication/setup: {e}")
        if db:
            try:
                db.rollback()
            except Exception:
                pass
    finally:
        # Close database session if still open
        if db:
            try:
                db.close()
            except Exception as e:
                logger.error(f"Error closing database session: {e}")
        manager.disconnect(connection_id)


# Function to broadcast new signal (called from signal sync endpoint)
async def broadcast_signal_to_websockets(signal: Signal, db: Session) -> None:
    """Broadcast a new signal to all connected WebSocket clients"""
    try:
        await manager.broadcast_new_signal(signal, db)
        logger.info(f"Broadcasted signal {signal.id} to WebSocket clients")
    except Exception as e:
        logger.error(f"Error broadcasting signal to WebSocket clients: {e}", exc_info=True)


@router.get("/ws/stats")
async def websocket_stats() -> Dict[str, Any]:
    """Get WebSocket connection statistics"""
    return {
        "total_connections": manager.get_connection_count(),
        "active_users": len(manager.user_connections),
        "users_by_tier": {
            tier.value: sum(1 for uid in manager.user_connections 
                          if manager.user_tiers.get(uid) == tier)
            for tier in UserTier
        }
    }

