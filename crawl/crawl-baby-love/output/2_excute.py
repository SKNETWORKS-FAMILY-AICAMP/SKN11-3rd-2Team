import json
import os
import uuid
from typing import List, Dict, Any

def extract_text_from_content(content: List[Dict]) -> str:
    """
    컨텐츠 리스트에서 텍스트 내용만 추출합니다.
    여러 타입(paragraph, list, table 등)의 콘텐츠를 처리합니다.
    """
    if not content:
        return ""
    
    texts = []
    
    for item in content:
        item_type = item.get("type")
        
        if item_type == "paragraph":
            texts.append(item.get("text", ""))
        
        elif item_type == "list":
            for list_item in item.get("items", []):
                # 리스트 아이템이 단순 텍스트인 경우
                if isinstance(list_item, dict) and "text" in list_item:
                    texts.append(list_item.get("text", ""))
                    
                    # 하위 항목이 있는 경우
                    if "sub_items" in list_item:
                        for sub_item in list_item.get("sub_items", []):
                            if isinstance(sub_item, dict) and "text" in sub_item:
                                texts.append("- " + sub_item.get("text", ""))
                
                # 리스트 아이템이 타이틀과 컨텐츠를 가진 복합 구조인 경우
                if isinstance(list_item, dict) and "title" in list_item:
                    texts.append(list_item.get("title", ""))
                    if "content" in list_item:
                        nested_text = extract_text_from_content(list_item.get("content", []))
                        texts.append(nested_text)
        
        elif item_type == "table":
            # 테이블의 캡션 추출
            if "data" in item and "caption" in item["data"]:
                texts.append(f"표: {item['data']['caption']}")
            
            # 테이블의 행 데이터를 텍스트로 변환
            if "data" in item and "rows" in item["data"]:
                for row in item["data"]["rows"]:
                    row_text = []
                    for cell in row:
                        # 셀이 텍스트 문자열인 경우
                        if isinstance(cell.get("text"), str):
                            row_text.append(cell.get("text", ""))
                        # 셀이 여러 항목을 담은 리스트인 경우
                        elif isinstance(cell.get("text"), list):
                            row_text.append(", ".join(cell.get("text", [])))
                    if row_text:
                        texts.append(" | ".join(row_text))
        
        elif item_type == "highlight_box":
            for highlight in item.get("items", []):
                texts.append(highlight.get("text", ""))
        
        elif item_type == "image":
            alt_text = item.get("alt", "")
            if alt_text:
                texts.append(f"[이미지: {alt_text}]")
    
    return "\n".join(texts)

def process_data_for_vector_db(input_path: str) -> List[Dict[str, Any]]:
    """
    JSON 데이터를 벡터 DB에 맞는 형식으로 변환합니다.
    
    각 섹션을 하나의 독립적인 문서로 변환하고, 
    관련 메타데이터(카테고리, 페이지, 섹션 제목 등)를 함께 저장합니다.
    """
    # JSON 파일 읽기
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    vector_db_documents = []
    
    for category in data:
        category_id = category.get("id")
        category_name = category.get("name")
        
        for page in category.get("pages", []):
            page_category = page.get("category", {})
            page_info = page.get("page", {})
            page_title = page.get("title", "")
            tabs = page.get("tabs", [])
            
            # 현재 선택된 탭을 찾기
            selected_tab = None
            for tab in tabs:
                if tab.get("selected", False):
                    selected_tab = tab.get("text", "")
                    break
            
            for section in page.get("sections", []):
                section_title = section.get("title", "")
                section_content = section.get("content", [])
                
                # 섹션 내용에서 텍스트 추출
                text_content = extract_text_from_content(section_content)
                
                if not text_content.strip():
                    continue  # 내용이 없는 섹션은 건너뜁니다
                
                # 벡터 DB 문서 생성
                document = {
                    "id": str(uuid.uuid4()),  # 고유 ID 생성
                    "text": text_content,  # 실제 텍스트 내용
                    "metadata": {
                        "category_id": category_id,
                        "category_name": category_name,
                        "page_id": page_info.get("id"),
                        "page_name": page_info.get("name"),
                        "page_title": page_title,
                        "selected_tab": selected_tab,
                        "section_title": section_title,
                        "source": f"{category_name}/{page_title}/{section_title}"
                    }
                }
                
                vector_db_documents.append(document)
    
    return vector_db_documents

def save_processed_data(processed_data: List[Dict[str, Any]], output_path: str) -> None:
    """처리된 데이터를 JSON 파일로 저장합니다."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)

def main():
    input_path = "/Users/link/Documents/SKN/4th_project_3/new_crawl/output/processed_data.json"
    output_path = "/Users/link/Documents/SKN/4th_project_3/new_crawl/output/vector_db_data.json"
    
    print(f"Processing {input_path}...")
    processed_data = process_data_for_vector_db(input_path)
    print(f"Created {len(processed_data)} documents for vector DB")
    
    save_processed_data(processed_data, output_path)
    print(f"Saved processed data to {output_path}")

if __name__ == "__main__":
    main()