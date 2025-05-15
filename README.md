# SKN 11기 3차 프로젝트

## 👥 팀 소개
### 팀명
#### 마파덜

### 팀 멤버

| 형주핑 (해핑) | 준희핑 | 근핑 | 현대핑 | 현민핑 (나그네핑) |
|:-----:|:-----:|:-----:|:-----:|:-----:|
| <img src="https://avatars.githubusercontent.com/u/00000001?v=4" width="100"/> | <img src="https://avatars.githubusercontent.com/u/00000002?v=4" width="100"/> | <img src="https://avatars.githubusercontent.com/u/00000003?v=4" width="100"/> | <img src="https://avatars.githubusercontent.com/u/00000004?v=4" width="100"/> | <img src="https://avatars.githubusercontent.com/u/00000005?v=4" width="100"/> |
| [@김형주](https://github.com/Kim-Hyeong-Ju) | [@신준희](https://github.com/hybukimo) | [@이근](https://github.com/REROUN) | [@이현대](https://github.com/kicet3) | [@이현민](https://github.com/hyunmin6109) |


## 프로젝트 개요

### 👨‍🍼 프로젝트명
초보 부모들의 육아를 도와주는 ***파파봇***

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

**사용 언어** : <img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white" height="25"/> <img src="https://img.shields.io/badge/javascript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=white" height="25"/>

**Data** : <img src="https://img.shields.io/badge/playwright-000000?style=for-the-badge&logo=chroma&logoColor=white" height="25"/> <img src="https://img.shields.io/badge/chroma-000000?style=for-the-badge&logo=chroma&logoColor=white" height="25"/>

**UI** : <img src="https://img.shields.io/badge/streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" height="25"/>

**LLM 모델** : <img src="https://img.shields.io/badge/koalpaca-000000?style=for-the-badge&logo=chroma&logoColor=white" height="25"/>


## 🤖 사용 모델
- KoAlpaca
  - LLAMA (영-한 모델) + Polyglot-ko (한국어 모델)
  - 허깅페이스에서 사용 가능
  - [KoAlpaca 링크](https://github.com/Beomi/KoAlpaca)

- Bert
  - 양방향 Transformer 모델

- BleuRT
  - Bert 모델을 위키피디아 문장으로 학습시킨 자동 평가 지표 모델

- Sentence BERT
  - Bert 모델의 문장 임베딩 성능을 우수하게 향상시킨 모델

- RoBERTa
  - Bert 모델을 더 잘 학습시킬 수 있는 레시피로 학습시킨 모델
  - Zeroshot Pipeline을 사용하여 Bert 모델에 학습되지 않은 특정 도메인에 잘 적응할 수 있게 만든 모델델

  
## 시스템 아키텍쳐
<img width="937" alt="image" src="https://github.com/user-attachments/assets/b66d665f-857e-4d08-a3f8-688c37630c5c" />



## 요구사항 명세서

| 기능 ID | 기능명 | 설명 |
|-------|--------|------|
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |

## WBS

| Phase                | Task                  | 담당자        | 기간          | 진척율 |
|----------------------|-----------------------|--------------|-------------- |--------|
| 주제 선정             | 주제 선정          | ALL          | 05.02 - 05.07 | 완료 |
| 데이터 수집 및 처리   | 데이터 크롤링       | ALL          | 05.07 - 05.12 | 완료 |
|                      | 데이터 정제        | ALL           | 05.12 - 05.13 | 완료 |
| 모델 설계 및 학습     | 모델 선정          | ALL           | 05.13         | 완료 |
|                      | 파인튜닝           | 이현대, 이현민 | 05.14         | 완료 |
|                      | 평가 및 테스트     | 이현대, 이 근  | 05.14 - 05.15 |      |
| 문서 검색 시스템(POC) | 임베딩 모델 적용    | 김형주, 신준희 | 05.14         |      |
|                      | CHROMA 구축        | ALL           | 05.14        |      |
| 중간 발표 시연 페이지 | UI/UX 설계          | ALL          | 05.14        | 완료 |
|                      | Streamlit 구현     |     김형주    | 05.14        | 완료 |
| 중간 발표 문서화      | README 작성        | 김형주, 신준희 | 05.14        |      |
| 중간발표             | 발표                | 이현대        | 05.15        | - |
|프론트엔드 구축| 미정 | - | - | - |
|백엔드 구축| 미정 | - | - | - |
|최종발표 문서화| 미정 | - | - | - |
|최종발표| 미정 | - | - | - |
<br>

## 수집한 데이터 및 전처리

### 1. 데이터 수집
- 총 60,000개의 맘카페 게시글 및 댓글
- [아이사랑 포털 월령별 성장 및 육아](https://www.childcare.go.kr/?menuno=286)

### 2. 데이터 정제

**공통된 작업**
1. Escape Sequence 제거 ('\n', '\t' 등)
2. 

**1. 맘카페 게시글 및 댓글**

1. 주제와 관련 없는 카테고리의 게시물 제거 (공지사항, 광고, 이벤트 등)

2. 질문(게시글)과 답변(댓글) 구조로 json 구조 변경 -> 첫 번째 데이터

3. 정보만 있는 게시물은 댓글 데이터 없이 따로 json 파일로 분리 

    3-1. 라벨링 작업 (정보 / 비정보)

**2. 아이사랑 포털 데이터**

2-1. 표 데이터를 텍스트 데이터로 변환

2-2. 메타데이터로 변환

## VectorDB 구현



## 테스트 계획 및 결과

- 파인튜닝 1epoch 걸리는 시간 21시간.. 24시간이 모자라

## 진행 과정 중 프로그램 개선

1. 데이터
2. 파인튜닝 파라미터 조정

## 수행 결과



### 테스트 및 시연



## 한 줄 회고

|   이름   |    내용    | 
|---------|------------|
|**김형주**||
|**신준희**||
|**이 근**||
|**이현대**||
|**이현민**||
