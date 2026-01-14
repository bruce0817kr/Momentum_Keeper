"""
AI 프롬프트 템플릿

이광수 애널리스트 페르소나
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 이광수 페르소나 시스템 프롬프트
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LEE_GWANGSOO_PERSONA = """
당신은 이광수, 한국의 유명한 주식 애널리스트입니다.

# 투자 철학
1. **추세 추종 (Trend Following)**: 정배열(MA5 > MA20)이 깨지면 즉시 경계하라
2. **손절 원칙 (Cut Losers)**: -10% 도달 시 즉시 손절. 손절은 자존심이 아니라 생존 전략
3. **수급 중시**: 외국인+기관 동반 매수 시 강력 홀딩, 동반 매도 시 경계
4. **집중 투자**: 5종목 이내로 집중도 유지
5. **데이터 기반**: 감정이 아닌 데이터로 판단

# 말투 및 스타일
- 전문적이면서도 냉철한 톤
- 불필요한 미사여구 없이 직설적
- 데이터와 팩트 중심
- 핵심만 간결하게 전달
- 경고할 때는 강하게, 긍정적일 때는 확신을 가지고

# 주의사항
- 절대 감정적인 조언 금지
- 구체적인 수치와 근거 제시
- 손절 대상은 반드시 명시
- 3개 이내의 bullet point로 요약

# 종목별 특화 지식
- 삼성전자: 반도체 수출, DRAM 가격, SOX 지수 언급
- 에코프로: 리튬 가격, 2차전지 업황, 중국 배터리 업체 동향
- KB금융: 금리 환경, 순이자마진(NIM), 대출 성장률
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 포트폴리오 분석 프롬프트
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PORTFOLIO_ANALYSIS_TEMPLATE = """
# 포트폴리오 현황

## 전체 요약
- 총 투자금: {total_invested:,.0f}원
- 현재 평가액: {total_current_value:,.0f}원
- 평가 손익: {total_profit:+,.0f}원 ({total_return_rate:+.2f}%)
- 보유 종목: {total_stocks}개

## 종목별 상세

{stock_details}

## 경고 사항
{warnings}

---

위 포트폴리오를 분석하여 다음 질문에 답하세요:

**질문**: {question}

**답변 형식**:
1. 종합 판단 (한 줄)
2. 긴급 조치 필요 종목 (있을 경우)
3. 핵심 조언 (3개 이내의 bullet point)

반드시 한국어로 답변하고, 이광수 애널리스트의 톤을 유지하세요.
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 개별 종목 분석 프롬프트
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STOCK_ANALYSIS_TEMPLATE = """
# 종목 분석: {name} ({ticker})

## 현재 상황
- 현재가: {current_price:,.0f}원
- 매수가: {buy_price:,.0f}원
- 수익률: {return_rate:+.2f}%
- 보유수량: {shares}주

## 기술적 지표
- MA5: {ma5:,.0f}원
- MA20: {ma20:,.0f}원
- 추세: {trend}
- 정배열 여부: {ma_alignment}

## 수급 현황
- 외국인 3일 순매수: {foreign_net:+,.0f}원
- 기관 3일 순매수: {institution_net:+,.0f}원
- 수급 신호: {supply_signal}

## 현재 신호
- 상태: {status}
- 조언: {action}

---

이 종목에 대해 다음 관점에서 분석하세요:

1. **현재 포지션 유지/청산 판단**
2. **추가 매수 또는 손절 필요성**
3. **업종 전망 (해당되는 경우 거시 지표 언급)**

한국어로 3개 bullet point 이내로 답변하세요.
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 일일 시황 분석 프롬프트
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DAILY_MARKET_TEMPLATE = """
# 오늘의 포트폴리오 점검

## 주요 변화
{major_changes}

## 긴급 조치 필요
{urgent_actions}

## 포트폴리오 건강도
- 전체 수익률: {total_return_rate:+.2f}%
- 손절 대상: {critical_count}종목
- 강한 매수 신호: {strong_buy_count}종목

---

오늘 투자자가 가장 주목해야 할 포인트를 이광수 애널리스트의 관점에서 3가지만 알려주세요.

형식:
**오늘의 핵심 메시지**
1. [첫 번째 조언]
2. [두 번째 조언]
3. [세 번째 조언]
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 프롬프트 생성 헬퍼 함수
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def format_stock_details(stocks: list) -> str:
    """종목 상세 정보를 텍스트로 포맷"""
    details = []

    for i, stock in enumerate(stocks, 1):
        detail = f"""
### {i}. {stock['name']} ({stock['ticker']})
- 현재가: {stock['current_price']:,.0f}원 | 수익률: {stock['return_rate']:+.2f}%
- 추세: {stock['trend']} | MA5: {stock.get('ma5', 0):,.0f}원 / MA20: {stock.get('ma20', 0):,.0f}원
- 수급: 외국인 {stock['foreign_net']:+,.0f}원 / 기관 {stock['institution_net']:+,.0f}원
- 신호: {stock['signal_emoji']} {stock['status']} - {stock['action']}
"""
        details.append(detail.strip())

    return "\n\n".join(details)


def format_warnings(warnings: list) -> str:
    """경고 사항 포맷"""
    if not warnings:
        return "없음"

    return "\n".join(f"- {w}" for w in warnings)


def build_portfolio_prompt(portfolio_result: dict, question: str = "현재 포트폴리오를 종합 분석하고 조언해주세요.") -> str:
    """포트폴리오 분석 프롬프트 생성"""
    stocks = portfolio_result.get('stocks', [])
    portfolio = portfolio_result.get('portfolio', {})

    return PORTFOLIO_ANALYSIS_TEMPLATE.format(
        total_invested=portfolio.get('total_invested', 0),
        total_current_value=portfolio.get('total_current_value', 0),
        total_profit=portfolio.get('total_profit', 0),
        total_return_rate=portfolio.get('total_return_rate', 0),
        total_stocks=portfolio.get('total_stocks', 0),
        stock_details=format_stock_details(stocks),
        warnings=format_warnings(portfolio.get('warnings', [])),
        question=question
    )


def build_stock_prompt(stock: dict) -> str:
    """개별 종목 분석 프롬프트 생성"""
    return STOCK_ANALYSIS_TEMPLATE.format(
        name=stock['name'],
        ticker=stock['ticker'],
        current_price=stock['current_price'],
        buy_price=stock['buy_price'],
        return_rate=stock['return_rate'],
        shares=stock['shares'],
        ma5=stock.get('ma5', 0),
        ma20=stock.get('ma20', 0),
        trend=stock['trend'],
        ma_alignment=stock.get('ma_alignment', 'Unknown'),
        foreign_net=stock['foreign_net'],
        institution_net=stock['institution_net'],
        supply_signal=stock['supply_signal'],
        status=stock['status'],
        action=stock['action']
    )


def build_daily_prompt(portfolio_result: dict) -> str:
    """일일 시황 프롬프트 생성"""
    stocks = portfolio_result.get('stocks', [])
    portfolio = portfolio_result.get('portfolio', {})

    # 주요 변화 (손익 큰 순)
    sorted_by_return = sorted(stocks, key=lambda x: abs(x['return_rate']), reverse=True)
    major_changes = "\n".join([
        f"- {s['name']}: {s['return_rate']:+.2f}% ({s['signal_emoji']} {s['status']})"
        for s in sorted_by_return[:3]
    ])

    # 긴급 조치 필요
    urgent = portfolio.get('urgent_actions', [])
    if urgent:
        urgent_text = "\n".join([
            f"- {s['name']}: {s['action']}"
            for s in urgent
        ])
    else:
        urgent_text = "없음"

    return DAILY_MARKET_TEMPLATE.format(
        major_changes=major_changes,
        urgent_actions=urgent_text,
        total_return_rate=portfolio.get('total_return_rate', 0),
        critical_count=portfolio.get('critical_count', 0),
        strong_buy_count=portfolio.get('strong_buy_count', 0)
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 테스트
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    print("=" * 80)
    print("🧪 Prompt Templates Test")
    print("=" * 80)

    # Mock 데이터
    mock_portfolio = {
        'stocks': [
            {
                'ticker': '005930',
                'name': '삼성전자',
                'current_price': 75000,
                'buy_price': 70000,
                'return_rate': 7.14,
                'shares': 10,
                'ma5': 74000,
                'ma20': 72000,
                'trend': 'Uptrend',
                'ma_alignment': 'Bullish',
                'foreign_net': 100000000,
                'institution_net': 50000000,
                'supply_signal': '🟢 강한 매수',
                'status': 'STRONG_BUY',
                'signal_emoji': '🟢',
                'action': '강력 홀딩'
            }
        ],
        'portfolio': {
            'total_invested': 700000,
            'total_current_value': 750000,
            'total_profit': 50000,
            'total_return_rate': 7.14,
            'total_stocks': 1,
            'critical_count': 0,
            'strong_buy_count': 1,
            'warnings': []
        }
    }

    print("\n📝 Portfolio Analysis Prompt:")
    print("-" * 80)
    prompt = build_portfolio_prompt(mock_portfolio)
    print(prompt[:500] + "...")

    print("\n📝 Stock Analysis Prompt:")
    print("-" * 80)
    stock_prompt = build_stock_prompt(mock_portfolio['stocks'][0])
    print(stock_prompt[:500] + "...")

    print("\n✅ Test completed")
