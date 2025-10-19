"""
Fetcher de datos de Alpaca
"""

import alpaca_trade_api as tradeapi
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class AlpacaDataFetcher:
    def __init__(self, api_key: str, secret_key: str, paper: bool = True):
        self.api = tradeapi.REST(
            api_key,
            secret_key,
            'https://paper-api.alpaca.markets' if paper else 'https://api.alpaca.markets',
            api_version='v2'
        )
    
    def get_account(self) -> Dict:
        """Obtener información de la cuenta"""
        try:
            account = self.api.get_account()
            return {
                'equity': account.equity,
                'buying_power': account.buying_power,
                'portfolio_value': account.portfolio_value,
                'cash': account.cash,
                'daily_pnl': account.equity - account.last_equity if hasattr(account, 'last_equity') else 0
            }
        except Exception as e:
            print(f"Error getting account: {e}")
            return {}
    
    def get_positions(self) -> List[Dict]:
        """Obtener posiciones actuales"""
        try:
            positions = self.api.list_positions()
            return [
                {
                    'symbol': pos.symbol,
                    'qty': pos.qty,
                    'avg_entry_price': pos.avg_entry_price,
                    'current_price': pos.current_price,
                    'market_value': pos.market_value,
                    'unrealized_pl': pos.unrealized_pl,
                    'unrealized_plpc': pos.unrealized_plpc
                }
                for pos in positions
            ]
        except Exception as e:
            print(f"Error getting positions: {e}")
            return []
    
    def get_recent_orders(self, limit: int = 10) -> List[Dict]:
        """Obtener órdenes recientes"""
        try:
            orders = self.api.list_orders(status='all', limit=limit)
            return [
                {
                    'id': order.id,
                    'symbol': order.symbol,
                    'side': order.side,
                    'qty': order.qty,
                    'filled_avg_price': order.filled_avg_price or 0,
                    'status': order.status,
                    'created_at': order.created_at
                }
                for order in orders
            ]
        except Exception as e:
            print(f"Error getting orders: {e}")
            return []
    
    def get_crypto_bars(self, symbol: str, timeframe: str = '15Min', limit: int = 100) -> Optional[pd.DataFrame]:
        """Obtener barras de criptomonedas"""
        try:
            # Mapear timeframe
            tf_map = {
                '1M': tradeapi.TimeFrame.Minute,
                '5M': tradeapi.TimeFrame(5, tradeapi.TimeFrameUnit.Minute),
                '15M': tradeapi.TimeFrame(15, tradeapi.TimeFrameUnit.Minute),
                '1H': tradeapi.TimeFrame.Hour,
                '1D': tradeapi.TimeFrame.Day
            }
            
            tf = tf_map.get(timeframe, tradeapi.TimeFrame(15, tradeapi.TimeFrameUnit.Minute))
            
            bars = self.api.get_crypto_bars(
                symbol,
                tf,
                limit=limit
            ).df
            
            return bars.reset_index()
        
        except Exception as e:
            print(f"Error getting crypto bars: {e}")
            return None
    
    def get_portfolio_history(self, period: str = '1M') -> Optional[List[Dict]]:
        """Obtener historial del portafolio"""
        try:
            # Mapear período
            period_map = {
                '1D': '1D',
                '1W': '1W',
                '1M': '1M',
                '3M': '3M',
                '1A': '1A'
            }
            
            portfolio_history = self.api.get_portfolio_history(
                period=period_map.get(period, '1M'),
                timeframe='1H'
            )
            
            if portfolio_history:
                return [
                    {
                        'timestamp': ts,
                        'equity': eq
                    }
                    for ts, eq in zip(portfolio_history.timestamp, portfolio_history.equity)
                ]
            return None
        
        except Exception as e:
            print(f"Error getting portfolio history: {e}")
            return None
