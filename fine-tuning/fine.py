# -*- coding: utf-8 -*-
import os
import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    EarlyStoppingCallback
)
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training,
    TaskType,
    PeftModel
)

# GPU 사용 가능 여부 확인
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(f"사용 중인 장치: {device}")

# 모델 및 토크나이저 로드
model_name = "beomi/KoAlpaca-Polyglot-5.8B"
tokenizer = AutoTokenizer.from_pretrained(model_name)

# 토크나이저에 패딩 토큰 설정 (없는 경우)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

# 모델 로드
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="cuda:0"    # GPU 메모리를 효율적으로 사용
)

# 먼저 모델 아키텍처를 검사하여 레이어 이름 확인
print("모델 아키텍처 검사:")
for name, module in model.named_modules():
    if "query" in name or "key" in name or "value" in name or "attn" in name or "mlp" in name:
        print(f"발견된 모듈: {name}")

# 실제 모델 구조에 맞춘 LoRA 설정
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=8,                    # LoRA 어댑터의 랭크
    lora_alpha=16,          # LoRA 스케일링 파라미터
    lora_dropout=0.05,      # LoRA 레이어의 드롭아웃 비율
    bias="none",            # 바이어스 학습 여부
    target_modules=[        # Polyglot-5.8B 모델의 실제 레이어 이름
        "query_proj", 
        "value_proj", 
        "key_proj", 
        "dense"
    ]
)

# 모델을 LoRA 용으로 준비
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()  # 학습 가능한 파라미터 비율 출력

# 데이터셋 로드
dataset = load_dataset("json", data_files="./expanded_info_contents.json")
print(f"데이터셋 정보: {dataset}")

# 학습/검증 데이터셋 분할 (검증 데이터셋 추가)
if "train" in dataset:
    # 이미 분할된 경우
    train_dataset = dataset["train"]
    # 검증 데이터셋 생성 (10% 사용)
    train_val = train_dataset.train_test_split(test_size=0.1)
    train_dataset = train_val["train"]
    val_dataset = train_val["test"]
else:
    # 분할되지 않은 경우
    train_val = dataset["train"].train_test_split(test_size=0.1)
    train_dataset = train_val["train"]
    val_dataset = train_val["test"]

print(f"학습 데이터셋 크기: {len(train_dataset)}")
print(f"검증 데이터셋 크기: {len(val_dataset)}")

# 토큰화 함수 정의 (KoAlpaca 형식으로 개선)

def tokenize_function(examples):
    # prompt와 completion을 KoAlpaca 형식으로 결합
    inputs = []
    for prompt, completion in zip(examples["post"], examples["comment"]):
        # KoAlpaca 형식 유지
        combined_text = f"### 질문: {prompt}\n\n### 답변: {completion}"
        inputs.append(combined_text)
    
    # 토큰화 - max_length로 잘라내고 패딩 활성화
    result = tokenizer(
        inputs,
        padding="max_length",      # 최대 길이로 패딩
        truncation=True,           # 너무 긴 시퀀스 자르기
        max_length=512,            # 최대 시퀀스 길이
        return_tensors=None        # 배치 내에서 텐서 변환 없음
    )
    
    # 인과적 언어 모델링을 위한 레이블 설정
    result["labels"] = result["input_ids"].copy()
    
    return result
tokenized_train = train_dataset.map(
    tokenize_function,
    batched=True,
    remove_columns=["post", "comment"]  # 원본 텍스트 컬럼 제거
)

tokenized_val = val_dataset.map(
    tokenize_function,
    batched=True,
    remove_columns=["post", "comment"]
)

# 데이터 콜레이터 설정
# 데이터 콜레이터 설정
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,         # 인과적 언어 모델링에 맞게 설정
    pad_to_multiple_of=8  # fp16 학습용 패딩 최적화
)


# 학습 인자 설정 (간소화)
training_args = TrainingArguments(
    output_dir="./results_lora_koalpaca",
    num_train_epochs=2,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=8,
    save_strategy="steps",   # 'eval_strategy' 대신 'save_strategy' 사용
    save_steps=100,
    save_total_limit=2,
    eval_steps=500,
    logging_dir="./logs_koalpaca",
    logging_steps=10,
    learning_rate=5e-5,
    weight_decay=0.01,
    fp16=True,
    warmup_ratio=0.1,
    gradient_accumulation_steps=4,
    remove_unused_columns=False,  # PEFT 모델에 필요
    group_by_length=True          # 비슷한 길이끼리 그룹화
)

# 평가 관련 매개변수 설정을 나중에 추가
if hasattr(TrainingArguments, 'evaluation_strategy'):
    training_args.evaluation_strategy = "steps"
    training_args.eval_steps = 500
elif hasattr(TrainingArguments, 'eval_strategy'):
    training_args.eval_strategy = "steps"
    training_args.eval_steps = 500

# 모델 로드 관련 매개변수
if hasattr(TrainingArguments, 'load_best_model_at_end'):
    training_args.load_best_model_at_end = True
    training_args.metric_for_best_model = "loss"
    training_args.greater_is_better = False

# 트레이너 초기화 (기본 설정으로)
trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_val,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
)

# 모델 훈련
trainer.train()

# 파인튜닝 전 모델 테스트
def test_model(model, tokenizer, prompt):
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model.generate(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_length=200,
            do_sample=True,
            top_p=0.95,
            temperature=0.7
        )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# 저장 전 한국어 테스트
print("=== 파인튜닝 후 모델 테스트 ===")
test_prompts = [
    "### 질문: 인공지능이란 무엇인가요?\n\n### 답변:",
    "### 질문: 한국의 유명한 음식을 알려주세요.\n\n### 답변:"
]

for prompt in test_prompts:
    response = test_model(model, tokenizer, prompt)
    print(f"프롬프트: {prompt}")
    print(f"응답: {response}")
    print("---")

# LoRA 모델 저장
model.save_pretrained("./lora_fine_tuned_koalpaca")
tokenizer.save_pretrained("./lora_fine_tuned_koalpaca")
print("LoRA 어댑터가 저장되었습니다.")

# 전체 모델 + LoRA 어댑터 합치기
print("LoRA 어댑터를 기본 모델과 병합 중...")
# 기본 모델 로드
base_model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="cuda:0"
)

# LoRA 어댑터 로드 및 병합
lora_model = PeftModel.from_pretrained(base_model, "./lora_fine_tuned_koalpaca")
merged_model = lora_model.merge_and_unload()  # LoRA 가중치를 기본 모델에 병합

# 병합된 모델 저장
merged_model.save_pretrained("./merged_lora_koalpaca")
tokenizer.save_pretrained("./merged_lora_koalpaca")
print("병합된 모델이 저장되었습니다.")

# 병합된 모델 테스트
print("=== 병합된 모델 테스트 ===")
merged_model = AutoModelForCausalLM.from_pretrained(
    "./merged_lora_koalpaca",
    torch_dtype=torch.float16,
    device_map="cuda:0"
)

for prompt in test_prompts:
    response = test_model(merged_model, tokenizer, prompt)
    print(f"프롬프트: {prompt}")
    print(f"응답: {response}")
    print("---")

print("파인튜닝 과정이 완료되었습니다.")
