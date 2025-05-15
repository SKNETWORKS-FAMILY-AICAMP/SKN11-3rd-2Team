import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

base_url = "https://www.childcare.go.kr/?menuno={}"
headers = {"User-Agent": "Mozilla/5.0"}

for menuno in range(425, 467):  # 425~433
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

    title = content_section.select_one("h3.title")
    if title:
        print(f"# 제목: {title.text.strip()}")

    for h4 in content_section.select("h4.title_line"):
        print(f"\n## {h4.text.strip()}")
        next_tag = h4.find_next_sibling()
        while next_tag and next_tag.name not in ['h3', 'h4', 'h5']:
            if next_tag.name == 'p':
                print(next_tag.text.strip())
            elif next_tag.name == 'ul':
                for li in next_tag.select('li'):
                    print(" -", li.text.strip())
            next_tag = next_tag.find_next_sibling()

    for h5 in content_section.select("h5.title_line"):
        print(f"\n## {h4.text.strip()}")
        next_tag = h5.find_next_sibling()
        while next_tag and next_tag.name not in ['h3', 'h4', 'h5']:
            if next_tag.name == 'p':
                print(next_tag.text.strip())
            elif next_tag.name == 'ul':
                for li in next_tag.select('li'):
                    print(" -", li.text.strip())
            next_tag = next_tag.find_next_sibling()

    # 테이블 추출
    tables = content_section.select("table")
    if not tables:
        print("📭 표 없음")
        continue

    for idx, table in enumerate(tables):
        print(f"\n📊 테이블 {idx+1}")
        table_headers = []
        table_data = []

        thead = table.find("thead")
        if thead:
            table_headers = [th.get_text(strip=True) for th in thead.select("th")]
        else:
            first_row = table.select_one("tr")
            col_count = len(first_row.select("td")) if first_row else 0
            table_headers = [f"컬럼{i+1}" for i in range(col_count)]

        rows = table.select("tbody tr") or table.select("tr")
        for row in rows:
            cols = [td.get_text(strip=True) for td in row.select("td")]
            if cols:
                table_data.append(cols)

        try:
            df = pd.DataFrame(table_data, columns=table_headers[:len(table_data[0])])
            print(df)
        except Exception as e:
            print(f"⚠️ 테이블 출력 오류: {e}")
    
    time.sleep(1)
