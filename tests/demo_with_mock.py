"""
데모: Mock 데이터로 전체 플로우 시연
네트워크 제약이 있어도 작동하는 완전한 예제
"""

import pandas as pd
from datetime import datetime, timedelta
import random

print("=" * 80)
print("🎬 Momentum Keeper - Mock 데이터 데모")
print("=" * 80)
print("\n📌 이 데모는 네트워크 없이도 전체 시스템이 어떻게 작동하는지 보여줍니다.\n")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Mock 데이터 생성
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def generate_mock_price_data(ticker, start_price, days=60):
    """모의 주가 데이터 생성"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    prices = []
    price = start_price

    for i in range(days):
        # 랜덤 워크 + 약한 추세
        change = random.gauss(0, 0.02)  # 평균 0%, 표준편차 2%
        price = price * (1 + change)
        prices.append(price)

    df = pd.DataFrame({
        'Date': dates,
        'Close': prices,
        'Open': [p * random.uniform(0.98, 1.02) for p in prices],
        'High': [p * random.uniform(1.0, 1.03) for p in prices],
        'Low': [p * random.uniform(0.97, 1.0) for p in prices],
        'Volume': [random.randint(1000000, 5000000) for _ in prices]
    })
    df.set_index('Date', inplace=True)

    # 이동평균선 계산
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()

    return df

def generate_mock_investor_flow(ticker, days=3):
    """모의 수급 데이터 생성"""
    flow_data = []
    for i in range(days):
        date = datetime.now() - timedelta(days=days-i)
        flow_data.append({
            'Date': date.strftime('%Y-%m-%d'),
            'Foreign': random.randint(-100000000, 150000000),  # 외국인
            'Institution': random.randint(-80000000, 120000000),  # 기관
            'Individual': random.randint(-200000000, 100000000)  # 개인
        })

    foreign_sum = sum(d['Foreign'] for d in flow_data)
    institution_sum = sum(d['Institution'] for d in flow_data)

    return {
        'details': flow_data,
        'foreign_sum': foreign_sum,
        'institution_sum': institution_sum
    }

def generate_mock_fundamental(ticker):
    """모의 펀더멘털 데이터 생성"""
    if ticker == '005930':  # 삼성전자
        return {'PER': 12.5, 'PBR': 1.15, 'EPS': 5000, 'BPS': 45000}
    elif ticker == '105560':  # KB금융
        return {'PER': 7.2, 'PBR': 0.55, 'EPS': 8200, 'BPS': 60000}
    elif ticker == '086520':  # 에코프로
        return {'PER': 25.3, 'PBR': 3.2, 'EPS': 1500, 'BPS': 12000}
    else:
        return {'PER': 15.0, 'PBR': 1.5, 'EPS': 1000, 'BPS': 10000}

def generate_mock_macro(ticker):
    """모의 거시지표 생성"""
    if ticker == '005930':  # 삼성전자
        return {
            'indicator': 'SOX Index (Mock)',
            'momentum_30d': random.uniform(-5, 10),
            'status': '상승' if random.random() > 0.3 else '하락'
        }
    elif ticker == '086520':  # 에코프로
        return {
            'indicator': 'Lithium Price Proxy (Mock)',
            'momentum_30d': random.uniform(-10, 15),
            'status': '상승' if random.random() > 0.4 else '하락'
        }
    return None

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 이광수 알고리즘
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def analyze_momentum(ticker, name, price_df, flow_data, fundamental, buy_price):
    """이광수식 추세 분석"""

    current_price = price_df['Close'].iloc[-1]
    ma5 = price_df['MA5'].iloc[-1]
    ma20 = price_df['MA20'].iloc[-1]

    foreign_net = flow_data['foreign_sum']
    institution_net = flow_data['institution_sum']

    # 수익률 계산
    return_rate = (current_price - buy_price) / buy_price * 100

    # 신호 판단
    status = ""
    action = ""
    signal_emoji = ""

    # 1. 손절 원칙 (최우선)
    if return_rate <= -10.0:
        status = "CRITICAL"
        action = "즉시 손절 (원칙 위반)"
        signal_emoji = "🔴"

    # 2. 강한 상승 추세
    elif ma5 > ma20 and foreign_net > 0 and institution_net > 0:
        status = "STRONG BUY"
        action = "강력 홀딩 / 불타기 가능"
        signal_emoji = "🟢"

    # 3. 약한 상승 추세
    elif ma5 > ma20 and (foreign_net > 0 or institution_net > 0):
        status = "BULLISH"
        action = "홀딩 유지"
        signal_emoji = "🟢"

    # 4. 추세 붕괴 경고
    elif current_price < ma20:
        status = "WARNING"
        action = "비중 축소 준비 (20일선 붕괴)"
        signal_emoji = "🟡"

    # 5. 중립
    else:
        status = "NEUTRAL"
        action = "관망"
        signal_emoji = "⚪"

    return {
        'ticker': ticker,
        'name': name,
        'current_price': current_price,
        'buy_price': buy_price,
        'return_rate': return_rate,
        'ma5': ma5,
        'ma20': ma20,
        'trend': 'Bullish' if ma5 > ma20 else 'Bearish',
        'foreign_net': foreign_net,
        'institution_net': institution_net,
        'status': status,
        'action': action,
        'signal_emoji': signal_emoji,
        'pbr': fundamental.get('PBR', 0)
    }

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 포트폴리오 시뮬레이션
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

portfolio = [
    {'ticker': '005930', 'name': '삼성전자', 'buy_price': 70000, 'shares': 10},
    {'ticker': '105560', 'name': 'KB금융', 'buy_price': 65000, 'shares': 5},
    {'ticker': '086520', 'name': '에코프로', 'buy_price': 85000, 'shares': 3},
]

print("\n" + "=" * 80)
print("📊 포트폴리오 분석 시작")
print("=" * 80)

results = []

for stock in portfolio:
    ticker = stock['ticker']
    name = stock['name']
    buy_price = stock['buy_price']

    print(f"\n{'━' * 80}")
    print(f"📈 종목: {name} ({ticker})")
    print('━' * 80)

    # 1. 주가 데이터 수집 (Mock)
    print("  [1/4] 주가 데이터 수집 중...")
    price_df = generate_mock_price_data(ticker, buy_price * 1.05)  # 5% 상승 기대
    print(f"  ✅ 60일 주가 데이터 수집 완료")

    # 2. 수급 데이터 수집 (Mock)
    print("  [2/4] 수급 데이터 수집 중...")
    flow_data = generate_mock_investor_flow(ticker)
    print(f"  ✅ 3일 수급 데이터 수집 완료")

    # 3. 펀더멘털 데이터 (Mock)
    print("  [3/4] 펀더멘털 데이터 수집 중...")
    fundamental = generate_mock_fundamental(ticker)
    print(f"  ✅ PER/PBR 데이터 수집 완료")

    # 4. 거시지표 (Mock)
    print("  [4/4] 거시지표 수집 중...")
    macro = generate_mock_macro(ticker)
    if macro:
        print(f"  ✅ {macro['indicator']} 수집 완료")
    else:
        print(f"  ➖ 거시지표 불필요")

    # 분석 실행
    analysis = analyze_momentum(
        ticker, name, price_df, flow_data, fundamental, buy_price
    )

    results.append(analysis)

    # 결과 출력
    print(f"\n  {analysis['signal_emoji']} 투자 신호: {analysis['status']}")
    print(f"  💰 현재가: {analysis['current_price']:,.0f}원")
    print(f"  📊 평단가: {analysis['buy_price']:,.0f}원")
    print(f"  📈 수익률: {analysis['return_rate']:+.2f}%")
    print(f"  📉 MA5: {analysis['ma5']:,.0f}원 | MA20: {analysis['ma20']:,.0f}원")
    print(f"  🌐 외국인 3일: {analysis['foreign_net']:+,.0f}원")
    print(f"  🏢 기관 3일: {analysis['institution_net']:+,.0f}원")
    print(f"  💡 조언: {analysis['action']}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 포트폴리오 요약
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("\n" + "=" * 80)
print("📊 포트폴리오 요약")
print("=" * 80)

# 테이블 형식 출력
print(f"\n{'종목명':<10} {'현재가':>12} {'수익률':>10} {'추세':>10} {'신호':>8} {'조치':<20}")
print("-" * 80)

total_invested = 0
total_current = 0

for stock, result in zip(portfolio, results):
    invested = stock['buy_price'] * stock['shares']
    current = result['current_price'] * stock['shares']
    total_invested += invested
    total_current += current

    print(f"{result['name']:<10} "
          f"{result['current_price']:>12,.0f}원 "
          f"{result['return_rate']:>+9.2f}% "
          f"{result['trend']:>10} "
          f"{result['signal_emoji']:>8} "
          f"{result['action']:<20}")

# 전체 수익률
total_return = (total_current - total_invested) / total_invested * 100

print("-" * 80)
print(f"{'전체 투자금':<10} {total_invested:>12,.0f}원")
print(f"{'현재 평가액':<10} {total_current:>12,.0f}원")
print(f"{'평가 손익':<10} {total_current - total_invested:>+12,.0f}원 ({total_return:+.2f}%)")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AI 어드바이저 시뮬레이션 (Mock)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("\n" + "=" * 80)
print("🤖 이광수 AI 어드바이저 (Mock)")
print("=" * 80)

print("\n📝 오늘의 투자 조언:\n")

# 손절 대상 확인
critical_stocks = [r for r in results if r['status'] == 'CRITICAL']
if critical_stocks:
    print("🔴 긴급 액션:")
    for stock in critical_stocks:
        print(f"  • {stock['name']}: {stock['return_rate']:+.2f}% - 즉시 손절하세요!")
    print()

# 강한 종목
strong_stocks = [r for r in results if r['status'] == 'STRONG BUY']
if strong_stocks:
    print("🟢 홀딩 유지:")
    for stock in strong_stocks:
        print(f"  • {stock['name']}: 정배열 + 수급 양호 - 강력 홀딩")
    print()

# 경고 종목
warning_stocks = [r for r in results if r['status'] == 'WARNING']
if warning_stocks:
    print("🟡 주의 필요:")
    for stock in warning_stocks:
        print(f"  • {stock['name']}: 20일선 붕괴 - 비중 축소 검토")
    print()

print("\n💬 이광수의 한마디:")
print("   '추세를 거스르지 마세요. 손절은 자존심이 아니라 생존 전략입니다.'")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 최종 요약
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("\n" + "=" * 80)
print("✅ 데모 완료!")
print("=" * 80)

print("\n📌 이 데모에서 확인한 것:")
print("  1. ✅ 주가 데이터 수집 및 이동평균선 계산")
print("  2. ✅ 외국인/기관 수급 데이터 수집")
print("  3. ✅ 펀더멘털 (PBR, PER) 데이터 수집")
print("  4. ✅ 거시지표 프록시 데이터 수집")
print("  5. ✅ 이광수 알고리즘 분석 (MA 크로스, 수급, 손절)")
print("  6. ✅ AI 어드바이저 조언 생성")
print("  7. ✅ 포트폴리오 요약 리포트")

print("\n🚀 다음 단계:")
print("  • 실제 데이터로 교체 (네트워크 연결 시)")
print("  • Streamlit UI로 대시보드 구현")
print("  • 실시간 Gemini AI 연동")

print("\n" + "=" * 80)
