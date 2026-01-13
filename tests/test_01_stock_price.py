"""
테스트 1: 주가 데이터 수집 (OHLCV + 이동평균선)
목표: FinanceDataReader와 pykrx 비교 테스트
"""

import sys
from datetime import datetime, timedelta
import pandas as pd

print("=" * 80)
print("📊 TEST 1: 주가 데이터 수집 테스트")
print("=" * 80)

# 테스트 종목
TEST_TICKERS = {
    '005930': '삼성전자',
    '105560': 'KB금융',
    '086520': '에코프로'
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 방법 1: FinanceDataReader (추천)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("\n[방법 1] FinanceDataReader 테스트")
print("-" * 80)

try:
    import FinanceDataReader as fdr

    for ticker, name in TEST_TICKERS.items():
        print(f"\n종목: {name} ({ticker})")

        # 최근 60일 데이터 수집
        end = datetime.now()
        start = end - timedelta(days=60)

        df = fdr.DataReader(ticker, start, end)

        # 이동평균선 계산
        df['MA5'] = df['Close'].rolling(window=5).mean()
        df['MA20'] = df['Close'].rolling(window=20).mean()

        # 최신 데이터
        latest = df.iloc[-1]
        prev = df.iloc[-2]

        print(f"  • 현재가: {latest['Close']:,.0f}원")
        print(f"  • 전일비: {latest['Close'] - prev['Close']:+,.0f}원 ({(latest['Close']/prev['Close']-1)*100:+.2f}%)")
        print(f"  • MA5: {latest['MA5']:,.0f}원")
        print(f"  • MA20: {latest['MA20']:,.0f}원")
        print(f"  • 정배열 여부: {'✅ YES (상승 추세)' if latest['MA5'] > latest['MA20'] else '❌ NO (하락 추세)'}")
        print(f"  • 데이터 기간: {df.index[0].date()} ~ {df.index[-1].date()} ({len(df)}일)")

        # 결과 판정
        if pd.notna(latest['MA5']) and pd.notna(latest['MA20']):
            print(f"  ✅ 성공: 주가 및 이평선 데이터 정상 수집")
        else:
            print(f"  ⚠️ 경고: 이평선 계산 오류")

    print("\n✅ FinanceDataReader 테스트 완료")
    FDR_SUCCESS = True

except Exception as e:
    print(f"\n❌ FinanceDataReader 실패: {e}")
    FDR_SUCCESS = False

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 방법 2: pykrx (백업)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("\n" + "=" * 80)
print("[방법 2] pykrx 테스트 (백업 방법)")
print("-" * 80)

try:
    from pykrx import stock

    for ticker, name in TEST_TICKERS.items():
        print(f"\n종목: {name} ({ticker})")

        # 최근 60일 데이터
        end = datetime.now().strftime('%Y%m%d')
        start = (datetime.now() - timedelta(days=60)).strftime('%Y%m%d')

        df = stock.get_market_ohlcv(start, end, ticker)

        if df.empty:
            print(f"  ❌ 데이터 없음")
            continue

        # 이동평균선 계산
        df['MA5'] = df['종가'].rolling(window=5).mean()
        df['MA20'] = df['종가'].rolling(window=20).mean()

        # 최신 데이터
        latest = df.iloc[-1]
        prev = df.iloc[-2]

        print(f"  • 현재가: {latest['종가']:,.0f}원")
        print(f"  • 전일비: {latest['종가'] - prev['종가']:+,.0f}원")
        print(f"  • MA5: {latest['MA5']:,.0f}원")
        print(f"  • MA20: {latest['MA20']:,.0f}원")
        print(f"  • 정배열 여부: {'✅ YES' if latest['MA5'] > latest['MA20'] else '❌ NO'}")
        print(f"  ✅ 성공: pykrx 데이터 정상 수집 ({len(df)}일)")

    print("\n✅ pykrx 테스트 완료")
    PYKRX_SUCCESS = True

except Exception as e:
    print(f"\n❌ pykrx 실패: {e}")
    PYKRX_SUCCESS = False

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 최종 결과
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("\n" + "=" * 80)
print("📊 테스트 1 최종 결과")
print("=" * 80)

print(f"\n[방법 1] FinanceDataReader: {'✅ 성공' if FDR_SUCCESS else '❌ 실패'}")
print(f"[방법 2] pykrx: {'✅ 성공' if PYKRX_SUCCESS else '❌ 실패'}")

if FDR_SUCCESS:
    print("\n🎯 최종 추천: FinanceDataReader (간단하고 안정적)")
elif PYKRX_SUCCESS:
    print("\n🎯 최종 추천: pykrx (FinanceDataReader 실패 시 백업)")
else:
    print("\n⚠️ 경고: 모든 방법 실패 - 네트워크 또는 패키지 설치 확인 필요")

print("\n" + "=" * 80)
