"""
Cliente para comunicarse con el backend de Vercel
"""

import requests
import streamlit as st
from typing import Dict, Any, Optional

class VercelAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Streamlit-Trading-Dashboard/1.0'
        })
    
    def _make_request(self, endpoint: str, method: str = 'GET', data: Optional[Dict] = None) -> Dict[str, Any]:
        """Hacer petición HTTP al backend"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == 'GET':
                response = self.session.get(url, timeout=30)
            elif method == 'POST':
                response = self.session.post(url, json=data, timeout=30)
            else:
                raise ValueError(f"Método HTTP no soportado: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.Timeout:
            st.error(f"⏱️ Timeout al conectar con {endpoint}")
            return {'success': False, 'error': 'Request timeout'}
        
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Error de conexión: {str(e)}")
            return {'success': False, 'error': str(e)}
        
        except Exception as e:
            st.error(f"❌ Error inesperado: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Obtener estado del bot"""
        return self._make_request('/api/status')
    
    def get_model_status(self) -> Dict[str, Any]:
        """Obtener estado de los modelos ML"""
        return self._make_request('/api/model-status')
    
    def refresh_models(self) -> Dict[str, Any]:
        """Refrescar modelos desde Google Drive"""
        return self._make_request('/api/refresh-models', method='POST')
    
    def execute_trade(self) -> Dict[str, Any]:
        """Ejecutar ciclo de trading"""
        return self._make_request('/api/trade', method='POST')
    
    def start_bot(self) -> Dict[str, Any]:
        """Iniciar bot (endpoint personalizado)"""
        return self._make_request('/api/bot/start', method='POST')
    
    def stop_bot(self) -> Dict[str, Any]:
        """Detener bot (endpoint personalizado)"""
        return self._make_request('/api/bot/stop', method='POST')
