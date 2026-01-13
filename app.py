"""
Momentum Keeper - Streamlit Dashboard

이광수식 투자 전략 자동화 대시보드
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(str(Path(__file__).parent))

from core.portfolio import PortfolioManager

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 페이지 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.set_page_config(
    page_title="Momentum Keeper",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 세션 상태 초기화
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if 'portfolio_manager' not in st.session_state:
    st.session_state.portfolio_manager = PortfolioManager()
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'last_update_time' not in st.session_state:
    st.session_state.last_update_time = None

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 헤더
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.title("📈 Momentum Keeper")
st.markdown("**이광수식 추세 추종 투자 전략 자동화**")
st.markdown("---")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 사이드바
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

with st.sidebar:
    st.header("🎛️ 제어 패널")

    # 새로고침 버튼
    if st.button("🔄 데이터 새로고침", use_container_width=True):
        with st.spinner("데이터 수집 및 분석 중..."):
            st.session_state.analysis_result = st.session_state.portfolio_manager.analyze_all()
            st.session_state.last_update_time = datetime.now()
        st.success("✅ 업데이트 완료!")
        st.rerun()

    # 마지막 업데이트 시간
    if st.session_state.last_update_time:
        st.caption(f"마지막 업데이트: {st.session_state.last_update_time.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        st.caption("아직 분석하지 않았습니다. 새로고침 버튼을 누르세요.")

    st.markdown("---")

    # 포트폴리오 정보
    st.subheader("📂 포트폴리오 정보")
    portfolio_data = st.session_state.portfolio_manager.portfolio_data
    st.write(f"**소유자**: {portfolio_data.get('owner', 'Unknown')}")
    st.write(f"**종목 수**: {st.session_state.portfolio_manager.get_stock_count()}")

    st.markdown("---")

    # 설정
    st.subheader("⚙️ 설정")
    settings = st.session_state.portfolio_manager.get_settings()
    st.write(f"손절 기준: {settings.get('stop_loss_percent', -10.0)}%")
    st.write(f"최대 보유: {settings.get('max_holdings', 5)}종목")

    st.markdown("---")

    # 정보
    st.caption("**Momentum Keeper v1.0**")
    st.caption("이광수 애널리스트의 투자 철학")
    st.caption("추세 추종 + 손절 원칙")

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

# 경고 메시지
if portfolio['warnings']:
    st.markdown("---")
    st.error("⚠️ **포트폴리오 경고**")
    for warning in portfolio['warnings']:
        st.write(f"- {warning}")

st.markdown("---")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. 종목별 상세 분석
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.subheader("📊 종목별 분석")

# 우선순위별 정렬 (CRITICAL > WARNING > STRONG_BUY > BULLISH > NEUTRAL)
sorted_stocks = sorted(result['stocks'], key=lambda x: x.get('priority', 99))

for stock in sorted_stocks:
    # 신호에 따라 배경색 설정
    if stock['status'] == 'CRITICAL':
        background = "background-color: #ffebee;"  # 빨강 배경
    elif stock['status'] == 'WARNING':
        background = "background-color: #fff9c4;"  # 노랑 배경
    elif stock['status'] == 'STRONG_BUY':
        background = "background-color: #e8f5e9;"  # 초록 배경
    else:
        background = ""

    with st.container():
        st.markdown(f"<div style='{background} padding: 15px; border-radius: 5px; margin-bottom: 10px;'>",
                    unsafe_allow_html=True)

        # 종목명 + 신호
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"### {stock['signal_emoji']} {stock['name']} ({stock['ticker']})")

        with col2:
            st.markdown(f"**{stock['status']}**")

        # 주요 지표 (3열)
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("현재가", f"{stock['current_price']:,.0f}원")
            st.caption(f"매수가: {stock['buy_price']:,.0f}원")

        with col2:
            profit_color = "normal" if stock['return_rate'] >= 0 else "inverse"
            st.metric(
                "수익률",
                f"{stock['return_rate']:+.2f}%",
                delta=f"{stock['profit']:+,.0f}원",
                delta_color=profit_color
            )

        with col3:
            st.metric("보유수량", f"{stock['shares']}주")
            st.caption(f"평가액: {stock['current_price'] * stock['shares']:,.0f}원")

        # 기술적 분석 (2열)
        col1, col2 = st.columns(2)

        with col1:
            st.write("**📉 기술적 지표**")
            st.write(f"MA5: {stock['ma5']:,.0f}원" if stock['ma5'] else "MA5: N/A")
            st.write(f"MA20: {stock['ma20']:,.0f}원" if stock['ma20'] else "MA20: N/A")
            st.write(f"추세: {stock['trend']}")

        with col2:
            st.write("**💰 수급 현황**")
            st.write(f"외국인: {stock['foreign_net']:+,.0f}원")
            st.write(f"기관: {stock['institution_net']:+,.0f}원")
            st.write(f"신호: {stock['supply_signal']}")

        # 투자 조언 (강조)
        st.markdown("---")
        st.markdown(f"**💡 투자 조언:** {stock['action']}")

        # 경고
        if stock['warnings']:
            st.warning("⚠️ " + " | ".join(stock['warnings']))

        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. 데이터 수집 상태
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

with st.expander("🔍 데이터 수집 상태 확인"):
    st.write("각 데이터 소스의 상태를 확인할 수 있습니다.")

    data_status = result.get('data_status', [])

    if data_status:
        df_status = pd.DataFrame(data_status)
        df_status = df_status[['ticker', 'type', 'source', 'level', 'message']]

        # 컬럼 이름 한글화
        df_status.columns = ['종목', '데이터 타입', '소스', '레벨', '메시지']

        st.dataframe(df_status, use_container_width=True)
    else:
        st.info("데이터 상태 정보가 없습니다.")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. 이광수의 조언 (AI 섹션 - 향후 구현)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.markdown("---")
st.subheader("🤖 이광수 AI 어드바이저")

st.info("""
**이광수의 투자 철학**

1. **추세를 거스르지 마라** - 정배열(MA5 > MA20)이 깨지면 경계하라
2. **손절은 자존심이 아니라 생존** - -10% 도달 시 즉시 손절
3. **수급이 모든 것을 말해준다** - 외국인+기관 동반 매수 시 강력 홀딩
4. **집중 투자** - 5종목 이내로 집중도 유지
5. **데이터가 답이다** - 감정이 아닌 데이터로 판단

_"시장은 항상 옳습니다. 시장을 이기려 하지 말고, 시장을 따르세요."_
""")

# AI 분석 (Gemini 연동 예정)
st.caption("🚧 Gemini AI 연동은 Phase 3에서 구현 예정입니다.")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 푸터
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.markdown("---")
st.caption("""
**Momentum Keeper v1.0** |
Made with ❤️ by Momentum Keeper Team |
Data sources: FinanceDataReader, pykrx, Naver Finance
""")
