#!/bin/bash

# 패키지 업데이트 및 설치
apt-get update
apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
xz-utils tk-dev liblzma-dev

# pyenv 설치
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
git clone https://github.com/yyuu/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv

# 환경 변수 설정 (bashrc에 추가)
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc

# bashrc 적용
source ~/.bashrc

# Python 3.10.17 설치
pyenv install 3.10.17

# 가상 환경 생성
pyenv virtualenv 3.10.17 llm_env

# 작업 디렉토리 생성 및 이동
mkdir llm_stream
cd llm_stream

# 가상 환경 활성화
pyenv activate llm_env

pip install --upgrade pip

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

pip install -r requirements.txt

echo "LLM 개발 환경 설정 완료!"
