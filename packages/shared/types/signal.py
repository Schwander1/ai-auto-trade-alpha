"""
Shared Pydantic models for trading signals
Used across Argo and Alpine backend for type safety and validation
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Literal

from pydantic import BaseModel, Field, validator


class SignalAction(str, Enum):
    """Trading action types"""
    BUY = "BUY"
    SELL = "SELL"


class SignalType(str, Enum):
    """Signal type based on confidence"""
    PREMIUM = "PREMIUM"  # 95%+ confidence
    STANDARD = "STANDARD"  # 87-94% confidence


class SignalStatus(str, Enum):
    """Signal status"""
    PENDING = "pending"
    ACTIVE = "active"
    CLOSED = "closed"
    EXPIRED = "expired"


class SignalOutcome(str, Enum):
    """Trade outcome"""
    WIN = "win"
    LOSS = "loss"
    EXPIRED = "expired"


class MarketRegime(str, Enum):
    """Market regime types"""
    BULL = "Bull"
    BEAR = "Bear"
    CHOP = "Chop"
    CRISIS = "Crisis"


class Signal(BaseModel):
    """Core trading signal model"""
    id: str = Field(..., description="Unique signal identifier")
    symbol: str = Field(..., description="Trading symbol (e.g., 'AAPL', 'BTC/USD')")
    action: SignalAction = Field(..., description="Trading action: BUY or SELL")
    entry_price: float = Field(..., gt=0, description="Entry price for the signal")
    stop_loss: Optional[float] = Field(None, gt=0, description="Stop loss price")
    take_profit: Optional[float] = Field(None, gt=0, description="Take profit price")
    confidence: float = Field(..., ge=0, le=100, description="Confidence score (0-100%)")
    type: SignalType = Field(..., description="Signal type: PREMIUM or STANDARD")
    timestamp: datetime = Field(..., description="ISO 8601 timestamp when signal was generated")
    hash: str = Field(..., description="SHA-256 cryptographic hash for verification")
    regime: Optional[MarketRegime] = Field(None, description="Market regime when signal was generated")
    regime_strength: Optional[float] = Field(None, ge=0, le=100, description="Regime strength (0-100)")
    status: Optional[SignalStatus] = Field(SignalStatus.PENDING, description="Signal status")
    outcome: Optional[SignalOutcome] = Field(None, description="Trade outcome")
    exit_price: Optional[float] = Field(None, gt=0, description="Exit price (if closed)")
    pnl_pct: Optional[float] = Field(None, description="Profit/loss percentage (if closed)")
    exit_timestamp: Optional[datetime] = Field(None, description="Exit timestamp (if closed)")
    reasoning: Optional[str] = Field(None, description="Reasoning/explanation for the signal")

    @validator('type', pre=True, always=True)
    def determine_type(cls, v, values):
        """Automatically determine signal type from confidence"""
        if 'confidence' in values:
            confidence = values['confidence']
            return SignalType.PREMIUM if confidence >= 95 else SignalType.STANDARD
        return v

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SignalVerification(BaseModel):
    """Signal verification result"""
    isValid: bool = Field(..., description="Whether the signal hash is valid")
    verifiedAt: datetime = Field(default_factory=datetime.utcnow, description="Verification timestamp")
    error: Optional[str] = Field(None, description="Error message if verification failed")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SignalFilters(BaseModel):
    """Signal filter options"""
    limit: Optional[int] = Field(10, ge=1, le=100, description="Maximum number of signals to return")
    premium_only: Optional[bool] = Field(False, description="Only return premium signals (95%+ confidence)")
    symbol: Optional[str] = Field(None, description="Filter by symbol")
    action: Optional[SignalAction] = Field(None, description="Filter by action")
    status: Optional[SignalStatus] = Field(None, description="Filter by status")
    regime: Optional[MarketRegime] = Field(None, description="Filter by market regime")

