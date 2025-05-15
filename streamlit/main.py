import streamlit as st
import os
import json
import logging
import time
import torch
from threading import Thread
from typing import List, Dict, Any, Optional
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer, StoppingCriteria, StoppingCriteriaList
from langchain.schema.retriever import BaseRetriever
from langchain_community.vectorstores import FAISS, Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 환경 변수 로드
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 모델 설정 (하드코딩)
MODEL_PATH = "Snowfall0601/finetuned-koalpaca-5.8B"  # 고정된 모델 경로
TOKENIZER_PATH = "beomi/KoAlpaca-Polyglot-5.8B"  # 토크나이저 경로
TEMPERATURE = 0.7  # 고정된 온도 값
MAX_LENGTH = 256  # 고정된 최대 길이
RETRIEVAL_K = 3  # 각 벡터 DB에서 검색할 문서 수

# 데이터 경로 설정 (하드코딩)
DATA_DIR = "./data"  # 데이터 파일 경로
VECTOR_DB_DIR = "./vector_db"  # 벡터 DB 저장 경로

# FAISS DB 저장 경로
FAISS_CLASSIFIED_PATH = os.path.join(VECTOR_DB_DIR, "faiss_classified")
FAISS_EXPANDED_PATH = os.path.join(VECTOR_DB_DIR, "faiss_expanded")

# Chroma DB 저장 경로
CHROMA_BABYLOVE_DIR = os.path.join(VECTOR_DB_DIR, "chroma_babylove")
SHOW_REFERENCES = False  # 참조 문서 표시 여부

# 시스템 프롬프트
SYSTEM_PROMPT = """
너는 초보 부모를 위한 육아 전문가 챗봇이야. 
아래 제공되는 문서 내용을 참고하여 질문에 대해 
친절하고 이해하기 쉽게 답변해줘.
"""

# 페이지 설정
st.set_page_config(
    page_title="🦙 육아 전문가 KoAlpaca 챗봇",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 페이지 제목
st.title("초보 부모들의 육아를 도와주는 마파덜")
st.markdown("---")

# JSON → Document 변환 함수
def load_documents_with_metadata(path: str) -> list[Document]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    docs: list[Document] = []

    # classified_contents.json
    if isinstance(data, dict) and all(isinstance(v, dict) and "post" in v for v in data.values()):
        for pid, e in data.items():
            text = e.get("post", "").strip()
            if not text:
                continue
            meta = {"id": pid}
            if "category" in e:    meta["category"]   = e["category"]
            if "confidence" in e:  meta["confidence"] = e["confidence"]
            docs.append(Document(page_content=text, metadata=meta))

    # expanded_info_contents.json
    elif isinstance(data, list) and data and all(isinstance(e, dict) and "comment" in e for e in data):
        for idx, e in enumerate(data):
            text = e.get("comment", "").strip()
            if not text:
                continue
            meta = {"post": e.get("post", ""), "index": idx}
            docs.append(Document(page_content=text, metadata=meta))

    # vector_db_final.json
    elif isinstance(data, list) and data and all(isinstance(e, dict) and "text" in e for e in data):
        for e in data:
            text = e.get("text", "").strip()
            if not text:
                continue
            docs.append(Document(page_content=text, metadata=e.get("metadata", {})))

    else:
        st.error(f"❌ `{path}`의 JSON 구조를 인식할 수 없습니다.")
        st.stop()

    return docs

# FAISS 벡터 DB 초기화
@st.cache_resource
def init_faiss(path: str, save_path: str):
    """
    FAISS 벡터 DB를 초기화하고 저장/로드합니다.
    path: 원본 JSON 파일 경로
    save_path: FAISS DB를 저장할 경로
    """
    try:
        # 이미 저장된 FAISS DB가 있는지 확인
        if os.path.exists(save_path):
            logger.info(f"저장된 FAISS DB를 로드합니다: {save_path}")
            embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
            return FAISS.load_local(save_path, embedding, allow_dangerous_deserialization=True)
        
        # 없으면 새로 생성
        logger.info(f"새 FAISS DB를 생성합니다: {path}")
        docs = load_documents_with_metadata(path)
        embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        
        # FAISS DB 생성 및 저장
        db = FAISS.from_documents(docs, embedding=embedding)
        
        # 저장 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # FAISS DB 저장
        db.save_local(save_path)
        logger.info(f"FAISS DB를 저장했습니다: {save_path}")
        
        return db
    except Exception as e:
        logger.error(f"FAISS 벡터 DB 초기화 오류: {str(e)}")
        return None

# Chroma 벡터 DB 초기화
@st.cache_resource
def init_chroma(path: str, persist_dir: str, collection_name: str):
    """
    Chroma 벡터 DB를 초기화하고 저장/로드합니다.
    path: 원본 JSON 파일 경로
    persist_dir: Chroma DB를 저장할 디렉토리
    collection_name: 컬렉션 이름
    """
    try:
        embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        
        # 이미 저장된 DB가 있으면 로드만 하고, 없으면 생성
        if os.path.isdir(persist_dir) and os.listdir(persist_dir):
            logger.info(f"저장된 Chroma DB를 로드합니다: {persist_dir}")
            return Chroma(
                persist_directory=persist_dir,
                embedding_function=embedding,
                collection_name=collection_name
            )
        else:
            logger.info(f"새 Chroma DB를 생성합니다: {path}")
            # 저장 디렉토리가 없으면 생성
            os.makedirs(persist_dir, exist_ok=True)
            
            docs = load_documents_with_metadata(path)
            db = Chroma.from_documents(
                documents=docs,
                embedding=embedding,
                persist_directory=persist_dir,
                collection_name=collection_name
            )
            
            # 명시적으로 저장 (실제로는 생성 시 자동 저장되지만 확실히 하기 위해)
            db.persist()
            logger.info(f"Chroma DB를 저장했습니다: {persist_dir}")
            
            return db
    except Exception as e:
        logger.error(f"Chroma 벡터 DB 초기화 오류: {str(e)}")
        return None

# 검색 도구 클래스 정의
class SearchTool:
    def __init__(self, name: str, description: str, vector_db: Any, db_type: str):
        self.name = name
        self.description = description
        self.vector_db = vector_db
        self.db_type = db_type
    
    def search(self, query: str) -> str:
        try:
            if self.vector_db is None:
                return f"{self.name} 데이터베이스를 사용할 수 없습니다."
            
            # 벡터 DB에서 검색 수행
            if hasattr(self.vector_db, 'similarity_search'):
                docs = self.vector_db.similarity_search(query, k=RETRIEVAL_K)
                
                results = []
                for i, doc in enumerate(docs):
                    source = f"[{self.db_type} 문서 {i+1}]"
                    meta = ""
                    if hasattr(doc, 'metadata') and doc.metadata:
                        if 'category' in doc.metadata:
                            meta += f" 카테고리: {doc.metadata['category']}"
                        if 'post' in doc.metadata and isinstance(doc.metadata['post'], str) and len(doc.metadata['post']) > 0:
                            meta += f" 관련 게시글: {doc.metadata['post'][:100]}..."
                    
                    results.append(f"{source}{meta}:\n{doc.page_content}")
                
                return "\n\n".join(results) if results else f"{self.name}에서 관련 정보를 찾을 수 없습니다."
            else:
                return f"{self.name}은 지원되지 않는 벡터 DB 타입입니다."
        
        except Exception as e:
            logger.error(f"{self.name} 검색 중 오류 발생: {str(e)}")
            return f"검색 오류: {str(e)}"

# 벡터 DB와 검색 도구 초기화
@st.cache_resource
def initialize_search_tools():
    try:
        # 벡터 DB 초기화
        faiss_classified = init_faiss(
            os.path.join(DATA_DIR, "classified_contents.json"),
            FAISS_CLASSIFIED_PATH
        )
        
        faiss_expanded = init_faiss(
            os.path.join(DATA_DIR, "expanded_info_contents.json"),
            FAISS_EXPANDED_PATH
        )
        
        chroma_baby_love = init_chroma(
            os.path.join(DATA_DIR, "vector_db_final.json"), 
            CHROMA_BABYLOVE_DIR, 
            "baby_love_contents"
        )
        
        # 개별 검색 도구 생성
        search_tools = []
        
        if faiss_classified:
            search_tools.append(
                SearchTool(
                    name="분류_게시글_검색",
                    description="육아 관련 분류된 게시글에서 정보를 검색합니다.",
                    vector_db=faiss_classified,
                    db_type="분류_게시글"
                )
            )
        
        if faiss_expanded:
            search_tools.append(
                SearchTool(
                    name="확장_정보_검색",
                    description="육아 관련 상세 정보와 추가 설명이 포함된 확장 정보를 검색합니다.",
                    vector_db=faiss_expanded,
                    db_type="확장_정보"
                )
            )
        
        if chroma_baby_love:
            search_tools.append(
                SearchTool(
                    name="베이비러브_정보_검색",
                    description="베이비러브 콘텐츠에서 정보를 검색합니다.",
                    vector_db=chroma_baby_love,
                    db_type="베이비러브"
                )
            )
        
        # 벡터 DB 사전 생성 (원래 코드와의 호환성을 위해)
        vector_dbs = {
            "faiss_classified": faiss_classified,
            "faiss_expanded": faiss_expanded,
            "chroma_baby_love": chroma_baby_love
        }
        
        return search_tools, vector_dbs, None
    
    except Exception as e:
        logger.error(f"검색 도구 초기화 오류: {str(e)}")
        return [], {}, None

# 커스텀 정지 기준 클래스 정의
class StopOnTokens(StoppingCriteria):
    def __init__(self, tokenizer, stop_token_ids):
        self.tokenizer = tokenizer
        self.stop_token_ids = stop_token_ids
    
    def __call__(self, input_ids, scores, **kwargs):
        for stop_ids in self.stop_token_ids:
            if input_ids[0][-len(stop_ids):].tolist() == stop_ids:
                return True
        return False

def load_model():
    """
    허깅페이스 레포지토리에서 모델과 토크나이저를 로드하는 함수 (Streamlit 캐싱 적용)
    """
    logger.info(f"허깅페이스 레포지토리에서 모델을 로드합니다: {MODEL_PATH}")
    logger.info(f"토크나이저를 로드합니다: {TOKENIZER_PATH}")
    
    # GPU 사용 가능 여부 확인
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    logger.info(f"사용 중인 장치: {device}")
    
    try:
        # 토크나이저 로드
        tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH)
        logger.info("토크나이저 로드 완료")
        
        # 토크나이저에 패딩 토큰 설정 (없는 경우)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            logger.info("패딩 토큰을 EOS 토큰으로 설정")
        
        # 파인튜닝된 모델을 허깅페이스 레포지토리에서 로드
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH,
            torch_dtype=torch.float16,  # 모델을 반정밀도(FP16)로 로드하여 메모리 사용량 감소
            device_map="auto",  # 자동으로 GPU에 할당
            low_cpu_mem_usage=True
        )
        
        logger.info("파인튜닝된 모델 로드 완료")
        return model, tokenizer, device
    
    except Exception as e:
        logger.error(f"모델 또는 토크나이저 로드 중 오류 발생: {str(e)}")
        raise

# 적합한 도구 선택 및 검색 수행
def select_and_use_tools(query: str, search_tools: List[SearchTool]) -> str:
    try:
        # 키워드 기반 도구 선택 로직
        keywords = {
            "분류_게시글_검색": ["발달", "단계", "일반", "기본", "수유", "이유식"],
            "확장_정보_검색": ["상세", "자세히", "사례", "예시", "경험"],
            "베이비러브_정보_검색": ["전문", "조언", "의학", "건강", "질병", "전문가"],
        }
        
        query_lower = query.lower()
        selected_tools = []
        
        # 키워드 일치도 기반 도구 선택
        for tool in search_tools:
            if tool.name in keywords:
                for word in keywords[tool.name]:
                    if word in query_lower:
                        selected_tools.append(tool)
                        break
        
        # 선택된 도구가 없으면 모든 도구 사용
        if not selected_tools:
            logger.info(f"키워드 매칭 실패, 모든 검색 도구 사용")
            selected_tools = search_tools
        
        # 선택된 도구로 검색 수행
        results = []
        for tool in selected_tools:
            logger.info(f"'{query}'에 대해 '{tool.name}' 도구 사용 중...")
            result = tool.search(query)
            if not result.endswith("에서 관련 정보를 찾을 수 없습니다."):
                results.append(f"[{tool.name} 결과]\n{result}")
        
        combined_result = "\n\n".join(results)
        logger.info(f"검색 완료: {len(selected_tools)}개 도구 사용")
        
        return combined_result if results else "어떤 데이터베이스에서도 관련 정보를 찾을 수 없습니다."
    
    except Exception as e:
        logger.error(f"도구 선택 및 사용 중 오류 발생: {str(e)}")
        return f"검색 오류: {str(e)}"

def generate_response(prompt, model, tokenizer, device, search_tools=None):
    """
    사용자 입력에 대한 응답을 생성하는 함수 (스트리밍 지원)
    """
    try:
        retrieved_context = ""
        no_results_found = False
        
        if search_tools:
            # 적합한 도구를 선택하고 검색 수행
            with st.spinner("관련 정보를 검색 중입니다..."):
                retrieved_context = select_and_use_tools(prompt, search_tools)
                logger.info("도구 기반 검색 완료")
                
                # 검색 결과에 "관련 정보를 찾을 수 없습니다" 또는 "어떤 데이터베이스에서도 관련 정보를 찾을 수 없습니다" 문구가 포함되어 있는지 확인
                if "어떤 데이터베이스에서도 관련 정보를 찾을 수 없습니다" in retrieved_context or not retrieved_context:
                    no_results_found = True
        
        # 관련 정보가 없을 경우 바로 응답
        if no_results_found:
            final_text = "죄송합니다. 현재 데이터베이스에서 해당 질문에 대한 관련 정보를 찾을 수 없습니다. 다른 주제나 더 일반적인 육아 관련 질문으로 문의해 주시면 도움드리겠습니다."
            return final_text, retrieved_context
        
        # KoAlpaca 형식으로 프롬프트 변환
        alpaca_prompt = f"### 시스템: {SYSTEM_PROMPT}\n\n"
        
        if retrieved_context:
            alpaca_prompt += f"### 문맥: {retrieved_context}\n\n"
            
        alpaca_prompt += f"### 질문: {prompt}\n\n### 답변:"
        logger.info("KoAlpaca 형식으로 프롬프트 변환 완료")
        
        # 입력 인코딩 (attention_mask 명시적 포함)
        encoded_input = tokenizer(alpaca_prompt, return_tensors="pt", padding=True)
        input_ids = encoded_input["input_ids"].to(device)
        attention_mask = encoded_input["attention_mask"].to(device)
        
        # 정지 토큰 설정
        stop_words = ["### 질문:", "### 답변:", "### 시스템:", "### 문맥:"]
        stop_token_ids = [tokenizer.encode(word, add_special_tokens=False) for word in stop_words]
        stopping_criteria = StoppingCriteriaList([StopOnTokens(tokenizer, stop_token_ids)])
        
        # 스트리머 초기화
        streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
        
        # 생성 매개변수 설정
        generation_kwargs = {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "max_new_tokens": MAX_LENGTH,
            "temperature": TEMPERATURE,
            "do_sample": True,
            "top_p": 0.95,
            "pad_token_id": tokenizer.pad_token_id,
            "streamer": streamer,
            "stopping_criteria": stopping_criteria
        }
        
        # 별도 스레드에서 텍스트 생성 시작
        thread = Thread(target=model.generate, kwargs=generation_kwargs)
        thread.start()
        
        # 응답 스트리밍을 위한 플레이스홀더 생성
        placeholder = st.empty()
        generated_text = ""
        
        # 스트리밍 출력
        for text in streamer:
            generated_text += text
            
            # 생성된 텍스트 정리 (중간 결과)
            cleaned_text = generated_text
            for tag in stop_words:
                if tag in cleaned_text:
                    cleaned_text = cleaned_text.split(tag)[0]
            
            # 업데이트된 텍스트를 플레이스홀더에 표시
            placeholder.markdown(cleaned_text)
            
            # 태그가 발견되면 생성 중단
            if any(tag in text for tag in stop_words):
                break
        
        # 최종 텍스트 정리
        final_text = generated_text
        for tag in stop_words:
            if tag in final_text:
                final_text = final_text.split(tag)[0]
        
        # 플레이스홀더를 최종 텍스트로 업데이트
        placeholder.markdown(final_text)
        
        # 참조 정보 추출 (필요한 경우)
        reference_info = ""
        if SHOW_REFERENCES and retrieved_context:
            reference_info = retrieved_context
        
        return final_text.strip(), reference_info
    
    except Exception as e:
        logger.error(f"응답 생성 중 오류 발생: {str(e)}")
        return f"오류 발생: {str(e)}", ""

# 대화 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화 기록 초기화 버튼
if st.button("대화 기록 초기화"):
    st.session_state.messages = []
    st.experimental_rerun()

# 이전 메시지 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("references") and SHOW_REFERENCES:
            st.markdown("---")
            st.markdown("**참조 정보:**")
            with st.expander("참조 문서 확인"):
                st.markdown(message["references"])

try:
    # 모델 로드
    model, tokenizer, device = load_model()
    
    # 검색 도구 초기화
    search_tools, vector_dbs, _ = initialize_search_tools()
    
    # 사용자 입력 처리
    if prompt := st.chat_input("육아에 관해 무엇이든 물어보세요!"):
        # 사용자 메시지 추가
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 사용자 메시지 표시
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 모델 응답 생성 및 표시
        with st.chat_message("assistant"):
            response, reference_info = generate_response(
                prompt=prompt, 
                model=model, 
                tokenizer=tokenizer, 
                device=device,
                search_tools=search_tools
            )
        
        # 어시스턴트 메시지 추가 (참조 정보 포함)
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response,
            "references": reference_info if SHOW_REFERENCES else ""
        })
        
except Exception as e:
    st.error(f"모델 로드 또는 응답 생성 중 오류 발생: {str(e)}")
    st.error("모델 설정과 데이터 파일 경로가 올바르게 설정되었는지 확인하세요.")
