"""
통합 테스트 러너
모든 데이터 수집 테스트를 순차적으로 실행
"""

import subprocess
import sys
from datetime import datetime

print("=" * 80)
print("🚀 Momentum Keeper - 데이터 크롤링 통합 테스트")
print("=" * 80)
print(f"\n시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 테스트 파일 목록
TESTS = [
    ('test_01_stock_price.py', '주가 데이터 수집'),
    ('test_02_investor_flow.py', '외국인/기관 수급'),
    ('test_03_fundamental.py', '펀더멘털 (PBR/PER)'),
    ('test_04_macro_proxy.py', '거시지표 프록시'),
]

results = []

for test_file, description in TESTS:
    print("\n" + "=" * 80)
    print(f"🧪 테스트 실행: {description}")
    print("=" * 80)

    try:
        # 테스트 실행
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=False,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            results.append((description, '✅ 성공'))
        else:
            results.append((description, '❌ 실패'))

    except subprocess.TimeoutExpired:
        print(f"\n⚠️ 타임아웃: {test_file}")
        results.append((description, '⏱️ 타임아웃'))

    except Exception as e:
        print(f"\n❌ 오류: {e}")
        results.append((description, f'❌ 오류: {str(e)[:30]}'))

# 최종 요약
print("\n" + "=" * 80)
print("📊 전체 테스트 결과 요약")
print("=" * 80)

for desc, status in results:
    print(f"{status:15} {desc}")

# 성공률 계산
success_count = sum(1 for _, status in results if '✅' in status)
total_count = len(results)
success_rate = (success_count / total_count) * 100

print("\n" + "-" * 80)
print(f"성공률: {success_count}/{total_count} ({success_rate:.1f}%)")
print("-" * 80)

if success_count == total_count:
    print("\n🎉 모든 테스트 통과! 데이터 수집 시스템 정상 작동")
elif success_count >= total_count * 0.7:
    print("\n✅ 대부분 테스트 통과. 일부 실패는 네트워크 또는 시장 휴장일 가능성")
else:
    print("\n⚠️ 다수 테스트 실패. 패키지 설치 또는 네트워크 연결 확인 필요")

print(f"\n종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
