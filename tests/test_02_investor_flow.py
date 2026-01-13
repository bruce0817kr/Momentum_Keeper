"""
테스트 2: 외국인/기관 수급 데이터
목표: pykrx로 투자자별 거래 데이터 수집
"""

from datetime import datetime, timedelta

print("=" * 80)
print("💰 TEST 2: 외국인/기관 수급 데이터 테스트")
print("=" * 80)

# 테스트 종목
TEST_TICKERS = {
    '005930': '삼성전자',
    '105560': 'KB금융',
    '086520': '에코프로'
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# pykrx로 투자자별 거래 데이터 수집
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

try:
    from pykrx import stock

    print("\n[pykrx 투자자별 거래 데이터]")
    print("-" * 80)

    for ticker, name in TEST_TICKERS.items():
        print(f"\n종목: {name} ({ticker})")

        # 최근 5일 데이터 (3일 연속 매수 확인용)
        end = datetime.now().strftime('%Y%m%d')
        start = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')

        # 방법 1: 투자자별 순매수 (더 간단)
        try:
            df = stock.get_market_trading_value_by_date(
                start, end, ticker, detail=True
            )

            if df.empty:
                print(f"  ❌ 데이터 없음")
                continue

            # 최근 3일 데이터만 추출
            df_recent = df.tail(3)

            print(f"\n  📅 최근 3일 거래 현황:")
            print(f"  {'날짜':<12} {'외국인':>15} {'기관':>15} {'개인':>15}")
            print("  " + "-" * 60)

            foreign_sum = 0
            institution_sum = 0

            for date, row in df_recent.iterrows():
                foreign_val = row.get('외국인', 0)
                institution_val = row.get('기관', 0)
                individual_val = row.get('개인', 0)

                foreign_sum += foreign_val
                institution_sum += institution_val

                print(f"  {date.strftime('%Y-%m-%d'):<12} "
                      f"{foreign_val:>+14,.0f}원 "
                      f"{institution_val:>+14,.0f}원 "
                      f"{individual_val:>+14,.0f}원")

            print("\n  📊 3일 누적 순매수:")
            print(f"  • 외국인: {foreign_sum:>+15,.0f}원 {'✅ 매수' if foreign_sum > 0 else '❌ 매도'}")
            print(f"  • 기관:   {institution_sum:>+15,.0f}원 {'✅ 매수' if institution_sum > 0 else '❌ 매도'}")

            # 판단 로직
            if foreign_sum > 0 and institution_sum > 0:
                signal = "🟢 강한 매수 (외국인+기관 동반 매수)"
            elif foreign_sum > 0:
                signal = "🟡 중립적 매수 (외국인 매수, 기관 매도)"
            elif institution_sum > 0:
                signal = "🟡 중립적 매수 (기관 매수, 외국인 매도)"
            else:
                signal = "🔴 약한 신호 (외국인+기관 동반 매도)"

            print(f"\n  💡 수급 신호: {signal}")
            print(f"  ✅ 수급 데이터 수집 성공")

        except Exception as e:
            print(f"  ❌ 오류: {e}")

    print("\n" + "=" * 80)
    print("✅ pykrx 투자자별 데이터 테스트 완료")
    print("=" * 80)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 추가 분석: 전체 시장 수급 (참고용)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    print("\n" + "=" * 80)
    print("📊 [보너스] 전체 시장 수급 현황 (KOSPI)")
    print("-" * 80)

    try:
        # 어제 날짜로 조회 (당일은 데이터 없을 수 있음)
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')

        # KOSPI 전체 수급
        market_df = stock.get_market_trading_value_by_investor(
            yesterday, yesterday, "KOSPI"
        )

        if not market_df.empty:
            print(f"\n날짜: {yesterday}")
            print(f"{'투자자':>10} {'순매수':>15}")
            print("-" * 30)

            for investor, row in market_df.iterrows():
                value = row['순매수']
                print(f"{investor:>10} {value:>+14,.0f}원")

            print("\n✅ 시장 전체 수급 데이터 수집 성공")
        else:
            print("⚠️ 시장 데이터 없음 (주말 또는 휴장일)")

    except Exception as e:
        print(f"❌ 시장 수급 조회 실패: {e}")

except ImportError:
    print("❌ pykrx 패키지가 설치되지 않았습니다.")
    print("설치 명령: pip install pykrx")
except Exception as e:
    print(f"❌ 테스트 실패: {e}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 최종 결과
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("\n" + "=" * 80)
print("📊 테스트 2 최종 결과")
print("=" * 80)
print("\n🎯 수급 데이터 수집 방법: pykrx 단독 사용 (가장 신뢰도 높음)")
print("⚠️ 주의: 당일 데이터는 오후 6시 이후 제공됨")
print("\n" + "=" * 80)
