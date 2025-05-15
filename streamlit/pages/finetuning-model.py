import streamlit as st
import os
import logging
import time
from threading import Thread

# torch와 transformers 임포트 전에 환경 변수 설정
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# 이후에 torch와 transformers 임포트
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer, StoppingCriteria, StoppingCriteriaList

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 모델 경로 설정 (하드코딩)
MODEL_PATH = "Snowfall0601/finetuned-koalpaca-5.8B"  # 고정된 모델 경로
TOKENIZER_PATH = "beomi/KoAlpaca-Polyglot-5.8B"  # 토크나이저 경로

# 페이지 설정
st.set_page_config(
    page_title="KoAlpaca 챗봇",
    page_icon="🦙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 페이지 제목
st.title("🦙 KoAlpaca 파인튜닝 모델 챗봇")
st.markdown("---")

# 사이드바 설정
with st.sidebar:
    st.header("모델 설정")
    
    # 모델 정보 표시 (수정 불가)
    st.info(f"현재 사용 중인 모델: {MODEL_PATH}")
    
    temperature = st.slider("온도 (Temperature)", min_value=0.1, max_value=2.0, value=0.7, step=0.1, 
                           help="값이 높을수록 더 창의적인 응답을 생성합니다.")
    max_length = st.slider("최대 길이", min_value=64, max_value=512, value=256, step=32,
                         help="생성할 텍스트의 최대 길이를 설정합니다.")
    
    st.markdown("---")
    st.header("모델 정보")
    st.info(f"모델 경로: {MODEL_PATH}")
    st.info(f"토크나이저: {TOKENIZER_PATH}")
    
    st.markdown("---")
    if st.button("대화 기록 초기화"):
        for key in st.session_state.keys():
            if key.startswith("messages"):
                del st.session_state[key]
        st.session_state.messages = []
        st.experimental_rerun()

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

@st.cache_resource(show_spinner=False)
def load_model():
    """
    하드코딩된 경로에서 모델과 토크나이저를 로드하는 함수 (Streamlit 캐싱 적용)
    """
    with st.spinner("모델을 로드 중입니다... 잠시만 기다려 주세요."):
        logger.info(f"모델을 로드합니다: {MODEL_PATH}")
        logger.info(f"토크나이저를 로드합니다: {TOKENIZER_PATH}")
        
        # GPU 사용 가능 여부 확인
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"사용 중인 장치: {device}")
        
        try:
            # 토크나이저 로드
            tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH, legacy=True)
            logger.info("토크나이저 로드 완료")
            
            # 토크나이저에 패딩 토큰 설정 (없는 경우)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
                logger.info("패딩 토큰을 EOS 토큰으로 설정")
            
            # 모델 로드
            model = AutoModelForCausalLM.from_pretrained(
                MODEL_PATH,
                torch_dtype=torch.float16,  # 모델을 반정밀도(FP16)로 로드하여 메모리 사용량 감소
                device_map="auto",  # 자동으로 GPU에 할당
                low_cpu_mem_usage=True
            )
            
            logger.info("모델 로드 완료")
            return model, tokenizer, device
        
        except Exception as e:
            logger.error(f"모델 또는 토크나이저 로드 중 오류 발생: {str(e)}")
            raise

def generate_response(prompt, model, tokenizer, device, max_length=256, temperature=0.7):
    """
    사용자 입력에 대한 응답을 생성하는 함수 (스트리밍 지원)
    """
    try:
        # KoAlpaca 형식으로 프롬프트 변환
        alpaca_prompt = f"### 질문: {prompt}\n\n### 답변:"
        logger.info("KoAlpaca 형식으로 프롬프트 변환 완료")
        
        # 입력 인코딩 (attention_mask 명시적 포함)
        encoded_input = tokenizer(alpaca_prompt, return_tensors="pt", padding=True)
        input_ids = encoded_input["input_ids"].to(device)
        attention_mask = encoded_input["attention_mask"].to(device)
        
        # 정지 토큰 설정
        stop_words = ["### 질문:", "### 답변:"]
        stop_token_ids = [tokenizer.encode(word, add_special_tokens=False) for word in stop_words]
        stopping_criteria = StoppingCriteriaList([StopOnTokens(tokenizer, stop_token_ids)])
        
        # 스트리머 초기화
        streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
        
        # 생성 매개변수 설정
        generation_kwargs = {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "max_new_tokens": max_length,
            "temperature": temperature,
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
            if "### 답변:" in cleaned_text:
                cleaned_text = cleaned_text.split("### 답변:")[0]
            if "### 질문:" in cleaned_text:
                cleaned_text = cleaned_text.split("### 질문:")[0]
            
            # 업데이트된 텍스트를 플레이스홀더에 표시
            placeholder.markdown(cleaned_text)
            
            # 태그가 발견되면 생성 중단
            if "### 답변:" in text or "### 질문:" in text:
                break
        
        # 최종 텍스트 정리
        final_text = generated_text
        if "### 답변:" in final_text:
            final_text = final_text.split("### 답변:")[0]
        if "### 질문:" in final_text:
            final_text = final_text.split("### 질문:")[0]
        
        # 플레이스홀더를 최종 텍스트로 업데이트
        placeholder.markdown(final_text)
        
        return final_text.strip()
    
    except Exception as e:
        logger.error(f"응답 생성 중 오류 발생: {str(e)}")
        return f"오류 발생: {str(e)}"

# 대화 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 메시지 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

try:
    # 모델 로드 (캐싱 적용) - 이제 매개변수 없음
    with st.spinner("모델 준비 중..."):
        model, tokenizer, device = load_model()
    
    # 사용자 입력 처리
    if prompt := st.chat_input("무엇이든 물어보세요!"):
        # 사용자 메시지 추가
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 사용자 메시지 표시
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 모델 응답 생성 및 표시
        with st.chat_message("assistant"):
            response = generate_response(
                prompt=prompt, 
                model=model, 
                tokenizer=tokenizer, 
                device=device,
                max_length=max_length,
                temperature=temperature
            )
        
        # 어시스턴트 메시지 추가
        st.session_state.messages.append({"role": "assistant", "content": response})
        
except Exception as e:
    st.error(f"모델 로드 또는 응답 생성 중 오류 발생: {str(e)}")
    import traceback
    st.error(traceback.format_exc())