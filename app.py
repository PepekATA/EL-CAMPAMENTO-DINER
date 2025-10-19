"""
🤖 Trading Bot Dashboard
Dashboard principal para monitorear y controlar el bot de trading automático
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from streamlit_autorefresh import st_autorefresh
from utils.api_client import VercelAPIClient
from utils.data_fetcher import AlpacaDataFetcher
from utils.charts import create_price_chart, create_portfolio_chart

# Configuración de la página
st.set_page_config(
    page_title="Trading Bot Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auto-refresh cada 30 segundos
count = st_autorefresh(interval=30000, key="dashboard_refresh")

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
    .metric-card {
        background-color: #262730;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #00ff00;
    }
    .status-active {
        color: #00ff00;
        font-weight: bold;
    }
    .status-inactive {
        color: #ff4444;
        font-weight: bold;
    }
    .trade-profit {
        color: #00ff00;
    }
    .trade-loss {
        color: #ff4444;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar clientes
@st.cache_resource
def init_clients():
    api_client = VercelAPIClient(
        base_url=st.secrets["VERCEL_API_URL"]
    )
    data_fetcher = AlpacaDataFetcher(
        api_key=st.secrets["ALPACA_API_KEY"],
        secret_key=st.secrets["ALPACA_SECRET_KEY"]
    )
    return api_client, data_fetcher

api_client, data_fetcher = init_clients()

# Header
st.markdown('<h1 class="main-header">🤖 Trading Bot Dashboard</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/bot.png", width=100)
    st.title("Control Panel")
    
    # Estado del bot
    st.subheader("🔌 Bot Status")
    try:
        status_response = api_client.get_status()
        if status_response and status_response.get('success'):
            st.markdown('<p class="status-active">● ACTIVE</p>', unsafe_allow_html=True)
            bot_active = True
        else:
            st.markdown('<p class="status-inactive">● INACTIVE</p>', unsafe_allow_html=True)
            bot_active = False
    except:
        st.markdown('<p class="status-inactive">● ERROR</p>', unsafe_allow_html=True)
        bot_active = False
    
    st.divider()
    
    # Controles
    st.subheader("⚡ Quick Actions")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Start Bot", use_container_width=True):
            with st.spinner("Iniciando bot..."):
                result = api_client.start_bot()
                if result.get('success'):
                    st.success("Bot iniciado!")
                else:
                    st.error("Error al iniciar")
    
    with col2:
        if st.button("⏸️ Stop Bot", use_container_width=True):
            with st.spinner("Deteniendo bot..."):
                result = api_client.stop_bot()
                if result.get('success'):
                    st.success("Bot detenido!")
                else:
                    st.error("Error al detener")
    
    if st.button("🔄 Refresh Models", use_container_width=True):
        with st.spinner("Actualizando modelos..."):
            result = api_client.refresh_models()
            if result.get('success'):
                st.success(f"✅ {result['data']['modelsCount']} modelos actualizados")
            else:
                st.error("Error al actualizar modelos")
    
    if st.button("📊 Execute Trade", use_container_width=True):
        with st.spinner("Ejecutando trading..."):
            result = api_client.execute_trade()
            if result.get('success'):
                st.success("Trade ejecutado!")
            else:
                st.error("Error en trading")
    
    st.divider()
    
    # Configuración
    st.subheader("⚙️ Settings")
    auto_trading = st.toggle("Auto Trading", value=True)
    risk_level = st.select_slider(
        "Risk Level",
        options=["Very Low", "Low", "Medium", "High", "Very High"],
        value="Medium"
    )

# Main content
tab1, tab2, tab3 = st.tabs(["📊 Overview", "💼 Portfolio", "📈 Live Trading"])

with tab1:
    # Métricas principales
    st.subheader("📊 Account Metrics")
    
    try:
        account_data = data_fetcher.get_account()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            equity = float(account_data.get('equity', 0))
            st.metric(
                label="💰 Total Equity",
                value=f"${equity:,.2f}",
                delta=f"+{(equity - 10000):,.2f}"
            )
        
        with col2:
            buying_power = float(account_data.get('buying_power', 0))
            st.metric(
                label="💵 Buying Power",
                value=f"${buying_power:,.2f}"
            )
        
        with col3:
            portfolio_value = float(account_data.get('portfolio_value', 0))
            st.metric(
                label="📈 Portfolio Value",
                value=f"${portfolio_value:,.2f}"
            )
        
        with col4:
            daily_pnl = float(account_data.get('daily_pnl', 0))
            pnl_percent = (daily_pnl / equity * 100) if equity > 0 else 0
            st.metric(
                label="📊 Daily P&L",
                value=f"${daily_pnl:,.2f}",
                delta=f"{pnl_percent:+.2f}%"
            )
    
    except Exception as e:
        st.error(f"Error cargando datos de cuenta: {str(e)}")
    
    st.divider()
    
    # Gráfica de rendimiento
    st.subheader("📈 Performance Chart")
    
    try:
        # Obtener historial de equity
        portfolio_history = data_fetcher.get_portfolio_history(period='1M')
        
        if portfolio_history:
            df_history = pd.DataFrame(portfolio_history)
            fig = create_portfolio_chart(df_history)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay suficientes datos históricos aún")
    
    except Exception as e:
        st.error(f"Error cargando gráfica: {str(e)}")
    
    st.divider()
    
    # Estado de modelos ML
    st.subheader("🧠 ML Models Status")
    
    try:
        models_status = api_client.get_model_status()
        
        if models_status.get('success'):
            status_data = models_status['status']
            models_data = models_status.get('models', [])
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Models", status_data.get('totalModels', 0))
            
            with col2:
                last_update = status_data.get('lastUpdate')
                if last_update:
                    update_time = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                    st.metric("Last Update", update_time.strftime("%H:%M"))
                else:
                    st.metric("Last Update", "Never")
            
            with col3:
                needs_refresh = status_data.get('needsRefresh', False)
                refresh_status = "🟡 Needed" if needs_refresh else "🟢 Fresh"
                st.metric("Refresh Status", refresh_status)
            
            # Tabla de modelos
            if models_data:
                st.subheader("Model Details")
                df_models = pd.DataFrame(models_data)
                df_models['performance'] = df_models['performance'].apply(
                    lambda x: f"{float(x)*100:.2f}%" if isinstance(x, (int, float)) else x
                )
                st.dataframe(df_models, use_container_width=True, hide_index=True)
        
        else:
            st.warning("No se pudo cargar el estado de los modelos")
    
    except Exception as e:
        st.error(f"Error cargando modelos: {str(e)}")

with tab2:
    st.subheader("💼 Current Positions")
    
    try:
        positions = data_fetcher.get_positions()
        
        if positions:
            # Crear DataFrame
            positions_data = []
            for pos in positions:
                positions_data.append({
                    'Symbol': pos['symbol'],
                    'Quantity': float(pos['qty']),
                    'Entry Price': f"${float(pos['avg_entry_price']):,.2f}",
                    'Current Price': f"${float(pos['current_price']):,.2f}",
                    'Market Value': f"${float(pos['market_value']):,.2f}",
                    'P&L': f"${float(pos['unrealized_pl']):,.2f}",
                    'P&L %': f"{float(pos['unrealized_plpc'])*100:+.2f}%"
                })
            
            df_positions = pd.DataFrame(positions_data)
            
            # Estilizar DataFrame
            def highlight_pnl(val):
                if isinstance(val, str) and '%' in val:
                    num = float(val.replace('%', '').replace('+', ''))
                    color = 'lightgreen' if num > 0 else 'lightcoral'
                    return f'background-color: {color}'
                return ''
            
            styled_df = df_positions.style.applymap(
                highlight_pnl, 
                subset=['P&L %']
            )
            
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
            
            # Gráfica de distribución
            st.subheader("Portfolio Distribution")
            fig = go.Figure(data=[go.Pie(
                labels=[p['Symbol'] for p in positions_data],
                values=[float(p['Market Value'].replace('$', '').replace(',', '')) for p in positions_data],
                hole=.3
            )])
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("No hay posiciones abiertas actualmente")
    
    except Exception as e:
        st.error(f"Error cargando posiciones: {str(e)}")
    
    st.divider()
    
    # Historial de trades
    st.subheader("📜 Recent Trades")
    
    try:
        orders = data_fetcher.get_recent_orders(limit=10)
        
        if orders:
            orders_data = []
            for order in orders:
                orders_data.append({
                    'Time': datetime.fromisoformat(order['created_at'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M'),
                    'Symbol': order['symbol'],
                    'Side': order['side'].upper(),
                    'Quantity': float(order['qty']),
                    'Price': f"${float(order.get('filled_avg_price', 0)):,.2f}",
                    'Status': order['status'].upper()
                })
            
            df_orders = pd.DataFrame(orders_data)
            
            # Colorear por tipo
            def color_side(val):
                if val == 'BUY':
                    return 'background-color: lightgreen'
                elif val == 'SELL':
                    return 'background-color: lightcoral'
                return ''
            
            styled_orders = df_orders.style.applymap(
                color_side,
                subset=['Side']
            )
            
            st.dataframe(styled_orders, use_container_width=True, hide_index=True)
        else:
            st.info("No hay trades recientes")
    
    except Exception as e:
        st.error(f"Error cargando trades: {str(e)}")

with tab3:
    st.subheader("📈 Live Price Charts")
    
    # Selector de símbolo
    symbols = ['BTC/USD', 'ETH/USD', 'LTC/USD', 'BCH/USD', 'DOGE/USD']
    selected_symbol = st.selectbox("Select Cryptocurrency", symbols)
    
    timeframe = st.select_slider(
        "Timeframe",
        options=["1M", "5M", "15M", "1H", "1D"],
        value="15M"
    )
    
    try:
        # Obtener datos
        bars = data_fetcher.get_crypto_bars(selected_symbol, timeframe, limit=100)
        
        if bars is not None and len(bars) > 0:
            # Crear gráfica de velas
            fig = create_price_chart(bars, selected_symbol, timeframe)
            st.plotly_chart(fig, use_container_width=True)
            
            # Métricas actuales
            current_price = bars['close'].iloc[-1]
            price_change = bars['close'].iloc[-1] - bars['close'].iloc[-2]
            price_change_pct = (price_change / bars['close'].iloc[-2]) * 100
            volume = bars['volume'].iloc[-1]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Current Price", f"${current_price:,.2f}")
            
            with col2:
                st.metric("Change", f"${price_change:+,.2f}", f"{price_change_pct:+.2f}%")
            
            with col3:
                st.metric("High (24h)", f"${bars['high'].max():,.2f}")
            
            with col4:
                st.metric("Low (24h)", f"${bars['low'].min():,.2f}")
        
        else:
            st.warning(f"No se pudieron cargar datos para {selected_symbol}")
    
    except Exception as e:
        st.error(f"Error cargando gráfica: {str(e)}")

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption(f"🕐 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
with col2:
    st.caption(f"🔄 Auto-refresh: {'ON' if count else 'OFF'}")
with col3:
    st.caption("🤖 Powered by Alpaca & Vercel")
