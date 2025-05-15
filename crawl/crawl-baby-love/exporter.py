# -*- coding: utf-8 -*-

import os
import json
import pandas as pd
import argparse
import re

class DataExporter:
    def __init__(self, input_file):
        self.input_file = input_file
        self.data = self.load_data()
        
        # 출력 디렉토리 설정
        self.output_dir = os.path.dirname(input_file)
        
        # 확장자 없는 파일명 추출
        base_filename = os.path.splitext(os.path.basename(input_file))[0]
        self.output_prefix = os.path.join(self.output_dir, base_filename)
    
    def load_data(self):
        """JSON 파일에서 데이터 로드"""
        with open(self.input_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def export_to_excel(self):
        """데이터를 Excel 파일로 내보내기"""
        # 페이지 정보 데이터프레임
        pages_data = []
        
        for page in self.data:
            # 페이지 정보 추가
            page_info = {
                "menu_num": page["menu_num"],
                "page_title": page["page_title"],
                "url": page["url"],
                "tabs_count": len(page["tabs"])
            }
            pages_data.append(page_info)
        
        # 탭 정보 데이터프레임
        tabs_data = []
        
        for page in self.data:
            for tab in page["tabs"]:
                # 탭 정보 추가
                tab_info = {
                    "menu_num": page["menu_num"],
                    "page_title": page["page_title"],
                    "tab_title": tab["tab_title"],
                    "tab_menuno": tab["tab_menuno"],
                    "tab_url": tab["tab_url"],
                    "content_text_length": len(tab["content_text"]),
                    "headings_count": len(tab["content_structured"]["headings"]),
                    "paragraphs_count": len(tab["content_structured"]["paragraphs"]),
                    "lists_count": len(tab["content_structured"]["lists"]),
                    "tables_count": len(tab["content_structured"]["tables"])
                }
                tabs_data.append(tab_info)
        
        # 데이터프레임 생성
        df_pages = pd.DataFrame(pages_data)
        df_tabs = pd.DataFrame(tabs_data)
        
        # Excel 파일로 저장
        excel_path = f"{self.output_prefix}_summary.xlsx"
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df_pages.to_excel(writer, sheet_name='Pages', index=False)
            df_tabs.to_excel(writer, sheet_name='Tabs', index=False)
        
        print(f"Excel 파일 생성: {excel_path}")
        
        return excel_path
    
    def create_valid_filename(self, name):
        """유효한 파일명 생성"""
        # 파일명으로 사용할 수 없는 문자 제거
        return re.sub(r'[\\/*?:"<>|]', "_", name)
    
    def export_text_files(self):
        """각 탭의 텍스트 내용을 개별 파일로 내보내기"""
        # 텍스트 파일 저장 디렉토리
        text_dir = os.path.join(self.output_dir, "text_files")
        if not os.path.exists(text_dir):
            os.makedirs(text_dir)
        
        # 파일 경로 목록
        file_paths = []
        
        for page in self.data:
            for tab in page["tabs"]:
                # 파일명 생성
                filename = self.create_valid_filename(
                    f"{page['menu_num']}_{page['page_title']}_{tab['tab_title']}.txt"
                )
                file_path = os.path.join(text_dir, filename)
                
                # 텍스트 내용 저장
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(tab["content_text"])
                
                # 파일 경로 추가
                file_paths.append(file_path)
                print(f"텍스트 파일 생성: {file_path}")
        
        return file_paths
    
    def export_csv_files(self):
        """구조화된 데이터를 CSV 파일로 내보내기"""
        # CSV 파일 저장 디렉토리
        csv_dir = os.path.join(self.output_dir, "csv_files")
        if not os.path.exists(csv_dir):
            os.makedirs(csv_dir)
        
        # 헤딩 데이터
        headings_data = []
        
        # 문단 데이터
        paragraphs_data = []
        
        # 목록 데이터
        lists_data = []
        
        # 표 데이터
        tables_data = []
        
        for page in self.data:
            for tab in page["tabs"]:
                # 페이지와 탭 정보
                base_info = {
                    "menu_num": page["menu_num"],
                    "page_title": page["page_title"],
                    "tab_title": tab["tab_title"],
                    "tab_menuno": tab["tab_menuno"]
                }
                
                # 헤딩 데이터 추가
                for heading, levels in tab["content_structured"]["headings"].items():
                    for level in levels:
                        heading_info = base_info.copy()
                        heading_info.update({
                            "heading_text": heading,
                            "heading_level": level
                        })
                        headings_data.append(heading_info)
                
                # 문단 데이터 추가
                for i, paragraph in enumerate(tab["content_structured"]["paragraphs"]):
                    paragraph_info = base_info.copy()
                    paragraph_info.update({
                        "paragraph_id": i + 1,
                        "paragraph_text": paragraph
                    })
                    paragraphs_data.append(paragraph_info)
                
                # 목록 데이터 추가
                for i, lst in enumerate(tab["content_structured"]["lists"]):
                    for j, item in enumerate(lst["items"]):
                        list_info = base_info.copy()
                        list_info.update({
                            "list_id": i + 1,
                            "list_type": lst["type"],
                            "item_id": j + 1,
                            "item_text": item
                        })
                        lists_data.append(list_info)
                
                # 표 데이터 추가
                for i, table in enumerate(tab["content_structured"]["tables"]):
                    # 표 캡션 정보
                    if table["caption"]:
                        table_info = base_info.copy()
                        table_info.update({
                            "table_id": i + 1,
                            "content_type": "caption",
                            "row_id": 0,
                            "col_id": 0,
                            "cell_text": table["caption"]
                        })
                        tables_data.append(table_info)
                    
                    # 헤더 정보
                    for row_id, header_row in enumerate(table["headers"]):
                        for col_id, cell in enumerate(header_row):
                            table_info = base_info.copy()
                            table_info.update({
                                "table_id": i + 1,
                                "content_type": "header",
                                "row_id": row_id + 1,
                                "col_id": col_id + 1,
                                "cell_text": cell
                            })
                            tables_data.append(table_info)
                    
                    # 데이터 행 정보
                    for row_id, data_row in enumerate(table["rows"]):
                        for col_id, cell in enumerate(data_row):
                            table_info = base_info.copy()
                            table_info.update({
                                "table_id": i + 1,
                                "content_type": "data",
                                "row_id": len(table["headers"]) + row_id + 1,
                                "col_id": col_id + 1,
                                "cell_text": cell
                            })
                            tables_data.append(table_info)
        
        # 데이터프레임 생성 및 CSV 저장
        csv_paths = []
        
        # 헤딩 CSV
        if headings_data:
            df_headings = pd.DataFrame(headings_data)
            headings_path = os.path.join(csv_dir, "headings.csv")
            df_headings.to_csv(headings_path, index=False, encoding='utf-8-sig')
            csv_paths.append(headings_path)
            print(f"CSV 파일 생성: {headings_path}")
        
        # 문단 CSV
        if paragraphs_data:
            df_paragraphs = pd.DataFrame(paragraphs_data)
            paragraphs_path = os.path.join(csv_dir, "paragraphs.csv")
            df_paragraphs.to_csv(paragraphs_path, index=False, encoding='utf-8-sig')
            csv_paths.append(paragraphs_path)
            print(f"CSV 파일 생성: {paragraphs_path}")
        
        # 목록 CSV
        if lists_data:
            df_lists = pd.DataFrame(lists_data)
            lists_path = os.path.join(csv_dir, "lists.csv")
            df_lists.to_csv(lists_path, index=False, encoding='utf-8-sig')
            csv_paths.append(lists_path)
            print(f"CSV 파일 생성: {lists_path}")
        
        # 표 CSV
        if tables_data:
            df_tables = pd.DataFrame(tables_data)
            tables_path = os.path.join(csv_dir, "tables.csv")
            df_tables.to_csv(tables_path, index=False, encoding='utf-8-sig')
            csv_paths.append(tables_path)
            print(f"CSV 파일 생성: {tables_path}")
        
        return csv_paths

def main():
    # 인수 파서 설정
    parser = argparse.ArgumentParser(description='구조화된 데이터를 다양한 형식으로 내보내기')
    parser.add_argument('input_file', help='처리할 JSON 파일 경로')
    parser.add_argument('--format', choices=['excel', 'text', 'csv', 'all'], default='all',
                        help='내보낼 형식 (기본값: all)')
    
    args = parser.parse_args()
    
    # 입력 파일 확인
    if not os.path.exists(args.input_file):
        print(f"오류: 파일을 찾을 수 없습니다 - {args.input_file}")
        return
    
    # 데이터 내보내기
    exporter = DataExporter(args.input_file)
    
    if args.format in ['excel', 'all']:
        exporter.export_to_excel()
    
    if args.format in ['text', 'all']:
        exporter.export_text_files()
    
    if args.format in ['csv', 'all']:
        exporter.export_csv_files()

if __name__ == "__main__":
    main()
