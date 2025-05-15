from huggingface_hub import HfApi
import os
import glob

# 허깅페이스 토큰 설정
huggingface_token = ""  # 허깅페이스 웹사이트에서 발급받은 토큰
api = HfApi(token=huggingface_token)

# 모델 경로와 레포지토리 설정
model_path = "./merged_lora_koalpaca"  # 파인튜닝된 모델이 저장된 로컬 경로
repo_name = "Snowfall0601/finetuned-koalpaca-5.8B"  # 예: username/my-finetuned-model

# 외부 저장 공간에 있는 경로 사용
workspace_dir = "/workspace/model_upload"
os.makedirs(workspace_dir, exist_ok=True)

# 1. 먼저 전체 구조를 /workspace로 복사
import shutil
if model_path != workspace_dir:  # 이미 workspace에 있지 않은 경우만
    # 모델 파일을 작은 단위로 복사
    for file in glob.glob(f"{model_path}/*"):
        filename = os.path.basename(file)
        shutil.copy(file, os.path.join(workspace_dir, filename))

# 2. huggingface_hub의 upload_file 메서드 사용해 파일 하나씩 업로드
for file_path in glob.glob(f"{workspace_dir}/*"):
    file_name = os.path.basename(file_path)
    api.upload_file(
        path_or_fileobj=file_path,
        path_in_repo=file_name,
        repo_id=repo_name,
        repo_type="model",
        token=huggingface_token
    )
    print(f"업로드 완료: {file_name}")

print(f"모든 파일이 '{repo_name}' 레포지토리에 업로드되었습니다.")