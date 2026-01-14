"""
AI Advisor - Gemini API 연동

이광수 페르소나 기반 투자 조언 생성
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from .prompts import (
    LEE_GWANGSOO_PERSONA,
    build_portfolio_prompt,
    build_stock_prompt,
    build_daily_prompt
)

logger = logging.getLogger(__name__)


class AIAdvisor:
    """
    AI 투자 어드바이저

    Gemini API를 사용하여 이광수 페르소나로 투자 조언 생성
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: Google AI API 키 (없으면 환경변수에서 가져옴)
        """
        self.api_key = api_key or self._get_api_key()
        self.model = None
        self.gemini_available = False

        # Gemini 초기화
        self._initialize_gemini()

    def _get_api_key(self) -> Optional[str]:
        """API 키 가져오기 (환경변수 또는 Streamlit secrets)"""
        # 1. 환경변수
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            return api_key

        # 2. Streamlit secrets (웹 앱에서 실행 시)
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
                return st.secrets['GEMINI_API_KEY']
        except:
            pass

        # 3. .streamlit/secrets.toml 파일 직접 읽기
        try:
            secrets_path = Path(__file__).parent.parent / ".streamlit" / "secrets.toml"
            if secrets_path.exists():
                with open(secrets_path, 'r') as f:
                    for line in f:
                        if line.startswith('GEMINI_API_KEY'):
                            return line.split('=')[1].strip().strip('"\'')
        except:
            pass

        logger.warning("Gemini API key not found")
        return None

    def _initialize_gemini(self):
        """Gemini API 초기화"""
        if not self.api_key:
            logger.warning("⚠️ Gemini API key not available - AI features disabled")
            return

        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)

            # Gemini Pro 모델 설정
            self.model = genai.GenerativeModel(
                model_name='gemini-pro',
                generation_config={
                    'temperature': 0.7,  # 적당한 창의성
                    'top_p': 0.8,
                    'top_k': 40,
                    'max_output_tokens': 1024,
                }
            )

            self.gemini_available = True
            logger.info("✅ Gemini API initialized successfully")

        except ImportError:
            logger.error("❌ google-generativeai package not installed")
            logger.info("Install with: pip install google-generativeai")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini: {e}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 조언 생성
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def analyze_portfolio(
        self,
        portfolio_result: Dict[str, Any],
        question: str = "현재 포트폴리오를 종합 분석하고 조언해주세요."
    ) -> str:
        """
        포트폴리오 전체 분석

        Args:
            portfolio_result: PortfolioManager.analyze_all() 결과
            question: 질문 (옵션)

        Returns:
            str: AI 조언
        """
        if not self.gemini_available:
            return self._generate_fallback_portfolio_advice(portfolio_result)

        try:
            # 프롬프트 생성
            user_prompt = build_portfolio_prompt(portfolio_result, question)

            # Gemini API 호출
            response = self.model.generate_content([
                LEE_GWANGSOO_PERSONA,
                user_prompt
            ])

            return response.text

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return self._generate_fallback_portfolio_advice(portfolio_result)

    def analyze_stock(self, stock: Dict[str, Any]) -> str:
        """
        개별 종목 분석

        Args:
            stock: 종목 분석 결과 dict

        Returns:
            str: AI 조언
        """
        if not self.gemini_available:
            return self._generate_fallback_stock_advice(stock)

        try:
            # 프롬프트 생성
            user_prompt = build_stock_prompt(stock)

            # Gemini API 호출
            response = self.model.generate_content([
                LEE_GWANGSOO_PERSONA,
                user_prompt
            ])

            return response.text

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return self._generate_fallback_stock_advice(stock)

    def generate_daily_insight(self, portfolio_result: Dict[str, Any]) -> str:
        """
        일일 시황 분석

        Args:
            portfolio_result: 포트폴리오 분석 결과

        Returns:
            str: 오늘의 핵심 메시지
        """
        if not self.gemini_available:
            return self._generate_fallback_daily_insight(portfolio_result)

        try:
            # 프롬프트 생성
            user_prompt = build_daily_prompt(portfolio_result)

            # Gemini API 호출
            response = self.model.generate_content([
                LEE_GWANGSOO_PERSONA,
                user_prompt
            ])

            return response.text

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return self._generate_fallback_daily_insight(portfolio_result)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Fallback (Gemini 없이 작동)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _generate_fallback_portfolio_advice(self, portfolio_result: Dict[str, Any]) -> str:
        """Gemini 없이 기본 조언 생성"""
        portfolio = portfolio_result.get('portfolio', {})
        stocks = portfolio_result.get('stocks', [])

        advice = ["**[이광수의 포트폴리오 분석]**\n"]

        # 1. 종합 판단
        total_return = portfolio.get('total_return_rate', 0)
        if total_return >= 5:
            advice.append("**종합 판단**: 양호한 수익률입니다. 현재 추세를 유지하세요.")
        elif total_return >= 0:
            advice.append("**종합 판단**: 소폭 상승 중. 경계 태세 유지가 필요합니다.")
        else:
            advice.append("**종합 판단**: 손실 상태. 포트폴리오 점검이 시급합니다.")

        # 2. 긴급 조치
        critical_stocks = [s for s in stocks if s['status'] == 'CRITICAL']
        if critical_stocks:
            advice.append(f"\n**⚠️ 긴급 조치 필요**: {len(critical_stocks)}종목이 손절 기준 도달")
            for stock in critical_stocks:
                advice.append(f"- {stock['name']}: {stock['return_rate']:+.2f}% → 즉시 손절")

        # 3. 핵심 조언
        advice.append("\n**핵심 조언**:")

        # 손절 대상
        if critical_stocks:
            advice.append("1. 손절 대상 종목은 지체 없이 청산하세요. 손절은 자존심이 아니라 생존입니다.")
        else:
            advice.append("1. 현재 손절 대상 종목은 없습니다.")

        # 추세
        uptrend_count = sum(1 for s in stocks if s['trend'] == 'Uptrend')
        if uptrend_count >= len(stocks) * 0.7:
            advice.append("2. 대부분 종목이 상승 추세입니다. 현재 포지션을 홀딩하세요.")
        else:
            advice.append("2. 하락 추세 종목이 많습니다. 비중 조절을 고려하세요.")

        # 수급
        strong_supply = sum(1 for s in stocks if s['foreign_net'] > 0 and s['institution_net'] > 0)
        if strong_supply > 0:
            advice.append(f"3. {strong_supply}종목에서 외국인+기관 동반 매수 포착. 강력 홀딩 대상입니다.")
        else:
            advice.append("3. 외국인/기관 수급 약세. 신규 매수는 자제하세요.")

        advice.append("\n_\"시장은 항상 옳습니다. 시장을 따르세요.\" - 이광수_")

        return "\n".join(advice)

    def _generate_fallback_stock_advice(self, stock: Dict[str, Any]) -> str:
        """개별 종목 기본 조언"""
        advice = [f"**{stock['name']} 분석**\n"]

        # 현재 상태
        if stock['status'] == 'CRITICAL':
            advice.append(f"🔴 **즉시 손절 필요**: 수익률 {stock['return_rate']:+.2f}%")
            advice.append("- 손절 기준(-10%)을 초과했습니다. 지체 없이 청산하세요.")
        elif stock['status'] == 'STRONG_BUY':
            advice.append(f"🟢 **강력 홀딩**: 정배열 + 수급 양호")
            advice.append("- 현재 포지션을 유지하고, 추가 불타기도 고려할 수 있습니다.")
        elif stock['status'] == 'WARNING':
            advice.append(f"🟡 **경고**: 20일선 붕괴")
            advice.append("- 추세가 약해지고 있습니다. 비중 축소를 준비하세요.")
        else:
            advice.append("⚪ **관망**: 명확한 추세 없음")

        # 수급
        if stock['foreign_net'] > 0 and stock['institution_net'] > 0:
            advice.append("- 외국인+기관 동반 매수: 긍정적 신호")
        elif stock['foreign_net'] < 0 and stock['institution_net'] < 0:
            advice.append("- 외국인+기관 동반 매도: 부정적 신호")

        return "\n".join(advice)

    def _generate_fallback_daily_insight(self, portfolio_result: Dict[str, Any]) -> str:
        """일일 기본 조언"""
        portfolio = portfolio_result.get('portfolio', {})

        insight = ["**오늘의 핵심 메시지**\n"]

        # 손절 대상
        if portfolio.get('critical_count', 0) > 0:
            insight.append(f"1. ⚠️ {portfolio['critical_count']}종목 손절 대상 - 즉시 청산하세요")
        else:
            insight.append("1. ✅ 손절 대상 없음 - 리스크 관리 양호")

        # 수익률
        total_return = portfolio.get('total_return_rate', 0)
        if total_return >= 5:
            insight.append(f"2. 📈 전체 수익률 {total_return:+.2f}% - 양호한 성과 유지 중")
        elif total_return >= 0:
            insight.append(f"2. 📊 전체 수익률 {total_return:+.2f}% - 보합권, 추세 관찰 필요")
        else:
            insight.append(f"2. 📉 전체 수익률 {total_return:+.2f}% - 포트폴리오 점검 시급")

        # 종목 수
        if portfolio.get('total_stocks', 0) > 5:
            insight.append("3. ⚠️ 보유 종목 과다 - 집중도를 높이세요")
        else:
            insight.append("3. ✅ 적정 종목 수 유지 - 집중 투자 원칙 준수")

        return "\n".join(insight)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 테스트
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    print("=" * 80)
    print("🧪 AI Advisor Test")
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
                'action': '강력 홀딩',
                'profit': 50000
            },
            {
                'ticker': '105560',
                'name': 'KB금융',
                'current_price': 60000,
                'buy_price': 70000,
                'return_rate': -14.29,
                'shares': 5,
                'ma5': 61000,
                'ma20': 65000,
                'trend': 'Downtrend',
                'ma_alignment': 'Bearish',
                'foreign_net': -50000000,
                'institution_net': -30000000,
                'supply_signal': '🔴 동반 매도',
                'status': 'CRITICAL',
                'signal_emoji': '🔴',
                'action': '즉시 손절',
                'profit': -50000
            }
        ],
        'portfolio': {
            'total_invested': 1050000,
            'total_current_value': 1050000,
            'total_profit': 0,
            'total_return_rate': 0.0,
            'total_stocks': 2,
            'critical_count': 1,
            'strong_buy_count': 1,
            'warnings': ['🔴 손절 대상 1종목'],
            'urgent_actions': [
                {
                    'name': 'KB금융',
                    'action': '즉시 손절'
                }
            ]
        }
    }

    # AI Advisor 초기화
    advisor = AIAdvisor()

    # 테스트 1: 포트폴리오 분석
    print("\n📊 Portfolio Analysis:")
    print("-" * 80)
    portfolio_advice = advisor.analyze_portfolio(mock_portfolio)
    print(portfolio_advice)

    # 테스트 2: 개별 종목 분석
    print("\n" + "=" * 80)
    print("📈 Stock Analysis (삼성전자):")
    print("-" * 80)
    stock_advice = advisor.analyze_stock(mock_portfolio['stocks'][0])
    print(stock_advice)

    # 테스트 3: 일일 조언
    print("\n" + "=" * 80)
    print("📅 Daily Insight:")
    print("-" * 80)
    daily = advisor.generate_daily_insight(mock_portfolio)
    print(daily)

    print("\n✅ Test completed")
    print(f"Gemini available: {advisor.gemini_available}")
