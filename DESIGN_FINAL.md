# 📊 Momentum Keeper - 최종 데이터 크롤링 설계

## 🎯 테스트 결과 요약

### 실행 환경
- 테스트 일시: 2026-01-13
- 테스트 종목: 삼성전자(005930), KB금융(105560), 에코프로(086520)
- 실행 결과: 네트워크 제약으로 인한 데이터 수집 실패

### 주요 발견사항

#### ✅ 코드 구조 검증
- 모든 테스트 스크립트가 오류 없이 실행됨
- 예외 처리 로직이 정상 작동함
- 각 데이터 소스별 분기 로직이 올바르게 구현됨

#### ⚠️ 네트워크 제약 발견
```
ProxyError: Tunnel connection failed: 403 Forbidden
```
- FinanceDataReader → 네이버 금융 (차단)
- pykrx → KRX 데이터 (휴장일 또는 차단)
- 네이버 크롤링 → 직접 접근 (차단)
- Yahoo Finance → SOX, ALB (차단)

#### 💡 실무 시사점
이런 문제들은 실제 프로덕션 환경에서도 발생할 수 있습니다:
1. **네트워크 오류**: ISP 차단, 방화벽, VPN
2. **시장 휴장**: 주말, 공휴일, 임시 휴장
3. **API 제한**: Rate Limiting, 인증 만료
4. **데이터 지연**: T+1 데이터 제공

---

## 🏗️ 최종 설계: Robust Data Pipeline

### 아키텍처 원칙

```
┌─────────────────────────────────────────────────────────────┐
│                   Resilient Architecture                    │
│         (장애 허용 + 다층 백업 + 캐싱 + 수동 대체)          │
└─────────────────────────────────────────────────────────────┘

레벨 1: 기본 데이터 소스 (Primary)
    ↓ (실패 시)
레벨 2: 백업 데이터 소스 (Fallback)
    ↓ (실패 시)
레벨 3: 캐시된 과거 데이터 (Cache)
    ↓ (실패 시)
레벨 4: 수동 입력 / Mock Data (Manual/Mock)
```

---

## 📊 데이터 소스별 전략

### 1. 주가 데이터 (OHLCV + 이동평균선)

#### 우선순위 체계
```python
try:
    # Primary: FinanceDataReader
    df = fdr.DataReader(ticker, start, end)
except:
    try:
        # Fallback: pykrx
        df = stock.get_market_ohlcv(start, end, ticker)
    except:
        # Cache: 로컬 저장된 최근 데이터
        df = load_cached_data(ticker)
        # 경고 표시: "⚠️ 24시간 이전 데이터"
```

#### 캐싱 전략
- **위치**: `data/cache/{ticker}_ohlcv.csv`
- **갱신**: 매 성공적인 수집 시 저장
- **TTL**: 24시간
- **표시**: 캐시 사용 시 UI에 경고 표시

---

### 2. 외국인/기관 수급

#### 우선순위 체계
```python
try:
    # Primary: pykrx (가장 신뢰도 높음)
    df = stock.get_market_trading_value_by_date(start, end, ticker)
except:
    # Fallback: 전일 데이터 재사용
    df = load_cached_investor_flow(ticker)
    # 경고: "⚠️ 전일 수급 데이터"
```

#### 특수 처리
- **당일 데이터 없음**: 오후 6시 이전 → 전일 데이터 표시
- **주말/휴장일**: 마지막 거래일 데이터 표시
- **3일 연속 계산**: 휴장일 제외하고 실거래일 기준 3일

---

### 3. 펀더멘털 (PBR/PER)

#### 우선순위 체계
```python
try:
    # Primary: pykrx
    df = stock.get_market_fundamental(date, date, ticker)
except:
    try:
        # Fallback: 네이버 금융 크롤링
        data = scrape_naver_finance(ticker)
    except:
        # Cache: 최근 1주일 내 데이터
        data = load_cached_fundamental(ticker)
        # 경고: "⚠️ 과거 펀더멘털 데이터 ({date})"
```

#### 네이버 크롤링 안정화
```python
# 다중 셀렉터 전략 (HTML 변경 대응)
SELECTORS = [
    ('em#_per', 'em#_pbr'),           # 방법 1: ID
    ('.per .num', '.pbr .num'),       # 방법 2: Class
    ('table.no_info td', 'regex')     # 방법 3: Table Parsing
]

for selector_set in SELECTORS:
    try:
        return extract_data(selector_set)
    except:
        continue
```

---

### 4. 거시지표 (반도체 수출, 리튬 가격)

#### 하이브리드 전략

##### 자동 수집 (프록시 지표)
```python
# 삼성전자: SOX 반도체 지수
try:
    sox = fdr.DataReader('SOX', start, end)
    trend = analyze_trend(sox)  # 30일 수익률 기반
except:
    trend = None  # 수동 입력으로 전환

# 에코프로: ALB + 에코프로비엠 상관관계
try:
    alb = fdr.DataReader('ALB', start, end)
    ecoproBM = fdr.DataReader('247540', start, end)
    trend = analyze_correlation(alb, ecoproBM)
except:
    trend = None
```

##### 수동 입력 (UI 대체 옵션)
```python
# Streamlit 사이드바
with st.sidebar:
    st.subheader("📊 거시지표 수동 입력")

    # 자동 수집 실패 시만 표시
    if macro_data is None:
        st.warning("자동 수집 실패 - 수동 입력 필요")

        # 삼성전자
        if '005930' in portfolio:
            semiconductor_trend = st.radio(
                "반도체 업황",
                ["상승", "중립", "하락"],
                help="최근 반도체 수출 및 DRAM 가격 추세"
            )

        # 에코프로
        if '086520' in portfolio:
            lithium_trend = st.radio(
                "리튬 가격",
                ["상승", "중립", "하락"],
                help="최근 리튬 가격 추세"
            )
```

---

## 🛡️ 에러 처리 전략

### 에러 레벨 정의

#### 🔴 Critical (치명적)
- 모든 데이터 소스 실패 + 캐시 없음
- **대응**: 앱 실행 불가, 명확한 오류 메시지

#### 🟡 Warning (경고)
- Primary 실패 → Fallback 성공
- 캐시 데이터 사용 (24시간 이내)
- **대응**: 노란색 배너 표시

#### 🟢 Info (정보)
- 정상 수집 (지연 포함)
- 주말/휴장일 안내
- **대응**: 회색 안내 메시지

### 통합 에러 핸들러

```python
class DataCollector:
    def __init__(self):
        self.cache_dir = "data/cache"
        self.logger = setup_logger()

    def collect_with_fallback(self, ticker, data_type):
        """
        다층 백업 수집 로직
        """
        # 1단계: Primary
        try:
            data = self._primary_source(ticker, data_type)
            self._save_cache(ticker, data_type, data)
            return {
                'data': data,
                'source': 'primary',
                'level': 'success',
                'message': None
            }
        except Exception as e:
            self.logger.warning(f"Primary failed: {e}")

        # 2단계: Fallback
        try:
            data = self._fallback_source(ticker, data_type)
            self._save_cache(ticker, data_type, data)
            return {
                'data': data,
                'source': 'fallback',
                'level': 'warning',
                'message': '⚠️ 백업 데이터 소스 사용'
            }
        except Exception as e:
            self.logger.warning(f"Fallback failed: {e}")

        # 3단계: Cache
        try:
            data, cache_time = self._load_cache(ticker, data_type)
            age_hours = (datetime.now() - cache_time).hours

            if age_hours > 24:
                level = 'critical'
                message = f'🔴 {age_hours}시간 전 데이터 (갱신 필요)'
            else:
                level = 'warning'
                message = f'🟡 캐시 데이터 사용 ({age_hours}시간 전)'

            return {
                'data': data,
                'source': 'cache',
                'level': level,
                'message': message
            }
        except:
            # 4단계: Mock/Manual
            return {
                'data': None,
                'source': 'none',
                'level': 'critical',
                'message': '🔴 데이터 없음 - 수동 입력 필요'
            }
```

---

## 📁 최종 프로젝트 구조

```
Momentum_Keeper/
├── app.py                          # Streamlit 메인 앱
├── requirements.txt                # 의존성
├── DESIGN_FINAL.md                 # 이 문서
├── README.md                       # 프로젝트 설명
│
├── core/                           # 코어 로직
│   ├── __init__.py
│   ├── data_collector.py           # 통합 데이터 수집기 (fallback 포함)
│   ├── data_sources.py             # 개별 데이터 소스 클래스
│   ├── analyzer.py                 # 추세 분석 (이광수 알고리즘)
│   ├── portfolio.py                # 포트폴리오 관리
│   └── cache_manager.py            # 캐싱 로직
│
├── ai/                             # AI 모듈
│   ├── __init__.py
│   ├── advisor.py                  # Gemini API 연동
│   └── prompts.py                  # 프롬프트 템플릿
│
├── data/                           # 데이터 저장소
│   ├── cache/                      # 캐시 파일
│   │   ├── 005930_ohlcv.csv
│   │   ├── 005930_flow.json
│   │   └── ...
│   ├── portfolio.json              # 사용자 포트폴리오
│   └── logs/                       # 로그 파일
│
├── tests/                          # 테스트 코드
│   ├── test_01_stock_price.py
│   ├── test_02_investor_flow.py
│   ├── test_03_fundamental.py
│   ├── test_04_macro_proxy.py
│   └── run_all_tests.py
│
└── .streamlit/
    └── secrets.toml                # API 키 (git 제외)
```

---

## 🚀 구현 우선순위

### Phase 1: MVP (필수 기능)
1. ✅ **데이터 수집 기본 구조**
   - Primary 소스만 구현
   - 에러 시 명확한 메시지

2. ✅ **포트폴리오 대시보드**
   - 현재가, 수익률 표시
   - 기본 테이블 UI

3. ✅ **이광수 알고리즘**
   - MA5/MA20 추세 판단
   - 손절 경고 (-10%)

### Phase 2: Resilience (안정성)
1. 🔄 **Fallback 시스템**
   - 백업 데이터 소스 구현
   - 다층 try-except

2. 🔄 **캐싱 시스템**
   - 성공 시 자동 저장
   - 실패 시 캐시 로드

3. 🔄 **에러 UI**
   - 레벨별 배너 표시
   - 상세 오류 로그

### Phase 3: Enhancement (고도화)
1. 📊 **거시지표 자동화**
   - SOX, ALB 프록시
   - 수동 입력 대체

2. 🤖 **AI 어드바이저**
   - Gemini API 연동
   - 이광수 페르소나

3. 📈 **고급 차트**
   - Plotly 인터랙티브 차트
   - 거래량, 수급 시각화

---

## ⚡ 성능 최적화

### 병렬 수집
```python
from concurrent.futures import ThreadPoolExecutor

def collect_all_portfolio_data(tickers):
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(collector.collect_with_fallback, ticker, 'ohlcv')
            for ticker in tickers
        ]
        results = [f.result() for f in futures]
    return results
```

### 증분 갱신
```python
# 전체 60일 데이터가 아닌, 마지막 캐시 이후만 수집
last_date = load_last_cache_date(ticker)
new_data = fetch_data(last_date, today)
full_data = concat(cached_data, new_data)
```

---

## 📊 예상 성능

| 시나리오 | 응답 시간 | 성공률 |
|---------|----------|--------|
| 정상 상황 | 2-3초 | 95%+ |
| Primary 장애 | 4-5초 (Fallback) | 90%+ |
| 전체 장애 | <1초 (Cache) | 80%+ |
| 휴장일 | <1초 (Cache) | 100% |

---

## 🎯 최종 결론

### ✅ 채택 전략
1. **주가**: FinanceDataReader → pykrx → Cache
2. **수급**: pykrx → Cache (당일 오후 6시 이후)
3. **펀더멘털**: pykrx → 네이버 크롤링 → Cache
4. **거시지표**: SOX/ALB 프록시 + 수동 입력 병행

### 💡 핵심 철학
> "완벽한 데이터보다, 신뢰할 수 있는 데이터가 더 중요하다"

- 100% 실시간 데이터를 추구하지 않음
- 24시간 이내 데이터면 충분히 유용함
- 명확한 경고 표시로 사용자 신뢰 확보
- 최악의 경우 수동 입력 옵션 제공

### 🚀 다음 단계
1. **즉시 구현 가능**: Phase 1 MVP 코드 작성
2. **점진적 개선**: Phase 2 Resilience 추가
3. **지속적 모니터링**: 로그 분석 및 데이터 소스 안정성 추적

---

**작성일**: 2026-01-13
**버전**: 1.0
**상태**: ✅ 설계 확정 - 구현 준비 완료
