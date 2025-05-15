import json
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util


with open('question.json', 'r') as j:
    posts = json.load(j)

post_data = {f'post{num+1}': {'post': post['content'], 'comment': [comment['content'] for comment in post['comments']]} for num, post in enumerate(posts)}

post_data

sample_post_data = post_data.copy()

classifier = pipeline("zero-shot-classification", model="joeddav/xlm-roberta-large-xnli")

for post_num in post_data:
    for num, comment in enumerate(post_data[post_num]['comment']):
        if not comment.strip():  # 빈 문자열 또는 공백만 있을 경우 건너뜀
            continue
        result = classifier(
            comment,
            candidate_labels=["질문", "설명", "명령", "조언"] # , "감정 표현"
        )
        label = result['labels']
        print(result['sequence'])
        print(label[result['scores'].index(max(result['scores']))])
        if label[result['scores'].index(max(result['scores']))] == "질문":
            sample_post_dat a[post_num]['comment'].remove(comment)
        
with open("classifier.json", "w") as j:
    json.dump(sample_post_data, j, ensure_ascii=False)