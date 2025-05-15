import json
import re

# 이모티콘 제거용 정규 표현식
emoji_pattern = re.compile(r"(ㅋ+|ㅎ+|ㅠ+|ㅜ+|\^\^)+")

def clean_text(text):
    """이모티콘 제거 및 공백 정리"""
    cleaned = emoji_pattern.sub(" ", text)        # 이모티콘 제거
    cleaned = re.sub(r"\s+", " ", cleaned).strip() # 불필요한 공백 제거
    return cleaned

def clean_json_file(input_path, output_path):
    """JSON 파일을 정제해서 새 파일로 저장"""
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        for key in ['title', 'content', 'comments']:
            if key in item and isinstance(item[key], str):
                item[key] = clean_text(item[key])

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 사용 예시
input_file = "./filtered/filtered_final.json"
output_file = "./filtered_data_cleaned.json"
clean_json_file(input_file, output_file)
