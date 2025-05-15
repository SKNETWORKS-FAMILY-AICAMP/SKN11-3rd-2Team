import json

# JSON 파일 읽기
with open('info_contents.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 확장된 리스트를 저장할 변수
expanded_list = []

# 각 키(post1, post2 등)의 값에 대해 처리
for key in data:
    post_data = data[key]
    post_text = post_data['post']
    comments = post_data['comment']
    
    # 각 댓글에 대해 별도의 딕셔너리 생성
    for comment in comments:
        expanded_dict = {
            'post': post_text,
            'comment': comment
        }
        expanded_list.append(expanded_dict)

# 결과 출력
print(expanded_list)

# 결과를 새 JSON 파일로 저장하기
with open('expanded_info_contents.json', 'w', encoding='utf-8') as file:
    json.dump(expanded_list, file, ensure_ascii=False, indent=2)