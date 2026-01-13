"""
테스트 4: 거시지표 프록시 데이터
목표: SOX 지수(반도체), ALB 주가(리튬)로 업황 파악
"""

from datetime import datetime, timedelta
import pandas as pd

print("=" * 80)
print("🌍 TEST 4: 거시지표 프록시 데이터 테스트")
print("=" * 80)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 프록시 1: SOX 반도체 지수 (삼성전자 업황 대리지표)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("\n[프록시 1] SOX 반도체 지수")
print("-" * 80)

try:
    import FinanceDataReader as fdr

    print("\n📊 SOX (Philadelphia Semiconductor Index)")
    print("   반도체 업계 30개 주요 기업으로 구성된 지수")
    print("   삼성전자 수출 환경의 대리 지표로 활용\n")

    # 최근 60일 데이터
    end = datetime.now()
    start = end - timedelta(days=60)

    df_sox = fdr.DataReader('SOX', start, end)

    if df_sox.empty:
        print("  ❌ SOX 데이터 수집 실패")
    else:
        # 최신 가격
        latest_price = df_sox['Close'].iloc[-1]
        first_price = df_sox['Close'].iloc[0]

        # 수익률 계산
        return_30d = (df_sox['Close'].iloc[-1] / df_sox['Close'].iloc[-20] - 1) * 100
        return_60d = (df_sox['Close'].iloc[-1] / df_sox['Close'].iloc[0] - 1) * 100

        # 이동평균선
        df_sox['MA20'] = df_sox['Close'].rolling(20).mean()
        latest_ma20 = df_sox['MA20'].iloc[-1]

        print(f"  • 현재 지수: {latest_price:,.2f}")
        print(f"  • 20일 이평선: {latest_ma20:,.2f}")
        print(f"  • 30일 수익률: {return_30d:+.2f}%")
        print(f"  • 60일 수익률: {return_60d:+.2f}%")

        # 추세 판단
        if latest_price > latest_ma20 and return_30d > 0:
            trend = "🟢 상승 추세 (반도체 업황 호조)"
            samsung_signal = "✅ 삼성전자 긍정적 환경"
        elif return_30d < -5:
            trend = "🔴 하락 추세 (반도체 업황 부진)"
            samsung_signal = "⚠️ 삼성전자 부정적 환경"
        else:
            trend = "🟡 횡보 (중립)"
            samsung_signal = "➖ 삼성전자 중립적 환경"

        print(f"\n  💡 업황 판단: {trend}")
        print(f"  💡 삼성전자 시사점: {samsung_signal}")
        print(f"\n  ✅ SOX 지수 데이터 수집 성공")

    SOX_SUCCESS = True

except Exception as e:
    print(f"  ❌ SOX 데이터 수집 실패: {e}")
    SOX_SUCCESS = False

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 프록시 2: Albemarle (ALB) 주가 (리튬 가격 대리지표)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("\n" + "=" * 80)
print("[프록시 2] Albemarle (ALB) 주가")
print("-" * 80)

try:
    print("\n📊 Albemarle Corporation (ALB)")
    print("   세계 1위 리튬 생산 기업")
    print("   에코프로 원자재 가격의 대리 지표로 활용\n")

    # 최근 60일 데이터
    end = datetime.now()
    start = end - timedelta(days=60)

    df_alb = fdr.DataReader('ALB', start, end)

    if df_alb.empty:
        print("  ❌ ALB 데이터 수집 실패")
    else:
        # 수익률 계산
        return_30d = (df_alb['Close'].iloc[-1] / df_alb['Close'].iloc[-20] - 1) * 100
        return_60d = (df_alb['Close'].iloc[-1] / df_alb['Close'].iloc[0] - 1) * 100

        # 이동평균선
        df_alb['MA20'] = df_alb['Close'].rolling(20).mean()
        latest_price = df_alb['Close'].iloc[-1]
        latest_ma20 = df_alb['MA20'].iloc[-1]

        print(f"  • 현재 주가: ${latest_price:,.2f}")
        print(f"  • 20일 이평선: ${latest_ma20:,.2f}")
        print(f"  • 30일 수익률: {return_30d:+.2f}%")
        print(f"  • 60일 수익률: {return_60d:+.2f}%")

        # 추세 판단
        if latest_price > latest_ma20 and return_30d > 0:
            trend = "🟢 상승 추세 (리튬 가격 반등 가능성)"
            ecopro_signal = "✅ 에코프로 긍정적 환경"
        elif return_30d < -5:
            trend = "🔴 하락 추세 (리튬 가격 약세)"
            ecopro_signal = "⚠️ 에코프로 부정적 환경"
        else:
            trend = "🟡 횡보 (중립)"
            ecopro_signal = "➖ 에코프로 중립적 환경"

        print(f"\n  💡 업황 판단: {trend}")
        print(f"  💡 에코프로 시사점: {ecopro_signal}")
        print(f"\n  ✅ ALB 주가 데이터 수집 성공")

    ALB_SUCCESS = True

except Exception as e:
    print(f"  ❌ ALB 데이터 수집 실패: {e}")
    ALB_SUCCESS = False

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 프록시 3: 에코프로비엠 (247540) - 리튬 2차전지 동반 지표
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("\n" + "=" * 80)
print("[프록시 3] 에코프로비엠 동반 분석")
print("-" * 80)

try:
    print("\n📊 에코프로 vs 에코프로비엠 상관관계 분석")
    print("   에코프로비엠: 에코프로의 양극재 자회사")
    print("   동반 상승 시 2차전지 업황 호조 신호\n")

    # 최근 30일 데이터
    end = datetime.now()
    start = end - timedelta(days=30)

    df_ecopro = fdr.DataReader('086520', start, end)  # 에코프로
    df_ecoproBM = fdr.DataReader('247540', start, end)  # 에코프로비엠

    if not df_ecopro.empty and not df_ecoproBM.empty:
        # 30일 수익률
        ecopro_return = (df_ecopro['Close'].iloc[-1] / df_ecopro['Close'].iloc[0] - 1) * 100
        ecoproBM_return = (df_ecoproBM['Close'].iloc[-1] / df_ecoproBM['Close'].iloc[0] - 1) * 100

        print(f"  • 에코프로 30일 수익률: {ecopro_return:+.2f}%")
        print(f"  • 에코프로비엠 30일 수익률: {ecoproBM_return:+.2f}%")

        # 동반 분석
        if ecopro_return > 0 and ecoproBM_return > 0:
            signal = "🟢 동반 상승 (2차전지 업황 호조)"
        elif ecopro_return < 0 and ecoproBM_return < 0:
            signal = "🔴 동반 하락 (2차전지 업황 부진)"
        else:
            signal = "🟡 엇갈림 (업황 불명확)"

        print(f"\n  💡 업황 신호: {signal}")
        print(f"  ✅ 동반 분석 완료")

    CORRELATION_SUCCESS = True

except Exception as e:
    print(f"  ❌ 동반 분석 실패: {e}")
    CORRELATION_SUCCESS = False

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 최종 결과
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("\n" + "=" * 80)
print("📊 테스트 4 최종 결과")
print("=" * 80)

print(f"\n[프록시 1] SOX 반도체 지수: {'✅ 성공' if SOX_SUCCESS else '❌ 실패'}")
print(f"[프록시 2] Albemarle (ALB): {'✅ 성공' if ALB_SUCCESS else '❌ 실패'}")
print(f"[프록시 3] 에코프로 동반 분석: {'✅ 성공' if CORRELATION_SUCCESS else '❌ 실패'}")

print("\n🎯 거시지표 전략:")
print("   1. 삼성전자: SOX 지수로 반도체 업황 파악")
print("   2. 에코프로: ALB + 에코프로비엠으로 리튬/2차전지 업황 파악")
print("   3. KB금융: 거시지표 불필요 (금융주는 금리/경기에 의존)")

print("\n💡 장점:")
print("   • 실시간 데이터 수집 가능")
print("   • 별도 API 인증 불필요")
print("   • 구현 간단하고 안정적")

print("\n⚠️ 단점:")
print("   • 간접 지표이므로 정확도 한계")
print("   • 실제 수출 데이터나 원자재 가격보다 지연 가능")

print("\n📌 추천:")
print("   프록시 지표를 기본으로 사용하되,")
print("   UI에 수동 입력 옵션 병행 (중요한 뉴스 발생 시 사용자가 직접 입력)")

print("\n" + "=" * 80)
