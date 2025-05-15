import json
from langchain.schema import Document
from langchain.vectorstores import Chroma
from transformers import BertTokenizer, BertModel
import torch
import os

# ✅ KoBERT 임베딩 모델 정의
class KoBERTEmbeddings:
    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained("skt/kobert-base-v1")
        self.model = BertModel.from_pretrained("skt/kobert-base-v1")
        self.model.eval()

    def embed(self, texts):
        embeddings = []
        for text in texts:
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
            with torch.no_grad():
                outputs = self.model(**inputs)
                cls_embedding = outputs.last_hidden_state[:, 0, :]  # [CLS] 토큰 임베딩
                embeddings.append(cls_embedding.squeeze().numpy())
        return embeddings

# ✅ JSON 파일 로딩
with open("./request_crawling/vector_db_final.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# ✅ Document 객체 리스트로 변환
documents = [
    Document(
        page_content=item["text"],
        metadata=item["metadata"]
    ) for item in data
]

# ✅ 임베딩 인스턴스 초기화
embedding_fn = KoBERTEmbeddings()

# ✅ Chroma 저장 경로
persist_dir = "./chroma_kobert"

# ✅ Chroma 벡터 저장소 생성
vecdb = Chroma.from_documents(
    documents=documents,
    embedding=embedding_fn,
    persist_directory=persist_dir
)

vecdb.persist()
print("✅ KoBERT 임베딩을 이용한 벡터 DB 저장 완료!")