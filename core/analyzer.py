"""
이광수 알고리즘 - 추세 추종 + 손절 원칙

핵심 철학:
1. 추세를 거스르지 마라 (Ride the Trend)
2. 손절은 자존심이 아니라 생존 (Cut Losers Short)
3. 데이터가 모든 것을 말해준다 (Data-Driven)
"""

import pandas as pd
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class MomentumAnalyzer:
    """
    이광수식 모멘텀 분석기

    분석 항목:
    - 이동평균선 정배열/역배열
    - 외국인/기관 수급
    - 손절 신호 (-10%)
    - 종합 투자 신호
    """

    def __init__(self, stop_loss_percent=-10.0):
        self.stop_loss_percent = stop_loss_percent

    def analyze(
        self,
        ticker: str,
        name: str,
        price_data: pd.DataFrame,
        flow_data: Dict[str, Any],
        buy_price: float,
        shares: int = 0
    ) -> Dict[str, Any]:
        """
        종목 종합 분석

        Args:
            ticker: 종목코드
            name: 종목명
            price_data: 주가 DataFrame (Close, MA5, MA20 포함)
            flow_data: 수급 데이터 (foreign_net, institution_net)
            buy_price: 매수 평단가
            shares: 보유 수량

        Returns:
            dict: 분석 결과
        """
        if price_data.empty:
            return self._generate_empty_result(ticker, name, "No price data")

        try:
            # 최신 가격 정보
            latest = price_data.iloc[-1]
            current_price = latest['Close']
            ma5 = latest.get('MA5', None)
            ma20 = latest.get('MA20', None)

            # 수익률 계산
            return_rate = (current_price - buy_price) / buy_price * 100
            profit = (current_price - buy_price) * shares

            # 수급 정보
            foreign_net = flow_data.get('foreign_net', 0)
            institution_net = flow_data.get('institution_net', 0)

            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # 이광수 알고리즘 적용
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            signal = self._calculate_signal(
                current_price, ma5, ma20,
                foreign_net, institution_net,
                return_rate
            )

            # 추세 방향
            trend = self._determine_trend(current_price, ma5, ma20)

            # 펀더멘털 밴드 (옵션)
            pbr_band = self._determine_pbr_band(ticker, price_data)

            return {
                # 기본 정보
                'ticker': ticker,
                'name': name,

                # 가격 정보
                'current_price': current_price,
                'buy_price': buy_price,
                'shares': shares,
                'return_rate': return_rate,
                'profit': profit,

                # 기술적 지표
                'ma5': ma5,
                'ma20': ma20,
                'trend': trend,
                'ma_alignment': 'Bullish' if ma5 and ma20 and ma5 > ma20 else 'Bearish',

                # 수급
                'foreign_net': foreign_net,
                'institution_net': institution_net,
                'supply_signal': self._get_supply_signal(foreign_net, institution_net),

                # 신호
                'status': signal['status'],
                'signal_emoji': signal['emoji'],
                'action': signal['action'],
                'priority': signal['priority'],

                # 추가 정보
                'pbr_band': pbr_band,
                'warnings': self._generate_warnings(return_rate, trend, foreign_net)
            }

        except Exception as e:
            logger.error(f"Analysis failed for {ticker}: {e}")
            return self._generate_empty_result(ticker, name, str(e))

    def _calculate_signal(
        self,
        price: float,
        ma5: float,
        ma20: float,
        foreign_net: float,
        institution_net: float,
        return_rate: float
    ) -> Dict[str, str]:
        """
        이광수 투자 신호 계산

        우선순위:
        1. 손절 (CRITICAL) - 최우선
        2. 강한 상승 추세 (STRONG BUY)
        3. 약한 상승 추세 (BULLISH)
        4. 추세 붕괴 경고 (WARNING)
        5. 중립 (NEUTRAL)
        """

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 1단계: 손절 원칙 (최우선)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if return_rate <= self.stop_loss_percent:
            return {
                'status': 'CRITICAL',
                'emoji': '🔴',
                'action': '즉시 손절 (원칙 위반)',
                'priority': 1
            }

        # MA 데이터 없으면 중립
        if not ma5 or not ma20:
            return {
                'status': 'NEUTRAL',
                'emoji': '⚪',
                'action': '데이터 부족 - 관망',
                'priority': 5
            }

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 2단계: 강한 상승 추세
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 정배열 + 외국인+기관 동반 매수
        if ma5 > ma20 and foreign_net > 0 and institution_net > 0:
            return {
                'status': 'STRONG_BUY',
                'emoji': '🟢',
                'action': '강력 홀딩 / 불타기 가능',
                'priority': 2
            }

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 3단계: 약한 상승 추세
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 정배열 + 수급 중 하나라도 양호
        elif ma5 > ma20 and (foreign_net > 0 or institution_net > 0):
            return {
                'status': 'BULLISH',
                'emoji': '🟢',
                'action': '홀딩 유지',
                'priority': 3
            }

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 4단계: 추세 붕괴 경고
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 20일선 붕괴
        elif price < ma20:
            return {
                'status': 'WARNING',
                'emoji': '🟡',
                'action': '비중 축소 준비 (20일선 붕괴)',
                'priority': 4
            }

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 5단계: 중립
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        else:
            return {
                'status': 'NEUTRAL',
                'emoji': '⚪',
                'action': '관망',
                'priority': 5
            }

    def _determine_trend(self, price: float, ma5: float, ma20: float) -> str:
        """추세 판단"""
        if not ma5 or not ma20:
            return 'Unknown'

        if ma5 > ma20:
            return 'Uptrend'
        elif ma5 < ma20:
            return 'Downtrend'
        else:
            return 'Sideways'

    def _get_supply_signal(self, foreign_net: float, institution_net: float) -> str:
        """수급 신호"""
        if foreign_net > 0 and institution_net > 0:
            return '🟢 강한 매수 (외국인+기관)'
        elif foreign_net > 0:
            return '🟡 외국인 매수'
        elif institution_net > 0:
            return '🟡 기관 매수'
        elif foreign_net < 0 and institution_net < 0:
            return '🔴 동반 매도'
        else:
            return '⚪ 혼조세'

    def _determine_pbr_band(self, ticker: str, price_data: pd.DataFrame) -> str:
        """PBR 밴드 판단 (삼성전자 특화)"""
        # 실제로는 펀더멘털 데이터에서 PBR 가져와야 함
        # 여기서는 간단히 처리
        if ticker == '005930':  # 삼성전자
            # PBR 1.0 기준
            return 'Normal'
        return 'N/A'

    def _generate_warnings(
        self,
        return_rate: float,
        trend: str,
        foreign_net: float
    ) -> list:
        """경고 메시지 생성"""
        warnings = []

        if return_rate < -5:
            warnings.append(f"⚠️ 수익률 {return_rate:.2f}% - 손절 기준 접근")

        if trend == 'Downtrend':
            warnings.append("⚠️ 하락 추세 - 주의 필요")

        if foreign_net < -100000000:  # 1억 이상 순매도
            warnings.append("⚠️ 외국인 대량 매도")

        return warnings

    def _generate_empty_result(self, ticker: str, name: str, reason: str) -> Dict[str, Any]:
        """빈 결과 생성 (에러 시)"""
        return {
            'ticker': ticker,
            'name': name,
            'current_price': 0,
            'buy_price': 0,
            'shares': 0,
            'return_rate': 0,
            'profit': 0,
            'ma5': None,
            'ma20': None,
            'trend': 'Unknown',
            'ma_alignment': 'Unknown',
            'foreign_net': 0,
            'institution_net': 0,
            'supply_signal': '⚪ 데이터 없음',
            'status': 'ERROR',
            'signal_emoji': '❌',
            'action': f'분석 실패: {reason}',
            'priority': 99,
            'pbr_band': 'N/A',
            'warnings': [f'❌ {reason}']
        }

    def analyze_portfolio(self, stocks_data: list) -> Dict[str, Any]:
        """
        포트폴리오 전체 분석

        Args:
            stocks_data: 개별 종목 분석 결과 리스트

        Returns:
            dict: 포트폴리오 요약
        """
        if not stocks_data:
            return {
                'total_stocks': 0,
                'total_invested': 0,
                'total_current_value': 0,
                'total_profit': 0,
                'total_return_rate': 0,
                'critical_count': 0,
                'strong_buy_count': 0,
                'warnings': ['포트폴리오가 비어있습니다']
            }

        total_invested = sum(s['buy_price'] * s['shares'] for s in stocks_data)
        total_current_value = sum(s['current_price'] * s['shares'] for s in stocks_data)
        total_profit = total_current_value - total_invested
        total_return_rate = (total_profit / total_invested * 100) if total_invested > 0 else 0

        # 신호별 카운트
        critical_count = sum(1 for s in stocks_data if s['status'] == 'CRITICAL')
        strong_buy_count = sum(1 for s in stocks_data if s['status'] == 'STRONG_BUY')
        warning_count = sum(1 for s in stocks_data if s['status'] == 'WARNING')

        # 전체 경고
        portfolio_warnings = []
        if critical_count > 0:
            portfolio_warnings.append(f"🔴 손절 대상 {critical_count}종목")
        if len(stocks_data) > 5:
            portfolio_warnings.append("⚠️ 보유 종목 5개 초과 (집중도 ↓)")
        if total_return_rate < -5:
            portfolio_warnings.append(f"⚠️ 전체 수익률 {total_return_rate:.2f}% - 포트폴리오 점검 필요")

        return {
            'total_stocks': len(stocks_data),
            'total_invested': total_invested,
            'total_current_value': total_current_value,
            'total_profit': total_profit,
            'total_return_rate': total_return_rate,

            'critical_count': critical_count,
            'strong_buy_count': strong_buy_count,
            'warning_count': warning_count,
            'neutral_count': len(stocks_data) - critical_count - strong_buy_count - warning_count,

            'warnings': portfolio_warnings,

            # 우선 조치 대상
            'urgent_actions': [
                s for s in stocks_data
                if s['status'] in ['CRITICAL', 'WARNING']
            ]
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 테스트 코드
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    import random
    from datetime import datetime, timedelta

    print("=" * 80)
    print("🧪 MomentumAnalyzer 테스트")
    print("=" * 80)

    analyzer = MomentumAnalyzer()

    # Mock 데이터 생성
    dates = pd.date_range(end=datetime.now(), periods=60, freq='D')
    mock_price_data = pd.DataFrame({
        'Close': [70000 * (1 + random.gauss(0, 0.02)) for _ in range(60)],
        'MA5': [70000 * (1 + random.gauss(0, 0.01)) for _ in range(60)],
        'MA20': [70000 * (1 + random.gauss(0, 0.005)) for _ in range(60)]
    }, index=dates)

    # 테스트 케이스 1: 강한 상승 추세
    print("\n" + "=" * 80)
    print("Test 1: 강한 상승 추세 (정배열 + 수급 양호)")
    print("-" * 80)

    mock_price_data.iloc[-1, mock_price_data.columns.get_loc('Close')] = 75000
    mock_price_data.iloc[-1, mock_price_data.columns.get_loc('MA5')] = 74000
    mock_price_data.iloc[-1, mock_price_data.columns.get_loc('MA20')] = 72000

    result1 = analyzer.analyze(
        ticker='005930',
        name='삼성전자',
        price_data=mock_price_data,
        flow_data={'foreign_net': 100000000, 'institution_net': 50000000},
        buy_price=70000,
        shares=10
    )

    print(f"종목: {result1['name']}")
    print(f"  현재가: {result1['current_price']:,.0f}원")
    print(f"  수익률: {result1['return_rate']:+.2f}%")
    print(f"  신호: {result1['signal_emoji']} {result1['status']}")
    print(f"  조언: {result1['action']}")

    # 테스트 케이스 2: 손절 대상
    print("\n" + "=" * 80)
    print("Test 2: 손절 대상 (-10% 이하)")
    print("-" * 80)

    mock_price_data.iloc[-1, mock_price_data.columns.get_loc('Close')] = 62000

    result2 = analyzer.analyze(
        ticker='105560',
        name='KB금융',
        price_data=mock_price_data,
        flow_data={'foreign_net': -50000000, 'institution_net': 10000000},
        buy_price=70000,
        shares=5
    )

    print(f"종목: {result2['name']}")
    print(f"  현재가: {result2['current_price']:,.0f}원")
    print(f"  수익률: {result2['return_rate']:+.2f}%")
    print(f"  신호: {result2['signal_emoji']} {result2['status']}")
    print(f"  조언: {result2['action']}")

    # 포트폴리오 분석
    print("\n" + "=" * 80)
    print("Test 3: 포트폴리오 종합 분석")
    print("-" * 80)

    portfolio = analyzer.analyze_portfolio([result1, result2])

    print(f"총 종목 수: {portfolio['total_stocks']}")
    print(f"총 투자금: {portfolio['total_invested']:,.0f}원")
    print(f"현재 평가액: {portfolio['total_current_value']:,.0f}원")
    print(f"평가 손익: {portfolio['total_profit']:+,.0f}원 ({portfolio['total_return_rate']:+.2f}%)")
    print(f"\n신호 분포:")
    print(f"  🔴 손절 대상: {portfolio['critical_count']}")
    print(f"  🟢 강한 매수: {portfolio['strong_buy_count']}")
    print(f"  🟡 경고: {portfolio['warning_count']}")
    print(f"  ⚪ 중립: {portfolio['neutral_count']}")

    if portfolio['warnings']:
        print(f"\n⚠️ 포트폴리오 경고:")
        for warning in portfolio['warnings']:
            print(f"  {warning}")

    print("\n✅ 테스트 완료")
