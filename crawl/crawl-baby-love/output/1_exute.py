
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTML 파일을 JSON으로 변환하는 스크립트
사용법: python html_to_json_converter.py
"""

import os
import re
import json
import glob
from collections import defaultdict
from bs4 import BeautifulSoup

def extract_table_data(table):
    """테이블 데이터를 추출하는 함수"""
    table_data = {}
    
    # 캡션 추출
    caption = table.find('caption')
    if caption:
        table_data['caption'] = caption.text.strip()
    
    # 헤더 추출
    headers = []
    header_rows = table.select('thead tr')
    
    if header_rows:
        for row in header_rows:
            row_headers = []
            for cell in row.select('th'):
                rowspan = int(cell.get('rowspan', 1))
                colspan = int(cell.get('colspan', 1))
                cell_data = {
                    'text': cell.text.strip(),
                    'rowspan': rowspan,
                    'colspan': colspan
                }
                row_headers.append(cell_data)
            headers.append(row_headers)
        table_data['headers'] = headers
    
    # 바디 데이터 추출
    body_rows = table.select('tbody tr')
    rows = []
    
    if body_rows:
        for row in body_rows:
            row_data = []
            
            # th 처리 (열 헤더)
            for cell in row.select('th'):
                rowspan = int(cell.get('rowspan', 1))
                colspan = int(cell.get('colspan', 1))
                cell_data = {
                    'text': cell.text.strip(),
                    'is_header': True,
                    'rowspan': rowspan,
                    'colspan': colspan
                }
                row_data.append(cell_data)
            
            # td 처리 (데이터 셀)
            for cell in row.select('td'):
                rowspan = int(cell.get('rowspan', 1))
                colspan = int(cell.get('colspan', 1))
                
                # 셀 내부에 리스트가 있는 경우
                list_items = cell.select('li')
                cell_content = ""
                
                if list_items:
                    cell_content = [item.text.strip() for item in list_items]
                else:
                    cell_content = cell.text.strip()
                
                cell_data = {
                    'text': cell_content,
                    'is_header': False,
                    'rowspan': rowspan,
                    'colspan': colspan
                }
                row_data.append(cell_data)
            
            rows.append(row_data)
        
        table_data['rows'] = rows
    
    return table_data

def extract_list_data(ul_tag):
    """리스트 데이터를 추출하는 함수"""
    list_data = []
    
    for li_tag in ul_tag.find_all('li', recursive=False):
        item_data = {}
        
        # 리스트 아이템의 텍스트 추출
        # 첫 번째 자식 요소가 strong 태그인 경우는 제목과 내용 구분
        strong_tag = li_tag.find('strong')
        
        if strong_tag:
            item_data['title'] = strong_tag.text.strip()
            
            # strong 태그 이후 내용 추출
            content = []
            
            # p 태그
            p_tags = li_tag.find_all('p', class_='txt')
            for p in p_tags:
                content.append({'type': 'paragraph', 'text': p.text.strip()})
            
            # 중첩된 ul 태그 처리
            nested_ul = li_tag.find('ul')
            if nested_ul:
                content.append({'type': 'list', 'items': extract_list_data(nested_ul)})
            
            # 테이블 처리
            table = li_tag.find('table')
            if table:
                content.append({'type': 'table', 'data': extract_table_data(table)})
            
            # img 태그 처리
            img_tags = li_tag.find_all('img')
            for img in img_tags:
                content.append({
                    'type': 'image',
                    'src': img.get('src', ''),
                    'alt': img.get('alt', '')
                })
            
            # 내용이 없고 직접 텍스트가 있는 경우
            if not content:
                # strong 태그 이후의 텍스트 추출
                text_content = li_tag.text.replace(strong_tag.text, '', 1).strip()
                if text_content:
                    content.append({'type': 'text', 'text': text_content})
            
            item_data['content'] = content
        else:
            # strong 태그가 없는 경우, 전체 텍스트를 내용으로 추출
            item_data['text'] = li_tag.text.strip()
            
            # 중첩된 ul 태그 처리
            nested_ul = li_tag.find('ul')
            if nested_ul:
                item_data['sub_items'] = extract_list_data(nested_ul)
        
        list_data.append(item_data)
    
    return list_data

def extract_content_sections(soup):
    """본문 섹션을 추출하는 함수"""
    sections = []
    
    # 모든 h4 태그 찾기
    h4_tags = soup.find_all('h4', class_='title_line')
    
    for h4 in h4_tags:
        section = {
            'title': h4.text.strip(),
            'content': []
        }
        
        # 현재 h4 다음 요소부터 다음 h4 전까지의 모든 요소를 찾기
        current = h4.next_sibling
        
        while current and (not isinstance(current, type(h4)) or not current.name == 'h4'):
            if hasattr(current, 'name'):
                # p 태그 처리
                if current.name == 'p':
                    section['content'].append({
                        'type': 'paragraph',
                        'text': current.text.strip()
                    })
                
                # ul 태그 처리
                elif current.name == 'ul':
                    section['content'].append({
                        'type': 'list',
                        'items': extract_list_data(current)
                    })
                
                # 테이블 처리
                elif current.name == 'div' and current.find('table'):
                    table = current.find('table')
                    section['content'].append({
                        'type': 'table',
                        'data': extract_table_data(table)
                    })
                
                # 이미지 처리
                elif current.name == 'img':
                    section['content'].append({
                        'type': 'image',
                        'src': current.get('src', ''),
                        'alt': current.get('alt', '')
                    })
                
                # div.color_box_blue_square 처리
                elif current.name == 'div' and 'color_box_blue_square' in current.get('class', []):
                    ul = current.find('ul')
                    if ul:
                        section['content'].append({
                            'type': 'highlight_box',
                            'items': extract_list_data(ul)
                        })
            
            # 다음 요소로 이동
            if hasattr(current, 'next_sibling'):
                current = current.next_sibling
            else:
                break
        
        sections.append(section)
    
    return sections

def process_html_file(file_path):
    """HTML 파일을 처리하고 JSON으로 변환하는 함수"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 파일 정보 추출
        file_name = os.path.basename(file_path)
        dir_name = os.path.basename(os.path.dirname(file_path))
        
        # 디렉토리 이름 파싱 (예: "287_이른둥이" -> {"id": 287, "name": "이른둥이"})
        dir_match = re.match(r'(\d+)_(.+)', dir_name)
        category = {}
        if dir_match:
            category = {
                "id": int(dir_match.group(1)),
                "name": dir_match.group(2)
            }
        
        # 파일 이름 파싱 (예: "1_이른둥이란_.html" -> {"id": 1, "name": "이른둥이란_"})
        file_match = re.match(r'(\d+)_(.+)\.html', file_name)
        page = {}
        if file_match:
            page = {
                "id": int(file_match.group(1)),
                "name": file_match.group(2)
            }
        
        # 주제 제목 (h3 태그)
        title = ""
        h3_tag = soup.find('h3', class_='title')
        if h3_tag:
            title = h3_tag.text.strip()
        
        # 탭 메뉴 (ul.tab 내의 li 태그들)
        tabs = []
        tab_ul = soup.find('ul', class_='tab')
        if tab_ul:
            for li in tab_ul.find_all('li'):
                tab = {
                    "text": li.text.strip(),
                    "url": li.find('a')['href'] if li.find('a') else "",
                    "selected": 'on' in li.get('class', [])
                }
                tabs.append(tab)
        
        # 본문 내용 추출
        sections = extract_content_sections(soup)
        
        # 결과 데이터 구성
        result = {
            "category": category,
            "page": page,
            "title": title,
            "tabs": tabs,
            "sections": sections
        }
        
        return result
    except Exception as e:
        print(f"파일 처리 중 오류 발생 ({file_path}): {e}")
        return None

def process_category_directory(category_dir):
    """하나의 카테고리 디렉토리에 있는 모든 HTML 파일을 처리하는 함수"""
    category_data = []
    
    # 카테고리 정보 추출
    category_basename = os.path.basename(category_dir)
    category_match = re.match(r'(\d+)_(.+)', category_basename)
    
    if not category_match:
        print(f"카테고리 디렉토리 이름 형식 오류: {category_dir}")
        return None
    
    category_id = int(category_match.group(1))
    category_name = category_match.group(2)
    
    # HTML 파일 목록 가져오기
    html_files = sorted(glob.glob(os.path.join(category_dir, '*.html')))
    
    # 각 HTML 파일 처리
    pages = []
    for html_file in html_files:
        try:
            result = process_html_file(html_file)
            if result:
                pages.append(result)
        except Exception as e:
            print(f"HTML 파일 처리 중 오류 발생 ({html_file}): {e}")
    
    # 페이지 ID로 정렬
    pages.sort(key=lambda x: x['page']['id'])
    
    return {
        "id": category_id,
        "name": category_name,
        "pages": pages
    }

def main():
    # 처리할 기본 디렉토리
    base_dir = '/Users/link/Documents/SKN/4th_project_3/new_crawl/data/20250514_113319'
    
    # 출력 디렉토리
    output_dir = '/Users/link/Documents/SKN/4th_project_3/new_crawl/output'
    
    # 먼저 출력 디렉토리가 있는지 확인하고 없으면 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 카테고리 디렉토리 목록 가져오기
    category_dirs = [d for d in glob.glob(os.path.join(base_dir, '*_*')) if os.path.isdir(d)]
    
    # 알파벳순으로 정렬 (파일 이름은 숫자로 시작하므로 숫자 순서로 정렬됨)
    category_dirs.sort()
    
    all_data = []
    
    # 각 카테고리 디렉토리 처리
    for category_dir in category_dirs:
        print(f"카테고리 처리 중: {category_dir}")
        category_data = process_category_directory(category_dir)
        if category_data:
            all_data.append(category_data)
    
    # 카테고리 ID로 정렬
    all_data.sort(key=lambda x: x['id'])
    
    # 결과를 JSON 파일로 저장
    output_file = os.path.join(output_dir, 'processed_data.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"처리 완료. 결과는 {output_file}에 저장되었습니다.")

if __name__ == "__main__":
    main()
