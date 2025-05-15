# SKN 11기 3차 프로젝트

## 👥 팀 소개
### 팀명
#### 마파덜
마더, 파더의 부담을 덜어주는 챗봇
### 팀 멤버

| 김형주 | 신준희 | 이 근 | 이현대 | 이현민 |
|:-----:|:-----:|:-----:|:-----:|:-----:|
| <img src="https://i.namu.wiki/i/j0S1ukGRi1C_AAeQDIHrt30cuQDVYwruBJRWpekny99aQKzDbX1PSmS51efVPDepp_e1oAuLdH_8QvDqSrX7uAnfQOZyHyLW1GFi_XnWEwMWKzpXFBikJ3qTXV6Q2qVb7pEgO0HiiWtjuYKpk-kZNA.webp" width="100"/> | <img src="https://i.namu.wiki/i/NWbxBpJRCVvReBHcxM_bQOxTAmPBkas_l4jeIkfzGdyWglEXS92QXOqzN17RGMBMweMKmtf7tD4VOkv_pmKlX5mE0l3AomEHKyfdeHOq7TAqfFho31hMxxhG2_GMKkhxG3yncu3NkfVbZQVfmXWG9Q.webp" width="100"/> | <img src="https://i.namu.wiki/i/gGhk93pYotJkQQ2VcOfDcPG4wNp8J7uJriA-53YImeg6qaixQIQoj6TnveA4IHm2Rz6j0OAwIFbA1IgoxlNsO2_Ak7le4L2j4tOuBiPg7enEPb65dr6eT8yL0apBaEPzPc2s_GWYDp8a6dp4kbOyOg.webp" width="100"/> | <img src="https://i.namu.wiki/i/rlaXL6whktZVwfLOV0pPQnbHEKCaFI9wfeVpD-mTYf0K5t-G09AQOOO7UPpZMWV_2l3ePEOIDVqA4rXLPHKxdDa-SPHOnk4dyW1JF3r6FyZq-KE-YJxQYLMrCCeENqocCrA7PK6GX3KZIoC-Daq8Hg.webp" width="100"/> | <img src="https://i.namu.wiki/i/mAdeCVXZSBD17XnMVl315reuLuA92ywvT9zIUV2XCnGtfFQz3KJy4dBGnv7y0NZDxfi7PJw4LApnXot6UWgewgi2CADirduSlRAdrJhnY4NSV7wYKOC8qV76M4No3Rcb10FYisJC8AC8p6ttAGeeDw.webp" width="100"/> |
| [@형주핑](https://github.com/Kim-Hyeong-Ju) | [@준희핑](https://github.com/hybukimo) | [@근핑](https://github.com/REROUN) | [@현대핑](https://github.com/kicet3) | [@현민핑](https://github.com/hyunmin6109) |

## 프로젝트 개요
### 👨‍🍼 프로젝트명
초보 부모들의 육아를 도와주는 ***마파덜***

### 📆 프로젝트 기간
2025-05-02 ~ 2025-05-15

### 📌 프로젝트 소개

초보 부모의 육아 고민을 덜어주는 의료 기반 AI 챗봇입니다.  
간단한 질문으로도 믿을 수 있는 정보를 쉽고 빠르게 제공합니다.

### ❗ 프로젝트 필요성

- 저출산 시대가 지속되는 한국 사회에서 초보 부모들은 육아에 대한 정보 부족과 불안을 동시에 겪고 있습니다.
- 특히 의료적 문제는 검색만으로 해결하기 어려워, 신뢰할 수 있는 조언이 절실한 상황입니다.
- 전문적인 의료 기반 정보를 쉽게 제공하는 육아 챗봇이 그 해답이 될 수 있습니다.

### 🎯 프로젝트 목표

- 초보 부모들이 겪는 의료적 육아 고민을 신속하고 정확하게 해결할 수 있도록 지원합니다.  
- 공신력 있는 문서를 기반으로 한 AI 챗봇을 구축하여 사용자 신뢰도를 확보합니다.  
- 누구나 쉽게 접근할 수 있는 웹 기반 플랫폼을 통해 육아 정보의 격차를 해소합니다.


## ⚒️ 기술 스택

| 카테고리 | 기술 스택 |
|:---------:|:-----------:|
| 사용 언어 | <img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white" height="20"/> <img src="https://img.shields.io/badge/javascript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=white" height="20"/> |
| 데이터 크롤링 | <img src="https://img.shields.io/badge/playwright-0ABF53?style=for-the-badge" height="20"/> |
| Vector DB | <img src="https://img.shields.io/badge/faiss-FF6600?style=for-the-badge" height="20"/> <img src="https://img.shields.io/badge/chroma-19216C?style=for-the-badge" height="20"/> |
| LLM 모델 | <img src="https://img.shields.io/badge/koalpaca-6B46C1?style=for-the-badge" height="20"/> |
| UI | <img src="https://img.shields.io/badge/streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" height="20"/> |


## 🤖 사용 모델

### LLM 모델
- **KoAlpaca** ([beomi/KoAlpaca-Polyglot-5.8B](https://huggingface.co/beomi/KoAlpaca-Polyglot-5.8B))
  - LLAMA (영-한 모델) + Polyglot-ko (한국어 모델)
  - [KoAlpaca Git Hub 링크](https://github.com/Beomi/KoAlpaca)

### NLP 모델
- **BERT**
  - 양방향 Transformer 모델

- **BleuRT**
  - BERT 모델을 위키피디아 문장으로 학습시킨 자동 평가 지표 모델

- **Sentence BERT (SBERT)**
  - BERT 모델의 문장 임베딩 성능을 우수하게 향상시킨 모델

- **RoBERTa**
  - BERT 모델을 더 잘 학습시킬 수 있는 레시피로 학습시킨 모델
  - Zeroshot Pipeline을 사용하여 BERT 모델에 학습되지 않은 특정 도메인에 잘 적응할 수 있게 만든 모델

### 임베딩 모델
- **OpenAI Embedding**
- koBERT, BERT 등 사용해봤지만 성능이 좋지 못했음.

### LLM 모델 선정 이유

1. 다른 한국어 모델에 비해 한국어 처리 능력이 뛰어남.
2. 한국어 QA에 특화되어 있어 프로젝트 목적과 가장 잘 맞는 모델

## 시스템 아키텍쳐
<img width="937" alt="image" src="https://github.com/user-attachments/assets/b66d665f-857e-4d08-a3f8-688c37630c5c" />

## 📜요구사항 명세서

| 대분류       | RQ_ID     | 기능 명칭               | 구현 기능                                           | 추가 설명 |
|--------------|-----------|------------------------|----------------------------------------------------|------------|
| **데이터 수집** |
| 데이터 수집 | FDATA_01  | 네이버 카페 게시글 크롤러 제작       | 전체 게시판 기준으로 범용적인 네이버 게시판 크롤러 제작  | 네이버 카페 게시글 크롤링 |
| 데이터 수집 | FDATA_02  | 아이사랑 사이트 육아 정보 크롤러 제작  | 아이 사랑 사이트의 육아 정보 크롤러 제작  | 아이사랑 사이트 크롤링 |
| **시스템 구성** |
| 시스템 구성   | SYSTEM_01  | 문서 기반 질의응답       | 질문 관련 문서 검색 후 응답 생성                        | 크롤링된 HTML 데이터 기반 응답 |
| 시스템 구성   | SYSTEM_02  | Vector DB 문서 임베딩    | ChromaDB 및 FAISS로 문서 벡터화 및 검색                | RAG용 사전 구축 완료 |
| 시스템 구성   | SYSTEM_03  | 문서 메타데이터 구조화    | 발달시기, 카테고리 등 정보 구조화 포함                  | 응답 근거로 명시 가능 |
|**모델 생성**   |
| 모델 생성     | MODEL_01   | 파인튜닝 모델 생성       | KoAlpaca 로컬 모델 생성                           | LoRA 기반 파인튜닝 적용 |
|**응답 생성**   |
| 응답 생성     | FLLM_02   | Vector DB 기반 응답 시스템 | Vector DB 기반 응답 기능 구현               | 크롤링으로 수집된 데이터를 기반으로 만들어진 Vector DB 기반 응답 시스템 |
| 응답 생성     | FLLM_02   | 파인 튜닝 모델 응답 시스템 | 파인 튜닝된 모델을 통해 단순 응답 기능 구현               | 질문 답변 기반의 크롤링 데이터로 파인 튜닝된 모델을 바탕으로 육아에 특화된 응답 시스템 |
|**인터페이스**|
| 인터페이스   | FWEB_01   | 채팅 UI                 | Streamlit 기반 채팅 구성                              | 직관적인 UX 유지 |


<br>

## WBS

| Phase                | Task               | 담당자       | 기간          | 진척율 |
|----------------------|--------------------|--------------|-------------- |--------|
| 주제 선정             | 주제 선정          | ALL          | 05.02 - 05.07 | 완료 |
| 데이터 수집 및 처리   | 데이터 크롤링       | ALL          | 05.07 - 05.12 | 완료 |
|                      | 데이터 정제        | ALL           | 05.12 - 05.13 | 완료 |
| 모델 설계 및 학습     | 모델 선정          | ALL           | 05.13         | 완료 |
|                      | 파인튜닝           | 이현대, 이현민 | 05.14         | 완료 |
|                      | 평가 및 테스트     | 이 근, 이현대  | 05.14 - 05.15 | 완료 |
| 문서 검색 시스템(POC) | 임베딩 모델 적용    | 김형주, 신준희 | 05.14         | 완료 |
|                      | Vector DB 구축     | 김형주, 신준희 | 05.14        | 완료 |
| 중간 발표 시연 페이지 | UI/UX 설계          | ALL          | 05.14        | 완료 |
|                      | Streamlit 구현     | 김형주, 이현대, 이현민 | 05.14        | 완료 |
| 중간 발표 문서화      | README 작성        | 김형주, 신준희 | 05.14        |      |
| 중간발표             | 발표 및 시연        | 이현대        | 05.15        | - |
|프론트엔드 구축| 미정 | - | - | - |
|백엔드 구축| 미정 | - | - | - |
|최종발표 문서화| 미정 | - | - | - |
|최종발표| 발표 및 시연 | - | 06.10 | - |
<br>

## 수집한 데이터 및 전처리

### 1. 데이터 수집
- 약 60,000개의 맘카페 게시글 및 댓글
- [아이사랑 포털 월령별 성장 및 육아](https://www.childcare.go.kr/?menuno=286)

### 2. 데이터 정제

**공통된 작업**
1. Escape Sequence 제거 ('\n', '\t' 등)

**1. 맘카페 게시글 및 댓글**

1. 주제와 관련 없는 카테고리의 게시물 제거 (공지사항, 광고, 이벤트 등)

2. 질문(게시글)과 답변(댓글) 구조로 json 구조 변경

3. 정보만 있는 게시물은 댓글 데이터 없이 따로 json 파일로 분리

    3-1. 라벨링 작업 (정보 / 비정보)

**2. 아이사랑 포털 데이터**

1. 표 데이터는 텍스트 데이터로 변환

2. 메타데이터로 변환

## VectorDB 구현
### Vector DB
[Vector DB Google Drive](https://drive.google.com/drive/folders/1bYmnzLqvDnDc01CPNEWlfZ63LH-KkGbN?usp=sharing)

### Model
[HggingFace](https://huggingface.co/Snowfall0601/finetuned-koalpaca-5.8B/tree/main)

## 테스트 계획 및 결과
### 계획
1. 수집된 데이터의 질문과 답변 데이터를 바탕으로 질문을 했을때 유사한 답변을 하는지 확인
2. Vector DB 데이터를 바탕으로 응답 여부 확인

## 진행 과정 중 프로그램 개선
1. 네이버 크롤러 제작 후 수집된 카테고리 데이터가 부족하여 추가 크롤러를 제작하여 데이터 매핑 
2. 문장 유사도는 문장의 빈도수, 문장의 벡터값과 비교하기에 같은 단어가 있어도 유사도 높음 -> zeroshot pipline을 통해 특정 도메인과 일치하는 문장만 추출
3. 문장 유사도를 1차적으로 개선하기 위해 수작업으로 게시판 이름을 바탕으로 정보글과 질문글 분류
4. 파인튜닝 과정에서 나온 결과물인 모델의 토크나이저가 정상적이지 않음 -> 베이스 모델의 토크나이저를 사용하여 모델 성능 개선
5. 모델의 용량은 크지만 런팟은 재구동시 데이터가 휘발 되는 특성을 보완하고자 huggingface에 모델을 업로드하여 cloud 기반으로 모델 관리


## 수행 결과



## 테스트 및 시연



## 프로젝트 회고

|   이름   |    내용    | 
|---------|------------|
|**김형주**| 크롤링한 정제되지 않은 데이터를 정제하며 그 과정에서 많은 어려움과 배움이 있었고, LLM 모델을 선정하는 첫 단계부터 파인튜닝과 Vector DB 연동 등 여러 과정을 해보면서 팀원들의 도움이 없었다면 포기할뻔 했지만 팀원들 덕분에 잘 마무리 할 수 있었습니다. 감사합니다. |
|**신준희**| 크롤링한 데이터를 정제하는데 많은 노력을 했습니다. 특히 비문이나 불용어 처리에 많이 했습니다. 데이터 임베딩과 벡터 DB에 저장하는 과정과 파인튜닝을 거치면서 NLP과 LLM 모델에 대해 많이 알게 되었습니다. |
|**이 근**| NLP 모델과 koalpaca 모델을 다뤄보았으며 LLM의 fine-tuning과 NLP 모델의 활용에 대해 배울 수 있어 매우 흥미롭고 도움이 되는 프로젝트였습니다. |
|**이현대**| 비정제 데이터인 네이버 카페 데이터를  크롤링 및 NLP를 통한 전처리를 과정이 적절하게 이루어져 파인 튜닝이 성공적으로 이루어 졌습니다. 또한 각자 역할 분배가 잘 이루어져 가장 무난하게 진행한 프로젝트였습니다. |
|**이현민**| 이번 프로젝트를 통해 파인튜닝은 단순한 문장 재현이 아닌, 맥락과 의도를 학습하는 과정임을 체감했습니다. 직접 NLP 애플리케이션의 개발 전 과정을 직접 경험함으로써, 자연스럽게 전체적인 개발 흐름에 대한 감을 잡을 수 있었던 점도 의미 있는 경험이었습니다. |
