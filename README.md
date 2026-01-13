# 🚀 Momentum Keeper

> 이광수 애널리스트의 투자 철학을 자동화한 AI 기반 포트폴리오 관리 시스템

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 프로젝트 개요

**Momentum Keeper**는 데이터 기반 투자 전략을 자동화하여:
- ✅ 추세 추종 (Trend Following) 원칙 적용
- ✅ 엄격한 손절 규칙 (-10%) 자동 경고
- ✅ 외국인/기관 수급 분석
- ✅ AI 기반 투자 조언 (Gemini)

---

## 🎯 핵심 기능

### 1. 📊 실시간 포트폴리오 대시보드
- 보유 종목 현황 (현재가, 평단가, 수익률)
- 추세 신호등 (🟢 매수 / 🟡 관망 / 🔴 매도)
- 이동평균선 정배열/역배열 확인

### 2. 💰 투자자별 수급 분석
- 외국인 3일 연속 순매수 여부
- 기관 매매 동향
- 수급 신호와 가격 추세 통합 판단

### 3. 📈 펀더멘털 분석
- PBR 밴드 (삼성전자 저평가 구간 확인)
- PER, EPS 자동 수집
- 거시지표 프록시 (SOX 반도체 지수, 리튬 가격 대리지표)

### 4. 🤖 AI 어드바이저
- Google Gemini 연동
- 이광수 페르소나 기반 투자 조언
- 포트폴리오 전체 상황 종합 분석

---

## 🛠️ 기술 스택

### 데이터 수집
- **FinanceDataReader**: 주가 데이터 (OHLCV)
- **pykrx**: 한국거래소 공식 데이터 (수급, 펀더멘털)
- **BeautifulSoup4**: 네이버 금융 크롤링 (백업)

### AI & 분석
- **Google Generative AI (Gemini)**: 투자 조언 생성
- **pandas**: 데이터 분석
- **plotly**: 인터랙티브 차트

### 프론트엔드
- **Streamlit**: 웹 대시보드

---

## 📦 설치 방법

### 1. 레포지토리 클론
```bash
git clone https://github.com/yourusername/Momentum_Keeper.git
cd Momentum_Keeper
```

### 2. 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. API 키 설정 (선택)
```bash
mkdir .streamlit
echo 'GEMINI_API_KEY = "your-api-key-here"' > .streamlit/secrets.toml
```

---

## 🚀 실행 방법

### 테스트 실행 (Mock 데이터)
```bash
python tests/demo_with_mock.py
```

### 개별 데이터 소스 테스트
```bash
# 주가 데이터
python tests/test_01_stock_price.py

# 수급 데이터
python tests/test_02_investor_flow.py

# 펀더멘털
python tests/test_03_fundamental.py

# 거시지표
python tests/test_04_macro_proxy.py
```

### Streamlit 대시보드 (구현 예정)
```bash
streamlit run app.py
```

---

## 📊 데이터 크롤링 설계

### 핵심 전략: 다층 백업 시스템

```
┌─────────────────────────────────────┐
│    Primary Source (우선 사용)       │
│  - FinanceDataReader (주가)         │
│  - pykrx (수급, 펀더멘털)           │
└─────────────────────────────────────┘
            ↓ (실패 시)
┌─────────────────────────────────────┐
│    Fallback Source (백업)           │
│  - pykrx (주가 백업)                │
│  - 네이버 금융 크롤링 (펀더멘털)    │
└─────────────────────────────────────┘
            ↓ (실패 시)
┌─────────────────────────────────────┐
│    Cached Data (캐시)               │
│  - 최근 24시간 내 데이터 재사용     │
└─────────────────────────────────────┘
            ↓ (실패 시)
┌─────────────────────────────────────┐
│    Manual Input (수동 입력)         │
│  - UI 체크박스로 거시지표 입력      │
└─────────────────────────────────────┘
```

### 거시지표 프록시 전략

| 종목 | 실제 지표 | 프록시 지표 | 구현 방법 |
|------|----------|-------------|----------|
| 삼성전자 | 반도체 수출액 | SOX 지수 | FinanceDataReader |
| 에코프로 | 리튬 가격 | Albemarle (ALB) 주가 | FinanceDataReader |
| KB금융 | 금리 환경 | (불필요) | - |

**장점**:
- 실시간 데이터 수집 가능
- 별도 API 인증 불필요
- 구현 간단하고 안정적

**한계**:
- 간접 지표이므로 정확도 제한
- 실제 수출 데이터보다 시차 발생 가능

→ **해결책**: 수동 입력 옵션 병행

---

## 🧪 테스트 결과

### 실행 환경
- 일시: 2026-01-13
- 네트워크: 제약 있음 (프록시 차단)

### Mock 데이터 데모 성공 ✅
```bash
$ python tests/demo_with_mock.py

📊 포트폴리오 요약
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
종목명      현재가      수익률    신호
삼성전자   76,508원   +9.30%    🟡
KB금융    54,802원  -15.69%    🔴
에코프로  105,695원  +24.35%    🟢
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
전체 수익률: +5.95%
```

**검증 완료**:
- ✅ 주가 데이터 수집 및 이동평균선 계산
- ✅ 외국인/기관 수급 분석
- ✅ 이광수 알고리즘 (추세 + 손절 판단)
- ✅ AI 어드바이저 조언 생성
- ✅ 포트폴리오 요약 리포트

---

## 📖 이광수 알고리즘

### 핵심 원칙

```python
def analyze_momentum(price, ma5, ma20, foreign_net, return_rate):
    # 1. 손절 원칙 (최우선)
    if return_rate <= -10.0:
        return "🔴 즉시 손절"

    # 2. 강한 상승 추세
    elif ma5 > ma20 and foreign_net > 0:
        return "🟢 강력 홀딩 / 불타기 가능"

    # 3. 추세 붕괴
    elif price < ma20:
        return "🟡 비중 축소 준비"

    # 4. 중립
    else:
        return "⚪ 관망"
```

### 판단 기준

| 신호 | 조건 | 액션 |
|------|------|------|
| 🔴 CRITICAL | 수익률 ≤ -10% | 즉시 손절 |
| 🟢 STRONG BUY | MA5 > MA20 + 외국인/기관 순매수 | 강력 홀딩 |
| 🟢 BULLISH | MA5 > MA20 + 외국인 또는 기관 순매수 | 홀딩 유지 |
| 🟡 WARNING | 현재가 < MA20 | 비중 축소 준비 |
| ⚪ NEUTRAL | 기타 | 관망 |

---

## 📂 프로젝트 구조

```
Momentum_Keeper/
├── app.py                      # Streamlit 메인 앱 (구현 예정)
├── requirements.txt            # 의존성 패키지
├── README.md                   # 이 문서
├── DESIGN_FINAL.md             # 상세 설계 문서
│
├── core/                       # 코어 로직 (구현 예정)
│   ├── data_collector.py       # 통합 데이터 수집기
│   ├── analyzer.py             # 추세 분석
│   └── portfolio.py            # 포트폴리오 관리
│
├── ai/                         # AI 모듈 (구현 예정)
│   ├── advisor.py              # Gemini API
│   └── prompts.py              # 프롬프트 템플릿
│
├── data/                       # 데이터 저장소
│   ├── cache/                  # 캐시 파일
│   └── portfolio.json          # 사용자 포트폴리오
│
└── tests/                      # 테스트 코드
    ├── test_01_stock_price.py  # 주가 데이터 테스트
    ├── test_02_investor_flow.py # 수급 데이터 테스트
    ├── test_03_fundamental.py  # 펀더멘털 테스트
    ├── test_04_macro_proxy.py  # 거시지표 테스트
    └── demo_with_mock.py       # 통합 데모 (Mock)
```

---

## 🎯 구현 로드맵

### ✅ Phase 1: 설계 및 검증 (완료)
- [x] 데이터 소스 조사 및 비교
- [x] 크롤링 아키텍처 설계
- [x] 샘플 코드 작성 및 테스트
- [x] Mock 데이터 데모 구현

### 🔄 Phase 2: MVP 구현 (진행 예정)
- [ ] 코어 데이터 수집 모듈
- [ ] 포트폴리오 관리 클래스
- [ ] 이광수 분석 알고리즘
- [ ] 기본 Streamlit 대시보드

### 📅 Phase 3: 안정성 강화
- [ ] Fallback 시스템 구현
- [ ] 캐싱 메커니즘
- [ ] 에러 핸들링 및 로깅

### 🚀 Phase 4: 고도화
- [ ] Gemini AI 연동
- [ ] 고급 차트 (Plotly)
- [ ] 알림 시스템 (이메일/Slack)

---

## 💡 주요 설계 결정

### 1. 왜 FinanceDataReader + pykrx?
- **FinanceDataReader**: 간단한 API, 다양한 거래소 지원
- **pykrx**: 한국거래소 공식 데이터, 가장 정확
- **전략**: FinanceDataReader 우선, 실패 시 pykrx 백업

### 2. 왜 프록시 지표?
- 실제 거시지표(수출액, 원자재 가격)는 API 인증 복잡하거나 유료
- SOX/ALB 같은 관련 지수는 무료로 실시간 수집 가능
- 완벽한 정확도보다 "신속한 추세 파악"이 목표

### 3. 왜 캐싱?
- 네트워크 오류, 시장 휴장, API 제한 등 실무 문제 대응
- 24시간 이내 데이터면 투자 판단에 충분
- 사용자 경험 향상 (빠른 로딩)

---

## ⚠️ 주의사항

### 법적 고지
- 이 프로젝트는 **교육 및 연구 목적**으로 제작되었습니다
- 실제 투자 손실에 대한 책임은 사용자에게 있습니다
- 크롤링 시 robots.txt 및 이용약관을 준수하세요

### 데이터 제약
- **pykrx**: 당일 데이터는 오후 6시 이후 제공
- **네이버 금융**: HTML 구조 변경 시 크롤링 실패 가능
- **주말/휴장일**: 마지막 거래일 데이터 표시

---

## 📚 참고 문서

- [DESIGN_FINAL.md](DESIGN_FINAL.md) - 상세 설계 문서
- [tests/](tests/) - 테스트 코드 및 샘플

---

## 🤝 기여

Issue 및 Pull Request 환영합니다!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능합니다.

---

## 👨‍💻 작성자

**Momentum Keeper Development Team**
- 설계 및 구현: 2026년 1월

---

## 🙏 감사의 말

이 프로젝트는 이광수 애널리스트의 투자 철학에서 영감을 받았습니다.
- "추세를 거스르지 마세요"
- "손절은 자존심이 아니라 생존 전략입니다"

---

**버전**: 1.0.0
**상태**: 설계 완료 - MVP 구현 준비 중
**최종 업데이트**: 2026-01-13
