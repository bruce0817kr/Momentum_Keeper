"""
Momentum Keeper - Streamlit Dashboard (Phase 3)

이광수식 투자 전략 자동화 대시보드
+ Gemini AI 어드바이저
+ Plotly 인터랙티브 차트
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(str(Path(__file__).parent))

from core.portfolio import PortfolioManager
from core.charts import (
    create_price_chart,
    create_candlestick_chart,
    create_portfolio_pie_chart,
    create_return_bar_chart
)
from ai.advisor import AIAdvisor

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 페이지 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.set_page_config(
    page_title="Momentum Keeper",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 커스터마이징
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .ai-advice {
        background-color: #e8f5e9;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #4caf50;
    }
    .critical-box {
        background-color: #ffebee;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #f44336;
    }
</style>
""", unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 세션 상태 초기화
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if 'portfolio_manager' not in st.session_state:
    st.session_state.portfolio_manager = PortfolioManager()
if 'ai_advisor' not in st.session_state:
    st.session_state.ai_advisor = AIAdvisor()
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'last_update_time' not in st.session_state:
    st.session_state.last_update_time = None
if 'show_charts' not in st.session_state:
    st.session_state.show_charts = True
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = None

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 헤더
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.title("📈 Momentum Keeper")
st.markdown("**이광수식 추세 추종 투자 전략 자동화** | Powered by Gemini AI")
st.markdown("---")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 사이드바
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

with st.sidebar:
    st.header("🎛️ 제어 패널")

    # 새로고침 버튼
    if st.button("🔄 데이터 새로고침", use_container_width=True, type="primary"):
        with st.spinner("데이터 수집 및 분석 중..."):
            st.session_state.analysis_result = st.session_state.portfolio_manager.analyze_all()
            st.session_state.last_update_time = datetime.now()
        st.success("✅ 업데이트 완료!")
        st.rerun()

    # 마지막 업데이트 시간
    if st.session_state.last_update_time:
        st.caption(f"마지막 업데이트: {st.session_state.last_update_time.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        st.caption("아직 분석하지 않았습니다.")

    st.markdown("---")

    # 포트폴리오 정보
    st.subheader("📂 포트폴리오 정보")
    portfolio_data = st.session_state.portfolio_manager.portfolio_data
    st.write(f"**소유자**: {portfolio_data.get('owner', 'Unknown')}")
    st.write(f"**종목 수**: {st.session_state.portfolio_manager.get_stock_count()}")

    st.markdown("---")

    # 표시 옵션
    st.subheader("⚙️ 표시 옵션")
    st.session_state.show_charts = st.checkbox("차트 표시", value=True)
    show_ai = st.checkbox("AI 조언 표시", value=True)

    st.markdown("---")

    # AI 상태
    st.subheader("🤖 AI 상태")
    if st.session_state.ai_advisor.gemini_available:
        st.success("✅ Gemini AI 연결됨")
    else:
        st.warning("⚠️ Gemini API 키 필요")
        st.caption("Fallback 모드로 작동 중")

    st.markdown("---")

    # 정보
    st.caption("**Momentum Keeper v2.0 (Phase 3)**")
    st.caption("이광수 애널리스트의 투자 철학")
    st.caption("추세 추종 + 손절 원칙 + AI")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 메인 컨텐츠
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 초기 분석 실행 (최초 1회)
if st.session_state.analysis_result is None:
    with st.spinner("포트폴리오 분석 중..."):
        st.session_state.analysis_result = st.session_state.portfolio_manager.analyze_all()
        st.session_state.last_update_time = datetime.now()

result = st.session_state.analysis_result

# 분석 결과가 없으면 경고
if not result or not result['stocks']:
    st.warning("⚠️ 포트폴리오가 비어있습니다. `data/portfolio.json`에 종목을 추가해주세요.")
    st.stop()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. 포트폴리오 요약 (KPI)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

portfolio = result['portfolio']

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="총 투자금",
        value=f"{portfolio['total_invested']:,.0f}원"
    )

with col2:
    st.metric(
        label="현재 평가액",
        value=f"{portfolio['total_current_value']:,.0f}원",
        delta=f"{portfolio['total_profit']:+,.0f}원"
    )

with col3:
    return_color = "normal" if portfolio['total_return_rate'] >= 0 else "inverse"
    st.metric(
        label="수익률",
        value=f"{portfolio['total_return_rate']:+.2f}%",
        delta_color=return_color
    )

with col4:
    st.metric(
        label="보유 종목",
        value=f"{portfolio['total_stocks']}개"
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. AI 일일 조언 (Phase 3)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if show_ai:
    st.markdown("---")
    st.subheader("🤖 이광수 AI 어드바이저")

    with st.expander("📅 오늘의 조언", expanded=True):
        with st.spinner("AI 분석 중..."):
            daily_advice = st.session_state.ai_advisor.generate_daily_insight(result)

        st.markdown(f'<div class="ai-advice">{daily_advice}</div>', unsafe_allow_html=True)

# 경고 메시지
if portfolio['warnings']:
    st.markdown("---")
    for warning in portfolio['warnings']:
        if '🔴' in warning:
            st.markdown(f'<div class="critical-box">⚠️ {warning}</div>', unsafe_allow_html=True)
        else:
            st.warning(warning)

st.markdown("---")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. 포트폴리오 차트 (Phase 3)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if st.session_state.show_charts:
    st.subheader("📊 포트폴리오 차트")

    col1, col2 = st.columns(2)

    with col1:
        # 비중 차트
        fig_pie = create_portfolio_pie_chart(result['stocks'])
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # 수익률 차트
        fig_bar = create_return_bar_chart(result['stocks'])
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. 종목별 상세 분석
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.subheader("📊 종목별 상세 분석")

# 우선순위별 정렬
sorted_stocks = sorted(result['stocks'], key=lambda x: x.get('priority', 99))

# 탭으로 종목 구분
tab_names = [f"{s['signal_emoji']} {s['name']}" for s in sorted_stocks]
tabs = st.tabs(tab_names)

for tab, stock in zip(tabs, sorted_stocks):
    with tab:
        # 신호에 따라 배경색 설정
        if stock['status'] == 'CRITICAL':
            st.error(f"🔴 **{stock['status']}**: {stock['action']}")
        elif stock['status'] == 'WARNING':
            st.warning(f"🟡 **{stock['status']}**: {stock['action']}")
        elif stock['status'] == 'STRONG_BUY':
            st.success(f"🟢 **{stock['status']}**: {stock['action']}")
        else:
            st.info(f"⚪ **{stock['status']}**: {stock['action']}")

        # 주요 지표
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("현재가", f"{stock['current_price']:,.0f}원")

        with col2:
            profit_color = "normal" if stock['return_rate'] >= 0 else "inverse"
            st.metric(
                "수익률",
                f"{stock['return_rate']:+.2f}%",
                delta=f"{stock['profit']:+,.0f}원",
                delta_color=profit_color
            )

        with col3:
            st.metric("매수가", f"{stock['buy_price']:,.0f}원")

        with col4:
            st.metric("보유수량", f"{stock['shares']}주")

        # 기술적 분석 + 수급
        col1, col2 = st.columns(2)

        with col1:
            st.write("**📉 기술적 지표**")
            st.write(f"MA5: {stock.get('ma5', 0):,.0f}원" if stock.get('ma5') else "MA5: N/A")
            st.write(f"MA20: {stock.get('ma20', 0):,.0f}원" if stock.get('ma20') else "MA20: N/A")
            st.write(f"추세: {stock['trend']}")

        with col2:
            st.write("**💰 수급 현황**")
            st.write(f"외국인: {stock['foreign_net']:+,.0f}원")
            st.write(f"기관: {stock['institution_net']:+,.0f}원")
            st.write(f"신호: {stock['supply_signal']}")

        # AI 개별 종목 조언 (Phase 3)
        if show_ai:
            with st.expander("🤖 AI 종목 분석"):
                with st.spinner(f"{stock['name']} AI 분석 중..."):
                    stock_advice = st.session_state.ai_advisor.analyze_stock(stock)
                st.markdown(stock_advice)

        # 주가 차트 (Phase 3)
        if st.session_state.show_charts:
            st.markdown("---")
            st.write("**📈 주가 차트**")

            # 데이터 수집에서 price_df 가져오기
            collector = st.session_state.portfolio_manager.collector
            price_result = collector.get_stock_price(stock['ticker'], days=60)

            if not price_result['data'].empty:
                chart_data = {
                    'name': stock['name'],
                    'ticker': stock['ticker'],
                    'price_df': price_result['data'],
                    'buy_price': stock['buy_price'],
                    'current_price': stock['current_price']
                }

                # 차트 타입 선택
                chart_type = st.radio(
                    "차트 타입",
                    ["간단 차트", "캔들스틱 + 거래량"],
                    horizontal=True,
                    key=f"chart_{stock['ticker']}"
                )

                if chart_type == "간단 차트":
                    fig = create_price_chart(chart_data, height=400)
                else:
                    fig = create_candlestick_chart(chart_data, height=500)

                st.plotly_chart(fig, use_container_width=True)

                # 데이터 소스 표시
                st.caption(f"데이터 소스: {price_result['source']}")
                if price_result['message']:
                    st.caption(f"{price_result['message']}")
            else:
                st.warning("차트 데이터를 불러올 수 없습니다.")

        # 경고
        if stock['warnings']:
            st.markdown("---")
            for warning in stock['warnings']:
                st.warning(warning)

st.markdown("---")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. 데이터 수집 상태
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

with st.expander("🔍 데이터 수집 상태 확인"):
    data_status = result.get('data_status', [])

    if data_status:
        df_status = pd.DataFrame(data_status)
        df_status = df_status[['ticker', 'type', 'source', 'level', 'message']]
        df_status.columns = ['종목', '데이터 타입', '소스', '레벨', '메시지']

        st.dataframe(df_status, use_container_width=True)
    else:
        st.info("데이터 상태 정보가 없습니다.")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. 이광수의 투자 철학
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

with st.expander("💡 이광수의 투자 철학"):
    st.markdown("""
    ### 5대 투자 원칙

    1. **추세를 거스르지 마라**
       - 정배열(MA5 > MA20)이 깨지면 경계하라
       - 20일선 붕괴 시 비중 축소 준비

    2. **손절은 자존심이 아니라 생존**
       - -10% 도달 시 즉시 손절
       - 손실을 키우는 것이 가장 위험하다

    3. **수급이 모든 것을 말해준다**
       - 외국인+기관 동반 매수 시 강력 홀딩
       - 동반 매도 시 경계 태세

    4. **집중 투자**
       - 5종목 이내로 집중도 유지
       - 확신 없는 종목은 담지 마라

    5. **데이터가 답이다**
       - 감정이 아닌 데이터로 판단
       - 뉴스가 아닌 차트와 수급을 보라

    ---

    _"시장은 항상 옳습니다. 시장을 이기려 하지 말고, 시장을 따르세요."_ - 이광수
    """)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 푸터
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.markdown("---")
st.caption("""
**Momentum Keeper v2.0 (Phase 3)** |
Made with ❤️ by Momentum Keeper Team |
Powered by Gemini AI & Plotly |
Data sources: FinanceDataReader, pykrx, Naver Finance
""")
