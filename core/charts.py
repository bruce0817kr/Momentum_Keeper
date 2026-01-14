"""
Plotly 차트 생성 모듈

인터랙티브 주가 차트 (가격 + 이동평균선)
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, Any


def create_price_chart(stock_data: Dict[str, Any], height: int = 400) -> go.Figure:
    """
    주가 + 이동평균선 차트

    Args:
        stock_data: {
            'name': str,
            'ticker': str,
            'price_df': DataFrame (index=날짜, columns=[Close, MA5, MA20]),
            'buy_price': float,
            'current_price': float
        }
        height: 차트 높이

    Returns:
        Plotly Figure
    """
    name = stock_data['name']
    ticker = stock_data['ticker']
    df = stock_data['price_df']
    buy_price = stock_data.get('buy_price', 0)
    current_price = stock_data.get('current_price', 0)

    # Figure 생성
    fig = go.Figure()

    # 1. 종가 (메인 라인)
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Close'],
        name='종가',
        line=dict(color='#1f77b4', width=2),
        hovertemplate='%{y:,.0f}원<extra></extra>'
    ))

    # 2. MA5 (단기 추세)
    if 'MA5' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['MA5'],
            name='MA5',
            line=dict(color='#ff7f0e', width=1.5, dash='dot'),
            hovertemplate='%{y:,.0f}원<extra></extra>'
        ))

    # 3. MA20 (중기 추세)
    if 'MA20' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['MA20'],
            name='MA20',
            line=dict(color='#2ca02c', width=1.5, dash='dash'),
            hovertemplate='%{y:,.0f}원<extra></extra>'
        ))

    # 4. 매수가 (참고선)
    if buy_price > 0:
        fig.add_hline(
            y=buy_price,
            line_dash="dashdot",
            line_color="gray",
            annotation_text=f"매수가: {buy_price:,.0f}원",
            annotation_position="right"
        )

    # 레이아웃
    fig.update_layout(
        title=f"{name} ({ticker}) 주가 차트",
        xaxis_title="날짜",
        yaxis_title="가격 (원)",
        hovermode='x unified',
        height=height,
        template='plotly_white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=10, r=10, t=80, b=10)
    )

    # Y축 포맷 (천 단위 구분)
    fig.update_yaxes(tickformat=",")

    return fig


def create_candlestick_chart(stock_data: Dict[str, Any], height: int = 500) -> go.Figure:
    """
    캔들스틱 + 거래량 차트

    Args:
        stock_data: {
            'name': str,
            'ticker': str,
            'price_df': DataFrame (OHLCV + MA)
        }
        height: 차트 높이

    Returns:
        Plotly Figure
    """
    name = stock_data['name']
    ticker = stock_data['ticker']
    df = stock_data['price_df']

    # 서브플롯 (가격 + 거래량)
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
        subplot_titles=(f"{name} ({ticker})", "거래량")
    )

    # 1. 캔들스틱
    if all(col in df.columns for col in ['Open', 'High', 'Low', 'Close']):
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='가격',
            increasing_line_color='#d62728',
            decreasing_line_color='#1f77b4'
        ), row=1, col=1)

    # 2. MA5
    if 'MA5' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['MA5'],
            name='MA5',
            line=dict(color='#ff7f0e', width=1),
        ), row=1, col=1)

    # 3. MA20
    if 'MA20' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['MA20'],
            name='MA20',
            line=dict(color='#2ca02c', width=1),
        ), row=1, col=1)

    # 4. 거래량
    if 'Volume' in df.columns:
        colors = ['red' if close >= open_price else 'blue'
                  for close, open_price in zip(df['Close'], df['Open'])]

        fig.add_trace(go.Bar(
            x=df.index,
            y=df['Volume'],
            name='거래량',
            marker_color=colors,
            showlegend=False
        ), row=2, col=1)

    # 레이아웃
    fig.update_layout(
        height=height,
        template='plotly_white',
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        margin=dict(l=10, r=10, t=80, b=10)
    )

    fig.update_yaxes(title_text="가격 (원)", row=1, col=1, tickformat=",")
    fig.update_yaxes(title_text="거래량", row=2, col=1, tickformat=",")

    return fig


def create_portfolio_pie_chart(stocks: list, height: int = 400) -> go.Figure:
    """
    포트폴리오 비중 파이 차트

    Args:
        stocks: 종목 리스트 [{name, current_price, shares}, ...]
        height: 차트 높이

    Returns:
        Plotly Figure
    """
    # 평가액 계산
    stocks_with_value = [
        {
            'name': s['name'],
            'value': s['current_price'] * s['shares']
        }
        for s in stocks
    ]

    # 정렬 (큰 순서)
    stocks_with_value.sort(key=lambda x: x['value'], reverse=True)

    names = [s['name'] for s in stocks_with_value]
    values = [s['value'] for s in stocks_with_value]

    fig = go.Figure(data=[go.Pie(
        labels=names,
        values=values,
        hole=0.4,  # 도넛 차트
        textinfo='label+percent',
        textposition='inside',
        hovertemplate='%{label}<br>%{value:,.0f}원<br>(%{percent})<extra></extra>'
    )])

    fig.update_layout(
        title="포트폴리오 비중",
        height=height,
        template='plotly_white',
        margin=dict(l=10, r=10, t=80, b=10)
    )

    return fig


def create_return_bar_chart(stocks: list, height: int = 400) -> go.Figure:
    """
    종목별 수익률 막대 차트

    Args:
        stocks: 종목 리스트 [{name, return_rate, status}, ...]
        height: 차트 높이

    Returns:
        Plotly Figure
    """
    # 수익률 순 정렬
    sorted_stocks = sorted(stocks, key=lambda x: x['return_rate'], reverse=True)

    names = [s['name'] for s in sorted_stocks]
    returns = [s['return_rate'] for s in sorted_stocks]

    # 색상 (수익률에 따라)
    colors = [
        '#d62728' if r >= 10 else  # 빨강 (10% 이상)
        '#ff7f0e' if r >= 5 else   # 주황 (5% 이상)
        '#2ca02c' if r >= 0 else   # 초록 (0% 이상)
        '#1f77b4' if r >= -5 else  # 파랑 (-5% 이상)
        '#8c564b'                   # 갈색 (-5% 미만)
        for r in returns
    ]

    fig = go.Figure(data=[go.Bar(
        x=names,
        y=returns,
        marker_color=colors,
        text=[f"{r:+.2f}%" for r in returns],
        textposition='outside',
        hovertemplate='%{x}<br>%{y:+.2f}%<extra></extra>'
    )])

    # 0% 기준선
    fig.add_hline(y=0, line_dash="dash", line_color="gray")

    fig.update_layout(
        title="종목별 수익률",
        xaxis_title="종목",
        yaxis_title="수익률 (%)",
        height=height,
        template='plotly_white',
        margin=dict(l=10, r=10, t=80, b=40)
    )

    return fig


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 테스트
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    import random
    from datetime import datetime, timedelta

    print("=" * 80)
    print("🧪 Chart Module Test")
    print("=" * 80)

    # Mock 데이터 생성
    dates = pd.date_range(end=datetime.now(), periods=60, freq='D')
    base_price = 70000

    mock_df = pd.DataFrame({
        'Open': [base_price * random.uniform(0.98, 1.02) for _ in range(60)],
        'High': [base_price * random.uniform(1.0, 1.05) for _ in range(60)],
        'Low': [base_price * random.uniform(0.95, 1.0) for _ in range(60)],
        'Close': [base_price * random.uniform(0.98, 1.02) for _ in range(60)],
        'Volume': [random.randint(1000000, 5000000) for _ in range(60)]
    }, index=dates)

    mock_df['MA5'] = mock_df['Close'].rolling(5).mean()
    mock_df['MA20'] = mock_df['Close'].rolling(20).mean()

    stock_data = {
        'name': '삼성전자',
        'ticker': '005930',
        'price_df': mock_df,
        'buy_price': 70000,
        'current_price': mock_df['Close'].iloc[-1]
    }

    # 차트 생성 테스트
    print("\n✅ Creating price chart...")
    fig1 = create_price_chart(stock_data)
    print(f"   Chart created: {type(fig1)}")

    print("\n✅ Creating candlestick chart...")
    fig2 = create_candlestick_chart(stock_data)
    print(f"   Chart created: {type(fig2)}")

    # Mock 포트폴리오
    mock_stocks = [
        {'name': '삼성전자', 'current_price': 75000, 'shares': 10, 'return_rate': 7.14},
        {'name': 'KB금융', 'current_price': 60000, 'shares': 5, 'return_rate': -7.69},
        {'name': '에코프로', 'current_price': 90000, 'shares': 3, 'return_rate': 5.88}
    ]

    print("\n✅ Creating portfolio pie chart...")
    fig3 = create_portfolio_pie_chart(mock_stocks)
    print(f"   Chart created: {type(fig3)}")

    print("\n✅ Creating return bar chart...")
    fig4 = create_return_bar_chart(mock_stocks)
    print(f"   Chart created: {type(fig4)}")

    print("\n✅ All chart tests passed!")
