"""
포트폴리오 관리 모듈

기능:
- portfolio.json 로드/저장
- 종목 추가/삭제/수정
- 전체 종목 분석 실행
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import logging

from .data_collector import DataCollector
from .analyzer import MomentumAnalyzer

logger = logging.getLogger(__name__)

# 기본 경로
DEFAULT_PORTFOLIO_PATH = Path(__file__).parent.parent / "data" / "portfolio.json"


class PortfolioManager:
    """
    포트폴리오 관리자

    역할:
    1. portfolio.json 파일 관리
    2. 전체 종목 데이터 수집 + 분석
    3. 결과 통합 및 제공
    """

    def __init__(self, portfolio_path: str = None):
        self.portfolio_path = Path(portfolio_path) if portfolio_path else DEFAULT_PORTFOLIO_PATH
        self.collector = DataCollector(use_cache=True)
        self.analyzer = MomentumAnalyzer()

        # 포트폴리오 로드
        self.portfolio_data = self.load_portfolio()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 파일 입출력
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def load_portfolio(self) -> Dict[str, Any]:
        """포트폴리오 JSON 로드"""
        try:
            if not self.portfolio_path.exists():
                logger.warning(f"Portfolio file not found: {self.portfolio_path}")
                return self._create_empty_portfolio()

            with open(self.portfolio_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            logger.info(f"✅ Portfolio loaded: {len(data.get('stocks', []))} stocks")
            return data

        except Exception as e:
            logger.error(f"Failed to load portfolio: {e}")
            return self._create_empty_portfolio()

    def save_portfolio(self) -> bool:
        """포트폴리오 JSON 저장"""
        try:
            # 타임스탬프 업데이트
            self.portfolio_data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # 파일 저장
            with open(self.portfolio_path, 'w', encoding='utf-8') as f:
                json.dump(self.portfolio_data, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ Portfolio saved: {self.portfolio_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save portfolio: {e}")
            return False

    def _create_empty_portfolio(self) -> Dict[str, Any]:
        """빈 포트폴리오 생성"""
        return {
            "version": "1.0",
            "last_updated": datetime.now().strftime('%Y-%m-%d'),
            "owner": "User",
            "stocks": [],
            "settings": {
                "stop_loss_percent": -10.0,
                "max_holdings": 5,
                "analysis_period_days": 60,
                "investor_flow_days": 3
            }
        }

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 포트폴리오 조회
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_stocks(self) -> List[Dict[str, Any]]:
        """전체 종목 목록 조회"""
        return self.portfolio_data.get('stocks', [])

    def get_settings(self) -> Dict[str, Any]:
        """설정 조회"""
        return self.portfolio_data.get('settings', {})

    def get_stock_count(self) -> int:
        """보유 종목 수"""
        return len(self.get_stocks())

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 포트폴리오 수정
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def add_stock(
        self,
        ticker: str,
        name: str,
        buy_price: float,
        shares: int,
        buy_date: str = None,
        notes: str = ""
    ) -> bool:
        """종목 추가"""
        try:
            # 중복 체크
            if any(s['ticker'] == ticker for s in self.get_stocks()):
                logger.warning(f"Stock {ticker} already exists")
                return False

            new_stock = {
                "ticker": ticker,
                "name": name,
                "buy_price": buy_price,
                "shares": shares,
                "buy_date": buy_date or datetime.now().strftime('%Y-%m-%d'),
                "notes": notes
            }

            self.portfolio_data['stocks'].append(new_stock)
            self.save_portfolio()

            logger.info(f"✅ Added stock: {name} ({ticker})")
            return True

        except Exception as e:
            logger.error(f"Failed to add stock: {e}")
            return False

    def remove_stock(self, ticker: str) -> bool:
        """종목 삭제"""
        try:
            stocks = self.get_stocks()
            initial_count = len(stocks)

            self.portfolio_data['stocks'] = [
                s for s in stocks if s['ticker'] != ticker
            ]

            if len(self.portfolio_data['stocks']) < initial_count:
                self.save_portfolio()
                logger.info(f"✅ Removed stock: {ticker}")
                return True
            else:
                logger.warning(f"Stock not found: {ticker}")
                return False

        except Exception as e:
            logger.error(f"Failed to remove stock: {e}")
            return False

    def update_stock(self, ticker: str, **kwargs) -> bool:
        """종목 정보 업데이트"""
        try:
            stocks = self.get_stocks()
            for stock in stocks:
                if stock['ticker'] == ticker:
                    stock.update(kwargs)
                    self.save_portfolio()
                    logger.info(f"✅ Updated stock: {ticker}")
                    return True

            logger.warning(f"Stock not found: {ticker}")
            return False

        except Exception as e:
            logger.error(f"Failed to update stock: {e}")
            return False

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 전체 분석 실행
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def analyze_all(self) -> Dict[str, Any]:
        """
        전체 포트폴리오 분석

        Returns:
            dict: {
                'stocks': 개별 종목 분석 결과 리스트,
                'portfolio': 포트폴리오 종합 분석,
                'data_status': 데이터 수집 상태
            }
        """
        logger.info("=" * 80)
        logger.info("🚀 Starting portfolio analysis...")
        logger.info("=" * 80)

        stocks = self.get_stocks()
        settings = self.get_settings()

        if not stocks:
            logger.warning("Portfolio is empty")
            return {
                'stocks': [],
                'portfolio': self.analyzer.analyze_portfolio([]),
                'data_status': {'message': 'Portfolio is empty'}
            }

        # 개별 종목 분석 결과
        analysis_results = []
        data_statuses = []

        for stock in stocks:
            ticker = stock['ticker']
            name = stock['name']
            buy_price = stock['buy_price']
            shares = stock['shares']

            logger.info(f"\n📊 Analyzing: {name} ({ticker})")
            logger.info("-" * 80)

            try:
                # 1. 주가 데이터 수집
                price_result = self.collector.get_stock_price(
                    ticker,
                    days=settings.get('analysis_period_days', 60)
                )

                data_statuses.append({
                    'ticker': ticker,
                    'type': 'price',
                    'source': price_result['source'],
                    'level': price_result['level'],
                    'message': price_result['message']
                })

                # 2. 수급 데이터 수집
                flow_result = self.collector.get_investor_flow(
                    ticker,
                    days=settings.get('investor_flow_days', 3)
                )

                data_statuses.append({
                    'ticker': ticker,
                    'type': 'flow',
                    'source': flow_result['source'],
                    'level': flow_result['level'],
                    'message': flow_result['message']
                })

                # 3. 펀더멘털 데이터 (선택)
                fund_result = self.collector.get_fundamental(ticker)

                data_statuses.append({
                    'ticker': ticker,
                    'type': 'fundamental',
                    'source': fund_result['source'],
                    'level': fund_result['level'],
                    'message': fund_result['message']
                })

                # 4. 분석 실행
                analysis = self.analyzer.analyze(
                    ticker=ticker,
                    name=name,
                    price_data=price_result['data'],
                    flow_data=flow_result['data'],
                    buy_price=buy_price,
                    shares=shares
                )

                # 추가 정보
                analysis['buy_date'] = stock.get('buy_date', 'N/A')
                analysis['notes'] = stock.get('notes', '')
                analysis['fundamental'] = fund_result['data']

                analysis_results.append(analysis)

                logger.info(f"  ✅ Analysis complete: {analysis['signal_emoji']} {analysis['status']}")

            except Exception as e:
                logger.error(f"  ❌ Analysis failed for {ticker}: {e}")
                # 실패 시 빈 결과 추가
                empty_result = self.analyzer._generate_empty_result(ticker, name, str(e))
                empty_result['buy_price'] = buy_price
                empty_result['shares'] = shares
                analysis_results.append(empty_result)

        # 포트폴리오 종합 분석
        portfolio_summary = self.analyzer.analyze_portfolio(analysis_results)

        logger.info("\n" + "=" * 80)
        logger.info("✅ Portfolio analysis complete")
        logger.info(f"   Total stocks: {len(analysis_results)}")
        logger.info(f"   Total return: {portfolio_summary['total_return_rate']:+.2f}%")
        logger.info("=" * 80)

        return {
            'stocks': analysis_results,
            'portfolio': portfolio_summary,
            'data_status': data_statuses,
            'timestamp': datetime.now().isoformat()
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 테스트 코드
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    print("=" * 80)
    print("🧪 PortfolioManager 테스트")
    print("=" * 80)

    # 포트폴리오 로드
    manager = PortfolioManager()

    print(f"\n📂 Portfolio loaded: {manager.portfolio_path}")
    print(f"   Owner: {manager.portfolio_data.get('owner', 'Unknown')}")
    print(f"   Stocks: {manager.get_stock_count()}")

    # 종목 목록
    print("\n📊 Holdings:")
    print("-" * 80)
    for stock in manager.get_stocks():
        print(f"  • {stock['name']} ({stock['ticker']})")
        print(f"    매수가: {stock['buy_price']:,.0f}원 × {stock['shares']}주")

    # 전체 분석
    print("\n" + "=" * 80)
    print("🚀 Running full analysis...")
    print("=" * 80)

    result = manager.analyze_all()

    # 결과 출력
    print("\n" + "=" * 80)
    print("📊 Analysis Results")
    print("=" * 80)

    for stock in result['stocks']:
        print(f"\n{stock['name']} ({stock['ticker']})")
        print(f"  현재가: {stock['current_price']:,.0f}원")
        print(f"  수익률: {stock['return_rate']:+.2f}%")
        print(f"  신호: {stock['signal_emoji']} {stock['status']}")
        print(f"  조언: {stock['action']}")

    # 포트폴리오 요약
    portfolio = result['portfolio']
    print("\n" + "=" * 80)
    print("📈 Portfolio Summary")
    print("=" * 80)
    print(f"총 투자금: {portfolio['total_invested']:,.0f}원")
    print(f"현재 평가액: {portfolio['total_current_value']:,.0f}원")
    print(f"평가 손익: {portfolio['total_profit']:+,.0f}원 ({portfolio['total_return_rate']:+.2f}%)")

    if portfolio['warnings']:
        print(f"\n⚠️ Warnings:")
        for warning in portfolio['warnings']:
            print(f"  {warning}")

    print("\n✅ 테스트 완료")
