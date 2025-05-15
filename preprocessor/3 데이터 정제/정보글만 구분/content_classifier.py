import json
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util

# 데이터 로드
with open('info.json', 'r', encoding='utf-8') as j:
    posts = json.load(j)

# 포스트 데이터 추출 (댓글 없이 포스트 내용만 추출)
post_data = {f'post{num+1}': {
    'post': post['content']
} for num, post in enumerate(posts)}

# 분류할 원본 데이터 복사
classified_posts = post_data.copy()

# 제로샷 분류 파이프라인 설정
# use_fast=False 옵션을 추가하여 fast tokenizer 대신 기본 tokenizer 사용
classifier = pipeline("zero-shot-classification", model="joeddav/xlm-roberta-large-xnli")

# 정보와 비정보로만 분류
content_categories = ["정보", "비정보"]

# 각 포스트 내용 분류
filtered_posts = {}

for post_num, data in classified_posts.items():
    content = data['post']
    
    if not content.strip():  # 빈 문자열 또는 공백만 있을 경우 건너뜀
        continue
    
    # 제로샷 분류 실행
    result = classifier(
        content,
        candidate_labels=content_categories
    )
    
    # 최고 점수 카테고리 선택
    best_label = result['labels'][result['scores'].index(max(result['scores']))]
    best_score = max(result['scores'])
    
    # 결과 출력
    print(f"포스트 ID: {post_num}")
    print(f"내용: {content[:100]}..." if len(content) > 100 else f"내용: {content}")
    print(f"분류 결과: {best_label} (신뢰도: {best_score:.4f})")
    print("-" * 50)
    
    # 분류 결과 저장
    classified_posts[post_num]['category'] = best_label
    classified_posts[post_num]['confidence'] = best_score
    
    # 정보 카테고리만 필터링하여 별도 저장
    if best_label == "정보":
        filtered_posts[post_num] = data

# 모든 분류 결과 저장
with open('classified_contents.json', 'w', encoding='utf-8') as f:
    json.dump(classified_posts, f, ensure_ascii=False, indent=4)

# 정보 카테고리만 저장
with open('info_contents.json', 'w', encoding='utf-8') as f:
    json.dump(filtered_posts, f, ensure_ascii=False, indent=4)

print("분류 완료!")
print("전체 분류 결과가 'classified_contents.json' 파일에 저장되었습니다.")
print("정보 카테고리만 'info_contents.json' 파일에 저장되었습니다.")

# 카테고리별 통계 출력
category_stats = {}
for post_data in classified_posts.values():
    category = post_data.get('category')
    if category:
        category_stats[category] = category_stats.get(category, 0) + 1

print("\n카테고리별 포스트 수:")
for category, count in category_stats.items():
    print(f"{category}: {count}개")

print(f"\n정보 카테고리로 분류된 포스트: {len(filtered_posts)}개")
print(f"총 포스트: {len(classified_posts)}개")
