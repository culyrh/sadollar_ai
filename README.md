# sadollar-ai — feat/audio-processing

키오스크의 음성 처리(STT/TTS) 모듈 구현 브랜치입니다.

- **STT**: 허깅페이스 Whisper 모델 로컬 추론 (faster-whisper)
- **TTS**: 구현 예정

---

### 1. 가상환경 생성 및 활성화

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

<br>

## STT (음성 인식)

허깅페이스 허브에서 Whisper 모델을 로컬로 다운로드해 추론합니다. OpenAI API를 사용하지 않습니다.

- 모델: `Systran/faster-whisper-{size}`
- 처음 실행 시 자동 다운로드, 이후 캐시에서 로드

### 모델 크기 선택

| 모델 | 다운로드 크기 | 속도 | 한국어 정확도 |
|------|-------------|------|--------------|
| small | ~500MB | 빠름 | 보통 |
| medium | ~1.5GB | 중간 | 좋음 |
| large-v3 | ~3GB | 느림 | 매우 좋음 |
| large-v3-turbo | ~1.6GB | 중간 | 매우 좋음 |

### 녹음파일 인식

```bash
# 기본 (medium 모델)
python voice/stt.py tests/뉴스녹음.m4a

# 모델 크기 지정
python voice/stt.py tests/뉴스녹음.m4a small
python voice/stt.py tests/뉴스녹음.m4a large-v3
python voice/stt.py tests/뉴스녹음.m4a large-v3-turbo
```

결과는 터미널에 출력되고 `tests/results/` 에 텍스트 파일로 저장됩니다.

```
tests/results/뉴스녹음_medium_20260326_210639.txt
```

### 실시간 음성 인식

마이크로 말하면 발화가 끝나는 시점을 자동으로 감지해 바로 인식합니다.

```bash
# 기본 (small 모델, 한국어)
python voice/stt_realtime.py

# 옵션 지정
python voice/stt_realtime.py --model small --device cpu --language ko

# 주변 소음이 많을 때 (임계값을 높여 잡음 오인식 방지)
python voice/stt_realtime.py --threshold 0.03
```

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `--model` | `small` | 모델 크기 (tiny / small / medium / large-v3) |
| `--device` | `cpu` | 추론 장치 (cpu / cuda) |
| `--language` | `ko` | 인식 언어 코드 |
| `--threshold` | `0.01` | 음성 감지 민감도 — 낮을수록 민감, 높을수록 잡음 무시 |

실행하면 마이크 대기 상태가 되고, 말을 마치면 약 0.8초 무음 후 자동으로 인식해 출력합니다.

```
[실시간 STT] 마이크 대기 중... (Ctrl+C로 종료)

[인식] 안녕하세요, 주문하고 싶어요.
      (1.23초)
```

`Ctrl+C` 로 종료합니다.

<br>

## 프로젝트 구조

```
sadollar-ai/
│
├── data/
│   ├── menu.json              # 크롤링 결과물
│   ├── menu.db                # SQLite DB 파일
│   └── chroma/                # ChromaDB 저장 디렉토리
│
├── ingestion/                 # [사전 준비] 1회성 파이프라인
│   ├── crawler.py             # 롯데리아 크롤링 (BS4/Selenium)
│   ├── sqlite_loader.py       # menu.json → SQLite
│   └── chroma_loader.py       # menu.json → 임베딩 → ChromaDB
│
├── db/
│   ├── sqlite.py
│   └── chroma.py
│
├── tools/
│   ├── search_menu.py         # ChromaDB 시맨틱 검색
│   ├── get_menu_by_name.py    # SQLite 이름 정확 조회
│   └── get_menu_detail.py     # SQLite 상세 정보 조회
│
├── agent/
│   ├── react_agent.py         # ReAct 루프 구현
│   └── prompts.py             # 시스템 프롬프트
│
├── voice/
│   ├── stt.py                 # Whisper STT (파일 인식)
│   ├── stt_realtime.py        # Whisper STT (실시간 마이크 인식)
│   └── tts.py                 # TTS
│
├── api/
│   ├── main.py
│   └── routes/
│       ├── order.py           # POST /order
│       └── menu.py            # GET /menu, GET /menu/{id}
│
├── config.py
├── main.py
└── requirements.txt
```
