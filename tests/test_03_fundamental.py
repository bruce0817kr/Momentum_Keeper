"""
테스트 3: 펀더멘털 데이터 (PBR, PER, 시가총액)
목표: pykrx와 네이버 금융 크롤링 비교
"""

from datetime import datetime, timedelta

print("=" * 80)
print("📈 TEST 3: 펀더멘털 데이터 테스트")
print("=" * 80)

# 테스트 종목
TEST_TICKERS = {
    '005930': '삼성전자',
    '105560': 'KB금융',
    '086520': '에코프로'
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 방법 1: pykrx 펀더멘털 데이터 (추천)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("\n[방법 1] pykrx 펀더멘털 데이터")
print("-" * 80)

try:
    from pykrx import stock

    for ticker, name in TEST_TICKERS.items():
        print(f"\n종목: {name} ({ticker})")

        try:
            # 어제 날짜 (당일 데이터는 없을 수 있음)
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')

            # 펀더멘털 데이터 가져오기
            df = stock.get_market_fundamental(yesterday, yesterday, ticker)

            if df.empty:
                print("  ⚠️ 데이터 없음 (주말 또는 휴장일)")
                continue

            # 데이터 추출
            data = df.iloc[0]

            bps = data.get('BPS', 0)
            per = data.get('PER', 0)
            pbr = data.get('PBR', 0)
            eps = data.get('EPS', 0)
            div_yield = data.get('DIV', 0)

            print(f"  • PER (주가수익비율): {per:.2f}배")
            print(f"  • PBR (주가순자산비율): {pbr:.2f}배")
            print(f"  • EPS (주당순이익): {eps:,.0f}원")
            print(f"  • BPS (주당순자산): {bps:,.0f}원")
            print(f"  • 배당수익률: {div_yield:.2f}%")

            # PBR 밴드 분석 (삼성전자 예시)
            if ticker == '005930':
                if pbr < 1.0:
                    band = "🟢 저평가 (PBR < 1.0)"
                elif pbr < 1.2:
                    band = "🟡 적정 (1.0 ≤ PBR < 1.2)"
                else:
                    band = "🔴 고평가 (PBR ≥ 1.2)"
                print(f"  • PBR 밴드: {band}")

            print(f"  ✅ pykrx 펀더멘털 데이터 수집 성공")

        except Exception as e:
            print(f"  ❌ 오류: {e}")

    print("\n✅ pykrx 펀더멘털 테스트 완료")
    PYKRX_SUCCESS = True

except Exception as e:
    print(f"\n❌ pykrx 테스트 실패: {e}")
    PYKRX_SUCCESS = False

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 방법 2: 네이버 금융 크롤링 (백업)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("\n" + "=" * 80)
print("[방법 2] 네이버 금융 크롤링 (백업)")
print("-" * 80)

try:
    import requests
    from bs4 import BeautifulSoup
    import time

    for ticker, name in TEST_TICKERS.items():
        print(f"\n종목: {name} ({ticker})")

        try:
            url = f"https://finance.naver.com/item/main.nhn?code={ticker}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            # PER, PBR, 시가총액 추출
            try:
                # 방법 1: ID 셀렉터 (가장 정확)
                per_elem = soup.select_one('em#_per')
                pbr_elem = soup.select_one('em#_pbr')

                # 방법 2: 테이블에서 추출 (백업)
                if not per_elem or not pbr_elem:
                    # 주요 시세 테이블 찾기
                    table = soup.select_one('table.no_info')
                    if table:
                        rows = table.find_all('tr')
                        for row in rows:
                            header = row.find('th')
                            if header and 'PER' in header.text:
                                per_elem = row.find('td')
                            elif header and 'PBR' in header.text:
                                pbr_elem = row.find('td')

                # 데이터 추출
                per_text = per_elem.text.strip() if per_elem else 'N/A'
                pbr_text = pbr_elem.text.strip() if pbr_elem else 'N/A'

                # 숫자로 변환
                try:
                    per = float(per_text.replace(',', ''))
                except:
                    per = None

                try:
                    pbr = float(pbr_text.replace(',', ''))
                except:
                    pbr = None

                print(f"  • PER: {per if per else 'N/A'}")
                print(f"  • PBR: {pbr if pbr else 'N/A'}")

                if per and pbr:
                    print(f"  ✅ 네이버 금융 크롤링 성공")
                else:
                    print(f"  ⚠️ 일부 데이터 누락")

            except Exception as e:
                print(f"  ❌ 파싱 오류: {e}")

            # 요청 간격 (크롤링 에티켓)
            time.sleep(1)

        except Exception as e:
            print(f"  ❌ 크롤링 실패: {e}")

    print("\n✅ 네이버 금융 크롤링 테스트 완료")
    NAVER_SUCCESS = True

except Exception as e:
    print(f"\n❌ 네이버 크롤링 테스트 실패: {e}")
    NAVER_SUCCESS = False

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 최종 결과
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("\n" + "=" * 80)
print("📊 테스트 3 최종 결과")
print("=" * 80)

print(f"\n[방법 1] pykrx 펀더멘털: {'✅ 성공' if PYKRX_SUCCESS else '❌ 실패'}")
print(f"[방법 2] 네이버 크롤링: {'✅ 성공' if NAVER_SUCCESS else '❌ 실패'}")

if PYKRX_SUCCESS:
    print("\n🎯 최종 추천: pykrx 우선 (공식 데이터, 안정적)")
    print("   네이버 크롤링은 pykrx 실패 시 백업으로 사용")
elif NAVER_SUCCESS:
    print("\n🎯 최종 추천: 네이버 크롤링 사용 (pykrx 실패 시)")
    print("   ⚠️ 주의: HTML 구조 변경 시 수정 필요")
else:
    print("\n⚠️ 경고: 모든 방법 실패")

print("\n" + "=" * 80)
