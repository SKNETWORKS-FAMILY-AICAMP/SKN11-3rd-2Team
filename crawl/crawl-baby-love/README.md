# 아이사랑 포털 크롤링 프로젝트

이 프로젝트는 [임신육아종합포털 아이사랑](https://www.childcare.go.kr/)의 '월령별 성장 및 돌보기' 섹션(menuno=287 ~ 294)의 내용을 크롤링하고 처리하는 파이썬 Playwright 기반 크롤링 도구입니다.

## 기능

- 아이사랑 포털의 '월령별 성장 및 돌보기' 페이지를 크롤링
- 각 페이지의 탭별 내용을 수집
- HTML 내용에서 텍스트 및 구조화된 데이터 추출
- 수집된 데이터를 다양한 형식(Excel, CSV, 텍스트 파일)으로 내보내기

## 설치 요구사항

```bash
pip install pandas openpyxl beautifulsoup4 playwright
playwright install
```

## 프로젝트 구성

- `crawler.py`: Playwright를 이용한 웹 크롤러
- `processor.py`: HTML 데이터 처리 및 구조화
- `exporter.py`: 구조화된 데이터를 다양한 형식으로 내보내기
- `run.py`: 전체 파이프라인 실행 스크립트

## 사용 방법

### 전체 파이프라인 실행
```bash
python run.py
```

### 옵션 지정
```bash
# 크롤링 단계 건너뛰기 (이미 수집된 데이터가 있는 경우)
python run.py --skip-crawl

# 처리 단계 건너뛰기
python run.py --skip-process

# 특정 형식으로만 내보내기
python run.py --format excel
python run.py --format text
python run.py --format csv
```

### 개별 스크립트 실행
```bash
# 크롤링만 실행
python crawler.py

# 데이터 처리만 실행
python processor.py

# 내보내기만 실행
python exporter.py [JSON_파일_경로] --format [excel/text/csv/all]
```

## 데이터 구조

### 크롤링된 원본 데이터 (all_data.json)
```
[
  {
    "menu_num": 287,
    "page_title": "이른둥이",
    "url": "https://www.childcare.go.kr/?menuno=287",
    "tabs": [
      {
        "tab_title": "이른둥이란?",
        "tab_menuno": "418",
        "tab_url": "https://www.childcare.go.kr/?menuno=418",
        "content": "HTML 내용..."
      },
      ...
    ]
  },
  ...
]
```

### 처리된 데이터 (processed_data.json)
```
[
  {
    "menu_num": 287,
    "page_title": "이른둥이",
    "url": "https://www.childcare.go.kr/?menuno=287",
    "tabs": [
      {
        "tab_title": "이른둥이란?",
        "tab_menuno": "418",
        "tab_url": "https://www.childcare.go.kr/?menuno=418",
        "content_text": "추출된 텍스트...",
        "content_structured": {
          "headings": { ... },
          "paragraphs": [ ... ],
          "lists": [ ... ],
          "tables": [ ... ]
        }
      },
      ...
    ]
  },
  ...
]
```
