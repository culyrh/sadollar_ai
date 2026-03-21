# 🍔 Sadollar AI Backend

롯데리아 메뉴 데이터를 기반으로
**메뉴 조회 API + AI 연동용 데이터 시스템**을 구축한 백엔드 프로젝트입니다.

---

## 📌 프로젝트 개요

본 프로젝트는 음성 기반 주문 시스템을 위한 백엔드로,
메뉴 데이터를 수집하고 AI 및 프론트엔드가 사용할 수 있도록 API 형태로 제공합니다.

### 전체 흐름

```text
크롤링 → JSON → SQLite DB → 조회 함수 → FastAPI → AI/프론트
```

---

## ⚙️ 현재 구현 기능

### 1. 데이터 수집 (Crawler)

* 롯데리아 영양성분표 페이지 크롤링
* 메뉴명, 알레르기, kcal, 원산지 정보 수집
* `data/menu.json` 생성

---

### 2. 데이터 저장 (SQLite)

* `menu.json` → `menu.db` 변환
* SQLite 기반 로컬 DB 구성

---

### 3. DB 조회 함수

파일: `db/sqlite.py`

지원 기능:

* 메뉴 목록 조회
* 메뉴 ID 조회
* 메뉴 이름 조회
* 키워드 검색

---

### 4. FastAPI API 서버

#### 📍 엔드포인트

| Method | URL           | 설명       |
| ------ | ------------- | -------- |
| GET    | `/menu`       | 메뉴 목록 조회 |
| GET    | `/menu?q=불고기` | 키워드 검색   |
| GET    | `/menu/{id}`  | 메뉴 상세 조회 |

---

### 5. AI 연동용 Tool

AI 파트에서 DB를 직접 다루지 않고
**함수 형태로 사용할 수 있도록 제공**

#### 사용 예시

```python
from tools.get_menu_by_name import run

run("한우불고기 세트")
```

---

## 📁 프로젝트 구조

```text
sadollar-ai/
│
├── data/
│   ├── menu.json
│   └── menu.db
│
├── ingestion/
│   ├── crawler.py
│   └── sqlite_loader.py
│
├── db/
│   ├── __init__.py
│   └── sqlite.py
│
├── api/
│   ├── __init__.py
│   ├── main.py
│   └── routes/
│       ├── __init__.py
│       └── menu.py
│
├── tools/
│   ├── __init__.py
│   ├── get_menu_by_name.py
│   └── get_menu_detail.py
│
├── requirements.txt
└── test_db.py
```

---

## 🚀 실행 방법

### 1. 프로젝트 클론

```bash
git clone <레포주소>
cd sadollar-ai
```

---

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

---

### 3. 데이터 생성

```bash
python ingestion/crawler.py
```

→ `data/menu.json` 생성

---

### 4. DB 생성

```bash
python ingestion/sqlite_loader.py
```

→ `data/menu.db` 생성

---

### 5. DB 테스트

```bash
python test_db.py
```

---

### 6. 서버 실행

```bash
uvicorn api.main:app --reload
```

---

### 7. 브라우저 확인

* 메뉴 목록:
  http://127.0.0.1:8000/menu

* 메뉴 상세:
  http://127.0.0.1:8000/menu/1

* API 문서 (Swagger):
  http://127.0.0.1:8000/docs

---

## 🤖 AI 파트 사용 가이드

AI 파트는 DB를 직접 접근하지 않고
**tools 폴더의 함수만 사용하면 됩니다.**

### 사용 가능한 함수

```python
from tools.get_menu_by_name import run
from tools.get_menu_detail import run
```

---

### 예시

```python
run("한우불고기 세트")
run(1)
```

---

## 📊 데이터 구조

```json
{
  "id": 1,
  "name": "한우불고기 세트",
  "category": "set",
  "price": null,
  "description": "",
  "image_url": "",
  "is_set_available": 0,
  "spicy_level": 0,
  "allergens": "달걀, 밀, 대두, 우유, 쇠고기, 토마토",
  "kcal": 684,
  "origin_text": "쇠고기 - 국내산 한우",
  "raw_source": "nutrition_page"
}
```

---

## ⚠️ 현재 데이터 한계

* 가격 없음 (`price = None`)
* 설명 없음 (`description = ""`)
* 이미지 없음 (`image_url = ""`)
* 검색은 단순 LIKE 기반 (semantic search 미적용)

---

## 🔜 향후 개발 예정

* ChromaDB 기반 의미 검색 (AI 추천 강화)
* 장바구니 API
* 주문 API
* 옵션 변경 기능
* 음성(STT/TTS) 통합

---

## 💡 역할 분리

| 역할  | 담당              |
| --- | --------------- |
| 백엔드 | 데이터 저장 및 조회 API |
| AI  | 의도 이해 및 tool 호출 |
| 프론트 | UI 및 사용자 입력     |

---

## 🧾 한 줄 요약

👉 **AI가 사용할 메뉴 데이터베이스 + 조회 API를 구축한 상태**

---

## 🙌 작성자

Sadollar AI Backend
