# -*- coding: utf-8 -*-

import os
import json
from bs4 import BeautifulSoup

class HTMLProcessor:
    def __init__(self, data_directory):
        self.data_directory = data_directory
        self.output_directory = os.path.join(data_directory, "processed")
        
        # 출력 디렉토리 생성
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
    
    def process_json_data(self, json_file):
        """JSON 파일에서 데이터 로드 및 처리"""
        print(f"JSON 파일 처리: {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        processed_data = []
        
        for page in data:
            processed_page = {
                "menu_num": page["menu_num"],
                "page_title": page["page_title"],
                "url": page["url"],
                "tabs": []
            }
            
            for tab in page["tabs"]:
                processed_tab = {
                    "tab_title": tab["tab_title"],
                    "tab_menuno": tab["tab_menuno"],
                    "tab_url": tab["tab_url"],
                    "content_text": self.extract_text_from_html(tab["content"]),
                    "content_structured": self.extract_structured_content(tab["content"])
                }
                processed_page["tabs"].append(processed_tab)
            
            processed_data.append(processed_page)
        
        # 처리된 데이터 저장
        output_file = os.path.join(self.output_directory, "processed_data.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=2)
        
        print(f"처리된 데이터 저장: {output_file}")
        
        return processed_data
    
    def extract_text_from_html(self, html_content):
        """HTML에서 텍스트만 추출"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 불필요한 요소 제거
        for element in soup.select('script, style'):
            element.decompose()
        
        # 텍스트 추출
        text = soup.get_text(separator=' ', strip=True)
        
        # 연속된 공백 제거
        import re
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def extract_structured_content(self, html_content):
        """HTML에서 구조화된 데이터 추출 (제목, 내용 등)"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 구조화된 데이터 저장 객체
        structured_data = {
            "headings": {},  # 제목
            "paragraphs": [],  # 단락 내용
            "lists": [],  # 목록
            "tables": []  # 표
        }
        
        # 제목 추출 (h1 ~ h6)
        for level in range(1, 7):
            headings = soup.find_all(f'h{level}')
            for heading in headings:
                if not heading.text.strip() in structured_data["headings"]:
                    structured_data["headings"][heading.text.strip()] = []
                structured_data["headings"][heading.text.strip()].append(f"h{level}")
        
        # 단락 추출
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.text.strip()
            if text and len(text) > 1:  # 1자 이상인 경우만 추가
                structured_data["paragraphs"].append(text)
        
        # 목록 추출
        lists = soup.find_all(['ul', 'ol'])
        for lst in lists:
            items = []
            for item in lst.find_all('li'):
                text = item.text.strip()
                if text:
                    items.append(text)
            if items:
                structured_data["lists"].append({
                    "type": lst.name,
                    "items": items
                })
        
        # 표 추출
        tables = soup.find_all('table')
        for table in tables:
            table_data = {
                "caption": "",
                "headers": [],
                "rows": []
            }
            
            # 캡션 추출
            caption = table.find('caption')
            if caption:
                table_data["caption"] = caption.text.strip()
            
            # 헤더 행 추출
            thead = table.find('thead')
            if thead:
                header_rows = thead.find_all('tr')
                for row in header_rows:
                    headers = []
                    for cell in row.find_all(['th', 'td']):
                        headers.append(cell.text.strip())
                    if headers:
                        table_data["headers"].append(headers)
            
            # 데이터 행 추출
            tbody = table.find('tbody') or table
            data_rows = tbody.find_all('tr')
            for row in data_rows:
                cells = []
                for cell in row.find_all(['td', 'th']):
                    cells.append(cell.text.strip())
                if cells:
                    table_data["rows"].append(cells)
            
            # 표 데이터 추가
            if table_data["rows"]:
                structured_data["tables"].append(table_data)
        
        return structured_data
    
    def find_latest_json_file(self):
        """가장 최근 생성된 JSON 파일 찾기"""
        for root, dirs, files in os.walk(self.data_directory):
            json_files = [os.path.join(root, file) for file in files if file.endswith('.json')]
            if json_files:
                # 수정 시간 기준으로 가장 최근 파일 찾기
                latest_json = max(json_files, key=os.path.getmtime)
                return latest_json
        return None

def main():
    # 실행 디렉토리 내 data 폴더의 가장 최근 디렉토리 찾기
    base_path = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_path, "data")
    
    if os.path.exists(data_path):
        # 가장 최근 디렉토리 찾기
        dirs = [os.path.join(data_path, d) for d in os.listdir(data_path) 
                if os.path.isdir(os.path.join(data_path, d))]
        
        if dirs:
            latest_dir = max(dirs, key=os.path.getmtime)
            processor = HTMLProcessor(latest_dir)
            json_file = processor.find_latest_json_file()
            
            if json_file:
                processor.process_json_data(json_file)
            else:
                print(f"'{latest_dir}' 디렉토리에 JSON 파일이 없습니다.")
        else:
            print(f"'{data_path}' 내에 처리할 디렉토리가 없습니다.")
    else:
        print(f"'{data_path}' 디렉토리가 존재하지 않습니다.")

if __name__ == "__main__":
    main()
