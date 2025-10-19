"""
Generador de gráficas con Plotly
"""

import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

def create_price_chart(df: pd.DataFrame, symbol: str, timeframe: str) -> go.Figure:
    """Crear gráfica de velas japonesas"""
    
    fig = go.Figure(data=[go.Candlestick(
        x=df['timestamp'] if 'timestamp' in df.columns else df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name=symbol
    )])
    
    # Agregar volumen
    fig.add_trace(go.Bar(
        x=df['timestamp'] if 'timestamp' in df.columns else df.index,
        y=df['volume'],
        name='Volume',
        yaxis='y2',
        opacity=0.3,
        marker_color='rgba(100, 150, 255, 0.5)'
    ))
    
    # Layout
    fig.update_layout(
        title=f'{symbol} - {timeframe}',
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
    
    return fig

def create_portfolio_chart(df: pd.DataFrame) -> go.Figure:
    """Crear gráfica de rendimiento del portafolio"""
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['equity'],
        mode='lines',
        name='Portfolio Value',
        line=dict(color='#00ff00', width=2),
        fill='tozeroy',
        fillcolor='rgba(0, 255, 0, 0.1)'
    ))
    
    # Línea base de capital inicial
    initial_capital = df['equity'].iloc[0]
    fig.add_hline(
        y=initial_capital,
        line_dash="dash",
        line_color="gray",
        annotation_text="Initial Capital"
    )
    
    fig.update_layout(
        title='Portfolio Performance',
        xaxis_title='Date',
        yaxis_title='Equity (USD)',
        template='plotly_dark',
        height=400,
        hovermode='x unified'
    )
    
    return fig
