import torch
import os
import logging
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer, StoppingCriteria, StoppingCriteriaList
from threading import Thread

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 모델 및 토크나이저 경로 설정
MODEL_PATH = "Snowfall0601/finetuned-koalpaca-5.8B"  # 허깅페이스 레포지토리
TOKENIZER_PATH = "beomi/KoAlpaca-Polyglot-5.8B"  # 토크나이저 경로

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

def load_model(model_path, tokenizer_path):
    """
    모델과 토크나이저를 로드하는 함수
    - 모델은 허깅페이스 레포지토리에서 로드
    - 토크나이저는 지정된 경로에서 로드
    """
    logger.info(f"모델을 로드합니다: {model_path}")
    logger.info(f"토크나이저를 로드합니다: {tokenizer_path}")
    
    # GPU 사용 가능 여부 확인
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"사용 중인 장치: {device}")
    
    try:
        # 다양한 옵션으로 토크나이저 로드 시도
        try:
            logger.info("첫 번째 방법으로 토크나이저 로드 시도")
            tokenizer = AutoTokenizer.from_pretrained(
                tokenizer_path,
                use_fast=False,
                trust_remote_code=True
            )
        except Exception as e:
            logger.warning(f"첫 번째 방법 실패: {str(e)}")
            logger.info("두 번째 방법으로 토크나이저 로드 시도")
            try:
                from transformers import PreTrainedTokenizerFast
                tokenizer = PreTrainedTokenizerFast.from_pretrained(tokenizer_path)
            except Exception as e2:
                logger.warning(f"두 번째 방법 실패: {str(e2)}")
                logger.info("마지막 방법으로 토크나이저 로드 시도")
                tokenizer = AutoTokenizer.from_pretrained(
                    tokenizer_path, 
                    padding_side='left',
                    truncation_side='left'
                )
        
        logger.info("토크나이저 로드 완료")
        
        # 토크나이저에 필요한 토큰 설정
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            logger.info("패딩 토큰을 EOS 토큰으로 설정")
        
        # 모델 설정
        model_loading_args = {
            "torch_dtype": torch.float16,
            "device_map": "cuda:0" if device == "cuda" else "auto",
            "low_cpu_mem_usage": True,
            "trust_remote_code": True
        }
        
        # 허깅페이스에서 모델 로드 시도
        try:
            logger.info("기본 옵션으로 모델 로드 시도")
            model = AutoModelForCausalLM.from_pretrained(model_path, **model_loading_args)
        except Exception as e:
            logger.warning(f"기본 옵션으로 모델 로드 실패: {str(e)}")
            logger.info("추가 옵션으로 모델 로드 시도")
            
            # 오류 발생 시 추가 옵션 시도
            model_loading_args["revision"] = "main"  # 메인 브랜치 사용
            model = AutoModelForCausalLM.from_pretrained(model_path, **model_loading_args)
        
        logger.info("모델 로드 완료")
        return model, tokenizer, device
    
    except Exception as e:
        logger.error(f"모델 또는 토크나이저 로드 중 오류 발생: {str(e)}")
        raise

def generate_response(prompt, model, tokenizer, device, max_length=256, temperature=0.7):
    """
    사용자 입력에 대한 응답을 생성하는 함수
    """
    try:
        # KoAlpaca 형식으로 프롬프트 변환
        alpaca_prompt = f"### 질문: {prompt}\n\n### 답변:"
        logger.info("KoAlpaca 형식으로 프롬프트 변환 완료")
        
        try:
            # 입력 텍스트를 수동으로 토큰화하여 오류 방지
            tokens = tokenizer.tokenize(alpaca_prompt)
            token_ids = tokenizer.convert_tokens_to_ids(tokens)
            input_ids = torch.tensor([token_ids]).to(device)
            attention_mask = torch.ones_like(input_ids).to(device)
            
            logger.info("수동 토큰화 완료")
        except Exception as e:
            logger.error(f"토큰화 중 오류: {str(e)}")
            # 백업 방법: 직접 인코딩
            try:
                input_ids = tokenizer.encode(alpaca_prompt, return_tensors="pt").to(device)
                attention_mask = torch.ones_like(input_ids).to(device)
                logger.info("백업 인코딩 방법 사용")
            except Exception as e2:
                logger.error(f"백업 인코딩 중 오류: {str(e2)}")
                raise
        
        # 정지 토큰 설정
        stop_words = ["### 질문:", "### 답변:"]
        stop_token_ids = []
        for word in stop_words:
            try:
                ids = tokenizer.encode(word, add_special_tokens=False)
                stop_token_ids.append(ids)
            except Exception as e:
                logger.error(f"정지 토큰 인코딩 오류 (무시): {str(e)}")
        
        stopping_criteria = StoppingCriteriaList([StopOnTokens(tokenizer, stop_token_ids)])
        
        # 스트리머 초기화 (답변 부분만 가져오도록 설정)
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
            "streamer": streamer
        }
        
        # stopping_criteria가 설정되어 있으면 추가
        if stop_token_ids:
            generation_kwargs["stopping_criteria"] = stopping_criteria
        
        # 별도 스레드에서 텍스트 생성 시작
        thread = Thread(target=model.generate, kwargs=generation_kwargs)
        thread.start()
        
        # 응답 생성 (스트리밍)
        generated_text = ""
        print("\n모델 응답: ", end="", flush=True)
        for text in streamer:
            print(text, end="", flush=True)
            generated_text += text
            
            # 응답에 "### 답변:" 또는 "### 질문:"이 포함되면 해당 부분까지만 사용
            if "### 답변:" in text or "### 질문:" in text:
                break
                
        print("\n")
        
        # 생성된 텍스트 정리
        # "### 답변:" 이후의 추가 태그 제거
        cleaned_text = generated_text
        if "### 답변:" in cleaned_text:
            cleaned_text = cleaned_text.split("### 답변:")[0]
        if "### 질문:" in cleaned_text:
            cleaned_text = cleaned_text.split("### 질문:")[0]
            
        return cleaned_text.strip()
        
    except Exception as e:
        logger.error(f"응답 생성 중 오류 발생: {str(e)}")
        return f"오류 발생: {str(e)}"

def chat_with_model():
    """
    대화형 인터페이스를 제공하는 메인 함수
    """
    try:
        # 모델 및 토크나이저 로드
        model, tokenizer, device = load_model(MODEL_PATH, TOKENIZER_PATH)
        
        print(f"🤖 모델 '{MODEL_PATH}'이(가) 로드되었습니다.")
        print(f"🔤 토크나이저는 '{TOKENIZER_PATH}'에서 로드되었습니다.")
        print("대화를 시작합니다. 종료하려면 'exit', 'quit', 또는 'q'를 입력하세요.")
        
        conversation_history = ""  # 대화 기록 저장용
        
        while True:
            user_input = input("\n사용자: ")
            
            # 종료 명령 확인
            if user_input.lower() in ["exit", "quit", "q"]:
                print("대화를 종료합니다. 감사합니다!")
                break
            
            # 대화 기록 업데이트
            if conversation_history:
                conversation_history += f"\n사용자: {user_input}"
            else:
                conversation_history = f"사용자: {user_input}"
            
            # 사용자 입력 그대로 전달 (KoAlpaca 형식은 generate_response 내에서 변환)
            response = generate_response(user_input, model, tokenizer, device, 500, 0.7)
            
            # 대화 기록 업데이트
            conversation_history += f"\n모델: {response}"
            
    except KeyboardInterrupt:
        print("\n사용자가 대화를 중단했습니다.")
    except Exception as e:
        logger.error(f"예상치 못한 오류 발생: {str(e)}")
        print(f"오류 발생: {str(e)}")

if __name__ == "__main__":
    chat_with_model()