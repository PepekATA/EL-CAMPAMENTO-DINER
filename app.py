"""
🤖 TRADING BOT DASHBOARD
========================
Dashboard en tiempo real con sincronización automática
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from streamlit_autorefresh import st_autorefresh

# Auto-refresh cada 30 segundos
count = st_autorefresh(interval=30000, key="data_refresh")

# Configuración
st.set_page_config(
    page_title="Trading Bot Live",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
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
        margin-bottom: 1rem;
    }
    .metric-card {
        background: #1e1e1e;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #00ff00;
    }
    .status-active {
        color: #00ff00;
        font-size: 1.2rem;
        font-weight: bold;
    }
    .status-inactive {
        color: #ff0000;
        font-size: 1.2rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🤖 Trading Bot Live Dashboard</h1>', unsafe_allow_html=True)

# Verificar secrets
required_secrets = ['VERCEL_API_URL', 'ALPACA_API_KEY', 'ALPACA_SECRET_KEY']
missing_secrets = [s for s in required_secrets if s not in st.secrets]

if missing_secrets:
    st.error(f"⚠️ Faltan secrets: {', '.join(missing_secrets)}")
    st.info("""
    **Configuración en Streamlit Cloud:**
    1. Ve a tu app en share.streamlit.io
    2. Settings → Secrets
    3. Agrega:
    ```toml
    VERCEL_API_URL = "https://tu-bot.vercel.app"
    ALPACA_API_KEY = "tu_api_key"
    ALPACA_SECRET_KEY = "tu_secret_key"
    ```
    """)
    st.stop()

# ============================================================================
# API CLIENT
# ============================================================================

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
    
    def get(self, endpoint):
        try:
            response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}

api = APIClient(st.secrets["VERCEL_API_URL"])

# ============================================================================
# ALPACA DATA FETCHER
# ============================================================================

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame

@st.cache_data(ttl=60)
def get_alpaca_data():
    """Obtener datos de Alpaca con cache"""
    try:
        client = TradingClient(
            st.secrets["ALPACA_API_KEY"],
            st.secrets["ALPACA_SECRET_KEY"],
            paper=True
        )
        
        account = client.get_account()
        positions = client.get_all_positions()
        
        return {
            'account': {
                'equity': float(account.equity),
                'buying_power': float(account.buying_power),
                'portfolio_value': float(account.portfolio_value),
                'cash': float(account.cash)
            },
            'positions': [
                {
                    'symbol': pos.symbol,
                    'qty': float(pos.qty),
                    'current_price': float(pos.current_price),
                    'market_value': float(pos.market_value),
                    'unrealized_pl': float(pos.unrealized_pl),
                    'unrealized_plpc': float(pos.unrealized_plpc) * 100
                }
                for pos in positions
            ]
        }
    except Exception as e:
        st.error(f"Error conectando con Alpaca: {e}")
        return None

@st.cache_data(ttl=300)
def get_crypto_chart_data(symbol, timeframe='15Min', limit=100):
    """Obtener datos de gráficas"""
    try:
        client = CryptoHistoricalDataClient()
        
        request = CryptoBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Minute if timeframe == '1Min' else TimeFrame(15, 'Minute'),
            limit=limit
        )
        
        bars = client.get_crypto_bars(request)
        df = bars.df.reset_index()
        
        return df
    except Exception as e:
        st.error(f"Error obteniendo datos de {symbol}: {e}")
        return None

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.title("🎛️ Control Panel")
    
    # Status
    st.subheader("🔌 Bot Status")
    status_response = api.get("/api/status")
    
    if status_response.get('success'):
        st.markdown('<p class="status-active">● ONLINE</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="status-inactive">● OFFLINE</p>', unsafe_allow_html=True)
    
    st.divider()
    
    # Quick Actions
    st.subheader("⚡ Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    with col2:
        if st.button("📊 Trade", use_container_width=True):
            with st.spinner("Ejecutando..."):
                result = api.get("/api/trade")
                if result.get('success'):
                    st.success("✅ OK")
                else:
                    st.error("❌ Error")
    
    if st.button("🧠 Update Models", use_container_width=True):
        with st.spinner("Actualizando desde Drive..."):
            result = api.get("/api/refresh-models")
            if result.get('success'):
                st.success("✅ Modelos actualizados")
            else:
                st.error("❌ Error")
    
    st.divider()
    
    # Settings
    st.subheader("⚙️ Settings")
    auto_refresh = st.checkbox("Auto-refresh", value=True)
    show_debug = st.checkbox("Debug info", value=False)

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Obtener datos
alpaca_data = get_alpaca_data()

if alpaca_data:
    account = alpaca_data['account']
    positions = alpaca_data['positions']
    
    # Metrics principales
    st.subheader("💰 Account Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💎 Equity", f"${account['equity']:,.2f}")
    
    with col2:
        st.metric("💵 Buying Power", f"${account['buying_power']:,.2f}")
    
    with col3:
        st.metric("📊 Portfolio", f"${account['portfolio_value']:,.2f}")
    
    with col4:
        total_pl = sum(p['unrealized_pl'] for p in positions)
        st.metric("📈 Unrealized P&L", f"${total_pl:,.2f}", 
                 delta=f"{total_pl:+.2f}")
    
    st.divider()
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Positions", "📈 Charts", "🧠 ML Models", "📋 Activity"])
    
    with tab1:
        st.subheader("💼 Current Positions")
        
        if positions:
            # Crear DataFrame
            df_positions = pd.DataFrame(positions)
            
            # Formatear
            df_positions['qty'] = df_positions['qty'].apply(lambda x: f"{x:.8f}")
            df_positions['current_price'] = df_positions['current_price'].apply(lambda x: f"${x:,.2f}")
            df_positions['market_value'] = df_positions['market_value'].apply(lambda x: f"${x:,.2f}")
            df_positions['unrealized_pl'] = df_positions['unrealized_pl'].apply(lambda x: f"${x:,.2f}")
            df_positions['unrealized_plpc'] = df_positions['unrealized_plpc'].apply(lambda x: f"{x:.2f}%")
            
            # Mostrar tabla
            st.dataframe(
                df_positions,
                use_container_width=True,
                hide_index=True,
                column_config={
                    'symbol': st.column_config.TextColumn('Symbol', width="small"),
                    'qty': st.column_config.TextColumn('Quantity', width="small"),
                    'current_price': st.column_config.TextColumn('Price', width="small"),
                    'market_value': st.column_config.TextColumn('Value', width="small"),
                    'unrealized_pl': st.column_config.TextColumn('P&L', width="small"),
                    'unrealized_plpc': st.column_config.TextColumn('P&L %', width="small")
                }
            )
            
            # Gráfica de distribución
            st.subheader("📊 Portfolio Distribution")
            
            fig = go.Figure(data=[go.Pie(
                labels=[p['symbol'] for p in positions],
                values=[p['market_value'] for p in positions],
                hole=0.4,
                marker_colors=['#00ff00', '#00aaff', '#ff00ff', '#ffaa00', '#ff0000']
            )])
            
            fig.update_layout(
                template='plotly_dark',
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📭 No hay posiciones abiertas")
    
    with tab2:
        st.subheader("📈 Price Charts")
        
        # Selector de símbolo
        symbols = ['BTC/USD', 'ETH/USD', 'LTC/USD', 'BCH/USD', 'DOGE/USD']
        selected_symbol = st.selectbox("Select Symbol", symbols)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            timeframe = st.selectbox("Timeframe", ['1Min', '15Min', '1H'], index=1)
        
        with col2:
            limit = st.number_input("Bars", min_value=50, max_value=500, value=100)
        
        # Obtener datos
        chart_data = get_crypto_chart_data(selected_symbol, timeframe, limit)
        
        if chart_data is not None and not chart_data.empty:
            # Gráfica de velas
            fig = go.Figure(data=[go.Candlestick(
                x=chart_data['timestamp'],
                open=chart_data['open'],
                high=chart_data['high'],
                low=chart_data['low'],
                close=chart_data['close'],
                name=selected_symbol
            )])
            
            # Volumen
            fig.add_trace(go.Bar(
                x=chart_data['timestamp'],
                y=chart_data['volume'],
                name='Volume',
                yaxis='y2',
                opacity=0.3,
                marker_color='rgba(0, 255, 0, 0.3)'
            ))
            
            fig.update_layout(
                title=f'{selected_symbol} - {timeframe}',
                yaxis_title='Price (USD)',
                yaxis2=dict(
                    title='Volume',
                    overlaying='y',
                    side='right'
                ),
                xaxis_rangeslider_visible=False,
                template='plotly_dark',
                height=600,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Stats
            col1, col2, col3, col4 = st.columns(4)
            
            current_price = chart_data['close'].iloc[-1]
            high_24h = chart_data['high'].max()
            low_24h = chart_data['low'].min()
            volume_24h = chart_data['volume'].sum()
            
            with col1:
                st.metric("Current Price", f"${current_price:,.2f}")
            with col2:
                st.metric("24h High", f"${high_24h:,.2f}")
            with col3:
                st.metric("24h Low", f"${low_24h:,.2f}")
            with col4:
                st.metric("24h Volume", f"{volume_24h:,.0f}")
        else:
            st.warning("No se pudieron cargar los datos del gráfico")
    
    with tab3:
        st.subheader("🧠 ML Models Status")
        
        models_response = api.get("/api/model-status")
        
        if models_response.get('success'):
            status = models_response.get('status', {})
            models = models_response.get('models', [])
            
            # Métricas
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Models", status.get('totalModels', 0))
            
            with col2:
                last_update = status.get('lastUpdate')
                if last_update:
                    update_dt = datetime.fromisoformat(last_update.replace('Z', ''))
                    st.metric("Last Update", update_dt.strftime("%H:%M"))
                else:
                    st.metric("Last Update", "Never")
            
            with col3:
                needs_refresh = status.get('needsRefresh', False)
                status_emoji = "🟡 Stale" if needs_refresh else "🟢 Fresh"
                st.metric("Status", status_emoji)
            
            # Tabla de modelos
            if models:
                st.divider()
                df_models = pd.DataFrame(models)
                
                # Ordenar por performance
                df_models = df_models.sort_values('performance', ascending=False)
                
                st.dataframe(
                    df_models,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        'symbol': st.column_config.TextColumn('Symbol', width="small"),
                        'algorithm': st.column_config.TextColumn('Algorithm', width="small"),
                        'performance': st.column_config.NumberColumn('Performance', format="%.4f"),
                        'trainedAt': st.column_config.DatetimeColumn('Trained At', width="medium")
                    }
                )
                
                # Gráfica de performance
                st.subheader("📊 Model Performance")
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=[m['symbol'] for m in models],
                        y=[m['performance'] * 100 for m in models],
                        marker_color=['#00ff00' if m['performance'] > 0 else '#ff0000' for m in models],
                        text=[f"{m['performance']*100:.2f}%" for m in models],
                        textposition='auto'
                    )
                ])
                
                fig.update_layout(
                    title='Performance by Symbol',
                    xaxis_title='Symbol',
                    yaxis_title='Return (%)',
                    template='plotly_dark',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No se pudo cargar el estado de los modelos")
    
    with tab4:
        st.subheader("📋 Recent Activity")
        
        # Aquí mostraremos logs y actividad reciente
        st.info("🚧 Próximamente: historial de trades, logs de ejecución, y estadísticas detalladas")
        
        # Placeholder para actividad
        activity_data = {
            'Timestamp': [
                datetime.now() - timedelta(minutes=5),
                datetime.now() - timedelta(minutes=10),
                datetime.now() - timedelta(minutes=15)
            ],
            'Action': ['BUY', 'SELL', 'UPDATE'],
            'Symbol': ['BTC/USD', 'ETH/USD', 'Models'],
            'Status': ['✅ Success', '✅ Success', '✅ Success']
        }
        
        df_activity = pd.DataFrame(activity_data)
        st.dataframe(df_activity, use_container_width=True, hide_index=True)
    
    # Debug info
    if show_debug:
        st.divider()
        st.subheader("🔧 Debug Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.json(status_response)
        
        with col2:
            st.json(models_response)

else:
    st.error("❌ No se pudo conectar con Alpaca. Verifica tus credenciales.")

# Footer
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.caption(f"🕐 Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

with col2:
    st.caption("🤖 Powered by Alpaca & Vercel")

with col3:
    if auto_refresh:
        st.caption("🔄 Auto-refresh: ON")
    else:
        st.caption("⏸️ Auto-refresh: OFF")
