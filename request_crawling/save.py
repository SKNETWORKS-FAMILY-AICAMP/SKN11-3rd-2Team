import requests
from bs4 import BeautifulSoup
import time
import json

base_url = "https://www.childcare.go.kr/?menuno={}"
headers = {"User-Agent": "Mozilla/5.0"}

result_data = []

for menuno in range(425, 467):  # 425~466 포함
    print(f"\n📌 [ menuno={menuno} ] 페이지 요청 중...")
    url = base_url.format(menuno)

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
        continue

    soup = BeautifulSoup(response.text, "html.parser")
    content_section = soup.select_one("section.contents_wrap")

    if not content_section:
        print("❌ 본문 없음")
        continue

    # 메인 제목
    title_tag = content_section.select_one("h3.title")
    title = title_tag.text.strip() if title_tag else f"페이지 {menuno}"
    print(f"# 제목: {title}")

    page_dict = {
        "title": title,
        "description": []
    }

    for h4 in content_section.select("h4.title_line"):
        sub_title = h4.text.strip()
        section_content = []

        next_tag = h4.find_next_sibling()
        while next_tag and next_tag.name not in ['h3', 'h4', 'h5']:
            if next_tag.name == 'p':
                text = next_tag.text.strip()
                if text:
                    section_content.append(text)
            elif next_tag.name == 'ul':
                for li in next_tag.select('li'):
                    li_text = li.text.strip()
                    if li_text:
                        section_content.append(f"- {li_text}")
            next_tag = next_tag.find_next_sibling()

        page_dict["description"].append({
            "sub_title": sub_title,
            "content": section_content
        })

    result_data.append(page_dict)
    time.sleep(1)

# ✅ JSON 저장
with open("./request_crawling/childcare_descriptions.json", "w", encoding="utf-8") as f:
    json.dump(result_data, f, ensure_ascii=False, indent=2)

print("\n✅ JSON 저장 완료: childcare_descriptions.json")