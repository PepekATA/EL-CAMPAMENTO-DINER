"""
🤖 Trading Bot Dashboard - Versión Simplificada
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import requests

# Configuración de la página
st.set_page_config(
    page_title="Trading Bot Dashboard",
    page_icon="🤖",
    layout="wide"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #00ff00, #00aaff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🤖 Trading Bot Dashboard</h1>', unsafe_allow_html=True)

# Verificar secrets
if 'VERCEL_API_URL' not in st.secrets:
    st.error("⚠️ Por favor configura los secrets en Streamlit Cloud")
    st.info("""
    Ve a Settings → Secrets y agrega:
```toml
    VERCEL_API_URL = "https://tu-bot.vercel.app"
    ALPACA_API_KEY = "tu_api_key"
    ALPACA_SECRET_KEY = "tu_secret_key"
```
    """)
    st.stop()

# API Client simple
class SimpleAPIClient:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def get(self, endpoint):
        try:
            response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}

# Inicializar cliente
api_client = SimpleAPIClient(st.secrets["VERCEL_API_URL"])

# Sidebar
with st.sidebar:
    st.title("🎛️ Control Panel")
    
    # Estado del bot
    st.subheader("🔌 Bot Status")
    status = api_client.get("/api/status")
    
    if status.get('success'):
        st.success("● ACTIVE")
    else:
        st.error("● INACTIVE")
    
    st.divider()
    
    # Acciones rápidas
    st.subheader("⚡ Quick Actions")
    
    if st.button("🔄 Refresh Models", use_container_width=True):
        with st.spinner("Actualizando..."):
            result = api_client.get("/api/refresh-models")
            if result.get('success'):
                st.success("✅ Actualizado!")
            else:
                st.error("❌ Error")
    
    if st.button("📊 Execute Trade", use_container_width=True):
        with st.spinner("Ejecutando..."):
            result = api_client.get("/api/trade")
            if result.get('success'):
                st.success("✅ Ejecutado!")
            else:
                st.error("❌ Error")

# Main content
tab1, tab2 = st.tabs(["📊 Overview", "🧠 ML Models"])

with tab1:
    st.subheader("📊 Account Status")
    
    # Obtener datos de cuenta desde Alpaca
    try:
        from utils.data_fetcher import AlpacaDataFetcher
        
        fetcher = AlpacaDataFetcher(
            st.secrets["ALPACA_API_KEY"],
            st.secrets["ALPACA_SECRET_KEY"]
        )
        
        account_data = fetcher.get_account()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 Equity", f"${float(account_data['equity']):,.2f}")
        
        with col2:
            st.metric("💵 Buying Power", f"${float(account_data['buying_power']):,.2f}")
        
        with col3:
            st.metric("📈 Portfolio", f"${float(account_data['portfolio_value']):,.2f}")
        
        with col4:
            daily_pnl = float(account_data['daily_pnl'])
            st.metric("📊 Daily P&L", f"${daily_pnl:,.2f}", delta=f"{daily_pnl:+.2f}")
        
        st.divider()
        
        # Posiciones
        st.subheader("💼 Current Positions")
        positions = fetcher.get_positions()
        
        if positions:
            df = pd.DataFrame(positions)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No hay posiciones abiertas")
        
    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Verifica que tus credenciales de Alpaca sean correctas")

with tab2:
    st.subheader("🧠 ML Models Status")
    
    models_status = api_client.get("/api/model-status")
    
    if models_status.get('success'):
        status_data = models_status.get('status', {})
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Models", status_data.get('totalModels', 0))
        
        with col2:
            last_update = status_data.get('lastUpdate', 'Never')
            if last_update != 'Never':
                update_time = datetime.fromisoformat(last_update.replace('Z', ''))
                st.metric("Last Update", update_time.strftime("%H:%M"))
            else:
                st.metric("Last Update", "Never")
        
        with col3:
            needs_refresh = status_data.get('needsRefresh', False)
            status_text = "🟡 Needed" if needs_refresh else "🟢 Fresh"
            st.metric("Status", status_text)
        
        # Modelos
        models = models_status.get('models', [])
        if models:
            st.divider()
            st.subheader("Model Details")
            df_models = pd.DataFrame(models)
            st.dataframe(df_models, use_container_width=True, hide_index=True)
    else:
        st.warning("No se pudo cargar el estado de los modelos")

# Footer
st.divider()
st.caption(f"🕐 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("🤖 Powered by Alpaca & Vercel")
