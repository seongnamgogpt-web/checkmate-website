# Check Mate - 수행평가 초안 검사 웹 앱

## 📚 프로젝트 소개
Check Mate는 학생들이 수행평가 초안이 평가 조건에 부합하는지 자동으로 검사하는 AI 기반 웹 애플리케이션입니다.

### 🎯 주요 목표
- 학생들이 수행평가에서 조건 누락으로 인한 감점을 예방
- 효율적인 검토를 통한 학습 효과 증대
- AI 기반 문장 분석을 통한 문맥 이해와 논리적 흐름 검토

## 🛠 기술 스택
- **Backend**: Python
- **AI/LLM**: LangChain + Google Gemini
- **Frontend**: Streamlit
- **이미지 처리**: Pillow, pytesseract (OCR)

## 🚀 설치 및 실행 방법

### 1. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정
`.env` 파일을 생성하고 Google Gemini API 키를 설정하세요:
```
GOOGLE_API_KEY=your_google_api_key_here
```

### 3. 애플리케이션 실행
```bash
streamlit run app.py
```

## 📖 사용법

### 입력 방법
1. **수행평가 요구조건**: 텍스트 직접 입력 또는 파일/이미지 업로드
2. **수행평가 결과물**: 텍스트 직접 입력 또는 파일/이미지 업로드

### 출력 결과
- 조건별 충족 여부 체크리스트
- 총점 및 세부 점수
- 개선점 제안
- 이메일 공유 기능

## 📁 프로젝트 구조
```
checkmate/
├── app.py              # 메인 애플리케이션
├── utils/
│   ├── __init__.py
│   ├── image_processor.py  # 이미지 처리 및 OCR
│   ├── ai_analyzer.py      # AI 분석 로직
│   └── email_sender.py     # 이메일 공유 기능
├── requirements.txt    # 필요한 패키지 목록
├── .env               # 환경 변수 (API 키 등)
└── README.md          # 프로젝트 설명서
```
