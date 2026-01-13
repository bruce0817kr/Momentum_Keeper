"""
데이터 수집 모듈 - Fallback 시스템 포함

Primary → Fallback → Cache → Mock/Manual 4단계 전략
"""

import os
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import logging

# 설정
CACHE_DIR = Path(__file__).parent.parent / "data" / "cache"
CACHE_TTL_HOURS = 24

# 로거 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataCollector:
    """
    통합 데이터 수집기
    - 다층 Fallback 시스템
    - 자동 캐싱
    - 에러 핸들링
    """

    def __init__(self, use_cache=True):
        self.use_cache = use_cache
        self.cache_dir = CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # 라이브러리 동적 로딩
        self._load_libraries()

    def _load_libraries(self):
        """필요한 라이브러리 동적 로딩"""
        try:
            import FinanceDataReader as fdr
            self.fdr = fdr
            self.fdr_available = True
            logger.info("✅ FinanceDataReader loaded")
        except ImportError:
            self.fdr = None
            self.fdr_available = False
            logger.warning("⚠️ FinanceDataReader not available")

        try:
            from pykrx import stock
            self.pykrx = stock
            self.pykrx_available = True
            logger.info("✅ pykrx loaded")
        except ImportError:
            self.pykrx = None
            self.pykrx_available = False
            logger.warning("⚠️ pykrx not available")

        try:
            import requests
            from bs4 import BeautifulSoup
            self.requests = requests
            self.BeautifulSoup = BeautifulSoup
            self.scraping_available = True
            logger.info("✅ Web scraping libraries loaded")
        except ImportError:
            self.requests = None
            self.BeautifulSoup = None
            self.scraping_available = False
            logger.warning("⚠️ Web scraping not available")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 주가 데이터 (OHLCV + 이동평균선)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_stock_price(self, ticker, days=60):
        """
        주가 데이터 수집 (Fallback 포함)

        Args:
            ticker: 종목코드
            days: 조회 기간 (일)

        Returns:
            dict: {
                'data': DataFrame,
                'source': str,
                'level': str,
                'message': str
            }
        """
        end = datetime.now()
        start = end - timedelta(days=days)

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Level 1: FinanceDataReader (Primary)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if self.fdr_available:
            try:
                logger.info(f"[{ticker}] Fetching from FinanceDataReader...")
                df = self.fdr.DataReader(ticker, start, end)

                if not df.empty:
                    df = self._add_moving_averages(df)
                    self._save_cache(ticker, 'price', df)

                    return {
                        'data': df,
                        'source': 'FinanceDataReader',
                        'level': 'success',
                        'message': None
                    }
            except Exception as e:
                logger.warning(f"[{ticker}] FinanceDataReader failed: {e}")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Level 2: pykrx (Fallback)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if self.pykrx_available:
            try:
                logger.info(f"[{ticker}] Fetching from pykrx (fallback)...")
                start_str = start.strftime('%Y%m%d')
                end_str = end.strftime('%Y%m%d')

                df = self.pykrx.get_market_ohlcv(start_str, end_str, ticker)

                if not df.empty:
                    # 컬럼명 통일 (영문으로 변경)
                    df = df.rename(columns={
                        '시가': 'Open',
                        '고가': 'High',
                        '저가': 'Low',
                        '종가': 'Close',
                        '거래량': 'Volume'
                    })

                    df = self._add_moving_averages(df, close_col='Close')
                    self._save_cache(ticker, 'price', df)

                    return {
                        'data': df,
                        'source': 'pykrx',
                        'level': 'warning',
                        'message': '⚠️ Backup data source used'
                    }
            except Exception as e:
                logger.warning(f"[{ticker}] pykrx failed: {e}")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Level 3: Cache
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if self.use_cache:
            try:
                logger.info(f"[{ticker}] Loading from cache...")
                df, cache_time = self._load_cache(ticker, 'price')

                if df is not None:
                    age_hours = (datetime.now() - cache_time).total_seconds() / 3600

                    if age_hours > CACHE_TTL_HOURS:
                        level = 'critical'
                        message = f'🔴 Cached data ({int(age_hours)}h old) - Update needed'
                    else:
                        level = 'warning'
                        message = f'🟡 Using cached data ({int(age_hours)}h old)'

                    return {
                        'data': df,
                        'source': 'cache',
                        'level': level,
                        'message': message
                    }
            except Exception as e:
                logger.warning(f"[{ticker}] Cache failed: {e}")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Level 4: Mock (최후의 수단 - 데모용)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        logger.error(f"[{ticker}] All sources failed - using mock data")
        df = self._generate_mock_price_data(ticker, days)

        return {
            'data': df,
            'source': 'mock',
            'level': 'critical',
            'message': '🔴 No real data available - Mock data used'
        }

    def _add_moving_averages(self, df, close_col='Close'):
        """이동평균선 계산"""
        df['MA5'] = df[close_col].rolling(window=5).mean()
        df['MA20'] = df[close_col].rolling(window=20).mean()
        return df

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 외국인/기관 수급
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_investor_flow(self, ticker, days=3):
        """
        투자자별 수급 데이터

        Returns:
            dict: {
                'data': dict with foreign_net, institution_net,
                'source': str,
                'level': str,
                'message': str
            }
        """
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Level 1: pykrx (유일한 신뢰 가능 소스)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if self.pykrx_available:
            try:
                logger.info(f"[{ticker}] Fetching investor flow from pykrx...")
                end = datetime.now().strftime('%Y%m%d')
                start = (datetime.now() - timedelta(days=days+5)).strftime('%Y%m%d')

                df = self.pykrx.get_market_trading_value_by_date(
                    start, end, ticker, detail=True
                )

                if not df.empty:
                    # 최근 N일 데이터만
                    df_recent = df.tail(days)

                    foreign_sum = df_recent.get('외국인', pd.Series([0])).sum()
                    institution_sum = df_recent.get('기관', pd.Series([0])).sum()

                    result_data = {
                        'foreign_net': float(foreign_sum),
                        'institution_net': float(institution_sum),
                        'days': days,
                        'details': df_recent.to_dict('records') if len(df_recent) > 0 else []
                    }

                    self._save_cache(ticker, 'flow', result_data)

                    return {
                        'data': result_data,
                        'source': 'pykrx',
                        'level': 'success',
                        'message': None
                    }
            except Exception as e:
                logger.warning(f"[{ticker}] pykrx investor flow failed: {e}")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Level 2: Cache
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if self.use_cache:
            try:
                data, cache_time = self._load_cache(ticker, 'flow')
                if data is not None:
                    age_hours = (datetime.now() - cache_time).total_seconds() / 3600

                    return {
                        'data': data,
                        'source': 'cache',
                        'level': 'warning',
                        'message': f'🟡 Cached investor flow ({int(age_hours)}h old)'
                    }
            except Exception as e:
                logger.warning(f"[{ticker}] Cache flow failed: {e}")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Level 3: Mock
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        logger.error(f"[{ticker}] Investor flow not available - using mock")
        import random
        result_data = {
            'foreign_net': random.randint(-100000000, 150000000),
            'institution_net': random.randint(-80000000, 120000000),
            'days': days,
            'details': []
        }

        return {
            'data': result_data,
            'source': 'mock',
            'level': 'critical',
            'message': '🔴 No investor flow data - Mock used'
        }

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 펀더멘털 (PBR/PER)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_fundamental(self, ticker):
        """
        펀더멘털 데이터 (PER, PBR, EPS, BPS)
        """
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Level 1: pykrx
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if self.pykrx_available:
            try:
                logger.info(f"[{ticker}] Fetching fundamental from pykrx...")
                yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')

                df = self.pykrx.get_market_fundamental(yesterday, yesterday, ticker)

                if not df.empty:
                    data_row = df.iloc[0]
                    result_data = {
                        'PER': float(data_row.get('PER', 0)),
                        'PBR': float(data_row.get('PBR', 0)),
                        'EPS': float(data_row.get('EPS', 0)),
                        'BPS': float(data_row.get('BPS', 0)),
                        'DIV': float(data_row.get('DIV', 0))
                    }

                    self._save_cache(ticker, 'fundamental', result_data)

                    return {
                        'data': result_data,
                        'source': 'pykrx',
                        'level': 'success',
                        'message': None
                    }
            except Exception as e:
                logger.warning(f"[{ticker}] pykrx fundamental failed: {e}")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Level 2: 네이버 금융 크롤링
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if self.scraping_available:
            try:
                logger.info(f"[{ticker}] Scraping from Naver Finance...")
                url = f"https://finance.naver.com/item/main.nhn?code={ticker}"
                headers = {'User-Agent': 'Mozilla/5.0'}

                response = self.requests.get(url, headers=headers, timeout=10)
                soup = self.BeautifulSoup(response.text, 'html.parser')

                per_elem = soup.select_one('em#_per')
                pbr_elem = soup.select_one('em#_pbr')

                per = float(per_elem.text.strip()) if per_elem and per_elem.text.strip() != 'N/A' else None
                pbr = float(pbr_elem.text.strip()) if pbr_elem and pbr_elem.text.strip() != 'N/A' else None

                if per or pbr:
                    result_data = {
                        'PER': per,
                        'PBR': pbr,
                        'EPS': None,
                        'BPS': None,
                        'DIV': None
                    }

                    self._save_cache(ticker, 'fundamental', result_data)

                    return {
                        'data': result_data,
                        'source': 'naver_scraping',
                        'level': 'warning',
                        'message': '⚠️ Web scraping used (limited data)'
                    }
            except Exception as e:
                logger.warning(f"[{ticker}] Naver scraping failed: {e}")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Level 3: Cache
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if self.use_cache:
            try:
                data, cache_time = self._load_cache(ticker, 'fundamental')
                if data is not None:
                    age_days = (datetime.now() - cache_time).days

                    return {
                        'data': data,
                        'source': 'cache',
                        'level': 'warning',
                        'message': f'🟡 Cached fundamental ({age_days} days old)'
                    }
            except Exception as e:
                logger.warning(f"[{ticker}] Cache fundamental failed: {e}")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Level 4: Mock
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        logger.error(f"[{ticker}] Fundamental not available - using mock")
        mock_fundamentals = {
            '005930': {'PER': 12.5, 'PBR': 1.15, 'EPS': 5000, 'BPS': 45000, 'DIV': 2.3},
            '105560': {'PER': 7.2, 'PBR': 0.55, 'EPS': 8200, 'BPS': 60000, 'DIV': 4.5},
            '086520': {'PER': 25.3, 'PBR': 3.2, 'EPS': 1500, 'BPS': 12000, 'DIV': 0.5}
        }

        result_data = mock_fundamentals.get(ticker, {
            'PER': 15.0, 'PBR': 1.5, 'EPS': 1000, 'BPS': 10000, 'DIV': 2.0
        })

        return {
            'data': result_data,
            'source': 'mock',
            'level': 'critical',
            'message': '🔴 No fundamental data - Mock used'
        }

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 캐싱 시스템
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _save_cache(self, ticker, data_type, data):
        """캐시 저장"""
        try:
            cache_file = self.cache_dir / f"{ticker}_{data_type}.json"

            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'ticker': ticker,
                'type': data_type,
                'data': self._serialize_data(data)
            }

            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            logger.debug(f"Cache saved: {cache_file}")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")

    def _load_cache(self, ticker, data_type):
        """캐시 로드"""
        try:
            cache_file = self.cache_dir / f"{ticker}_{data_type}.json"

            if not cache_file.exists():
                return None, None

            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            cache_time = datetime.fromisoformat(cache_data['timestamp'])
            data = self._deserialize_data(cache_data['data'], data_type)

            return data, cache_time
        except Exception as e:
            logger.error(f"Failed to load cache: {e}")
            return None, None

    def _serialize_data(self, data):
        """DataFrame을 JSON 직렬화 가능하게 변환"""
        if isinstance(data, pd.DataFrame):
            return {
                'type': 'dataframe',
                'data': data.to_dict('split'),
                'index': [str(idx) for idx in data.index]
            }
        else:
            return {'type': 'dict', 'data': data}

    def _deserialize_data(self, serialized, data_type):
        """JSON에서 원래 형태로 복원"""
        if serialized['type'] == 'dataframe':
            df = pd.DataFrame(**serialized['data'])
            df.index = pd.to_datetime(serialized['index'])
            return df
        else:
            return serialized['data']

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Mock 데이터 생성 (최후의 수단)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _generate_mock_price_data(self, ticker, days=60):
        """Mock 주가 데이터 생성 (데모용)"""
        import random

        base_prices = {
            '005930': 70000,
            '105560': 65000,
            '086520': 85000
        }

        base_price = base_prices.get(ticker, 50000)
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        prices = []
        price = base_price

        for _ in range(days):
            change = random.gauss(0, 0.02)
            price = price * (1 + change)
            prices.append(price)

        df = pd.DataFrame({
            'Open': [p * random.uniform(0.98, 1.02) for p in prices],
            'High': [p * random.uniform(1.0, 1.03) for p in prices],
            'Low': [p * random.uniform(0.97, 1.0) for p in prices],
            'Close': prices,
            'Volume': [random.randint(1000000, 5000000) for _ in prices]
        }, index=dates)

        df = self._add_moving_averages(df)

        return df


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 테스트 코드
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    print("=" * 80)
    print("🧪 DataCollector 테스트")
    print("=" * 80)

    collector = DataCollector()

    # 삼성전자 테스트
    print("\n📊 Test: 삼성전자 (005930)")
    print("-" * 80)

    # 주가
    price_result = collector.get_stock_price('005930', days=60)
    print(f"주가 데이터: {price_result['source']} ({price_result['level']})")
    if price_result['message']:
        print(f"  {price_result['message']}")
    print(f"  데이터 크기: {len(price_result['data'])} rows")

    # 수급
    flow_result = collector.get_investor_flow('005930', days=3)
    print(f"수급 데이터: {flow_result['source']} ({flow_result['level']})")
    if flow_result['message']:
        print(f"  {flow_result['message']}")
    print(f"  외국인 3일: {flow_result['data']['foreign_net']:,.0f}원")

    # 펀더멘털
    fund_result = collector.get_fundamental('005930')
    print(f"펀더멘털: {fund_result['source']} ({fund_result['level']})")
    if fund_result['message']:
        print(f"  {fund_result['message']}")
    print(f"  PBR: {fund_result['data']['PBR']:.2f}")

    print("\n✅ 테스트 완료")
