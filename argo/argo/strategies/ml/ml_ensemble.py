"""ML Ensemble Strategy - Multiple ML Models Combined"""
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from argo.strategies.base_strategy import BaseStrategy, SignalOutput
from datetime import datetime
import joblib
import os

class MLEnsembleStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("MLEnsemble")
        self.models = self._load_or_create_models()
    
    def _load_or_create_models(self):
        """Load pre-trained models or create new ones"""
        models = []
        
        # Random Forest
        rf = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
        models.append(rf)
        
        # Gradient Boosting
        gb = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
        models.append(gb)
        
        # Neural Network
        nn = MLPClassifier(hidden_layer_sizes=(128, 64, 32), max_iter=500, random_state=42)
        models.append(nn)
        
        return models
    
    async def generate_signal(self, symbol: str, market_data: dict):
        """Generate ML-based prediction"""
        try:
            # Extract features
            features = self._extract_features(market_data)
            
            if features is None:
                return None
            
            # Get predictions from all models
            predictions = []
            confidences = []
            
            for model in self.models:
                try:
                    pred = model.predict([features])[0]
                    prob = model.predict_proba([features])[0]
                    
                    predictions.append(pred)
                    confidences.append(max(prob))
                except:
                    continue
            
            if not predictions:
                return None
            
            # Ensemble voting
            avg_prediction = np.mean(predictions)
            avg_confidence = np.mean(confidences)
            
            current_price = market_data.get('current_price', 0)
            
            if avg_prediction > 0.6 and avg_confidence > 0.75:  # Buy signal
                return SignalOutput(
                    symbol=symbol,
                    action='BUY',
                    confidence=avg_confidence,
                    entry_price=current_price,
                    target_price=current_price * 1.04,
                    stop_loss=current_price * 0.98,
                    position_size=0.12,
                    reasoning=f"ML ensemble prediction: {avg_prediction:.2f} (3 models agree)",
                    strategy_name=self.name,
                    timestamp=datetime.utcnow()
                )
            
            elif avg_prediction < 0.4 and avg_confidence > 0.75:  # Sell signal
                return SignalOutput(
                    symbol=symbol,
                    action='SELL',
                    confidence=avg_confidence,
                    entry_price=current_price,
                    target_price=current_price * 0.96,
                    stop_loss=current_price * 1.02,
                    position_size=0.12,
                    reasoning=f"ML ensemble prediction: {avg_prediction:.2f} (3 models agree)",
                    strategy_name=self.name,
                    timestamp=datetime.utcnow()
                )
            
            return None
            
        except Exception as e:
            print(f"ML ensemble error for {symbol}: {e}")
            return None
    
    def _extract_features(self, market_data: dict) -> np.ndarray:
        """Extract ML features from market data"""
        try:
            prices = np.array(market_data.get('close_prices', []))
            volumes = np.array(market_data.get('volumes', []))
            
            if len(prices) < 30:
                return None
            
            features = [
                prices[-1] / prices[-5] - 1,  # 5-day return
                prices[-1] / prices[-10] - 1,  # 10-day return
                prices[-1] / prices[-20] - 1,  # 20-day return
                np.std(prices[-20:]) / np.mean(prices[-20:]),  # Volatility
                volumes[-1] / np.mean(volumes[-20:]),  # Volume ratio
                (prices[-1] - np.min(prices[-20:])) / (np.max(prices[-20:]) - np.min(prices[-20:])),  # Stochastic
            ]
            
            return np.array(features)
            
        except:
            return None
    
    def get_required_data(self) -> list[str]:
        return ['close_prices', 'volumes']
