#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import glob
import time
from datetime import datetime
import argparse

def process_item(item, source_file, is_info=False):
    """
    각 항목(item)을 처리하는 함수
    
    Args:
        item (dict): 처리할 JSON 항목
        source_file (str): 소스 파일 이름
        is_info (bool): info 폴더의 파일인지 여부
    
    Returns:
        dict: 처리된 항목
    """
    # 원본 데이터 복사 (원본 변경 방지)
    processed_item = item.copy()
    
    # 소스 파일 정보 추가
    processed_item['source_file'] = source_file
    
    # info 폴더 파일에서는 comments 필드 제거
    if is_info and 'comments' in processed_item:
        del processed_item['comments']
    
    return processed_item

def merge_json_files(directory_path, output_filename, is_info=False):
    """
    지정된 디렉토리 내의 모든 JSON 파일을 하나의 JSON 파일로 병합
    
    Args:
        directory_path (str): 병합할 JSON 파일이 있는 디렉토리 경로
        output_filename (str): 출력 파일 이름
        is_info (bool): info 폴더의 파일인지 여부
    
    Returns:
        list: 병합된 데이터 리스트
    """
    # 결과를 저장할 리스트
    merged_data = []
    
    # 디렉토리 내의 모든 JSON 파일 경로 가져오기
    json_files = glob.glob(os.path.join(directory_path, "*.json"))
    total_files = len(json_files)
    
    print(f"총 {total_files}개 파일을 처리합니다.")
    
    # 처리 시작 시간
    start_time = time.time()
    
    # 각 JSON 파일을 읽어서 데이터 병합
    for idx, file_path in enumerate(json_files, 1):
        file_name = os.path.basename(file_path)
        
        # .DS_Store 파일 무시
        if file_name == '.DS_Store':
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
                
                # 단일 객체인 경우 리스트로 변환
                if isinstance(file_data, dict):
                    file_data = [file_data]
                
                # 각 항목 처리
                processed_items = [
                    process_item(item, file_name, is_info) 
                    for item in file_data
                ]
                
                # 병합 데이터에 추가
                merged_data.extend(processed_items)
            
            # 진행 상황 표시
            progress = (idx / total_files) * 100
            elapsed_time = time.time() - start_time
            est_total_time = elapsed_time * (total_files / idx)
            remaining_time = est_total_time - elapsed_time
            
            print(f"처리 중: {idx}/{total_files} ({progress:.1f}%) - {file_name}")
            print(f"  - 진행 시간: {format_time(elapsed_time)} / 남은 시간: {format_time(remaining_time)}")
            
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {file_path} - {str(e)}")
        except Exception as e:
            print(f"처리 오류: {file_path} - {str(e)}")
    
    # 중복 제거 (선택적)
    # merged_data = remove_duplicates(merged_data)
    
    # 병합된 데이터를 파일로 저장
    output_file_path = os.path.join(os.path.dirname(directory_path), output_filename)
    
    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
        print(f"병합 완료: {len(merged_data)}개의 항목이 {output_file_path}에 저장되었습니다.")
    except Exception as e:
        print(f"파일 저장 오류: {output_file_path} - {str(e)}")
    
    return merged_data

def format_time(seconds):
    """
    초 단위 시간을 사람이 읽기 쉬운 형식으로 변환
    """
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours > 0:
        return f"{hours}시간 {minutes}분 {seconds}초"
    elif minutes > 0:
        return f"{minutes}분 {seconds}초"
    else:
        return f"{seconds}초"

def remove_duplicates(data_list, key_fields=None):
    """
    중복 항목 제거 (선택적)
    
    Args:
        data_list (list): 데이터 리스트
        key_fields (list): 중복 확인에 사용할 필드 목록
    
    Returns:
        list: 중복이 제거된 데이터 리스트
    """
    if not key_fields:
        # 기본적으로 'id' 필드로 중복 확인
        key_fields = ['id']
    
    unique_data = {}
    
    for item in data_list:
        # 키 필드를 모두 포함하는 항목만 처리
        if all(field in item for field in key_fields):
            # 키 필드의 값을 조합하여 고유 키 생성
            key = tuple(item.get(field) for field in key_fields)
            unique_data[key] = item
    
    return list(unique_data.values())

def create_backup(file_path):
    """
    파일 백업 함수
    """
    if os.path.exists(file_path):
        backup_dir = os.path.join(os.path.dirname(file_path), 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.basename(file_path)
        backup_path = os.path.join(backup_dir, f"{filename}.{timestamp}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as src_file:
                with open(backup_path, 'w', encoding='utf-8') as dst_file:
                    dst_file.write(src_file.read())
            print(f"백업 생성: {backup_path}")
            return True
        except Exception as e:
            print(f"백업 생성 실패: {e}")
            return False
    
    return False

def main():
    parser = argparse.ArgumentParser(description='JSON 파일 병합 스크립트')
    parser.add_argument('--backup', action='store_true', help='기존 파일 백업 생성')
    args = parser.parse_args()
    
    # 기본 경로 설정
    base_path = '/Users/link/Documents/SKN/4th_project_3/data'
    info_path = os.path.join(base_path, 'info')
    question_path = os.path.join(base_path, 'question')
    
    # 출력 파일 경로
    info_output = 'info.json'
    question_output = 'question.json'
    
    # 백업 생성 (선택적)
    if args.backup:
        for file_path in [os.path.join(base_path, info_output), 
                         os.path.join(base_path, question_output)]:
            create_backup(file_path)
    
    print(f"작업 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # info 폴더의 JSON 파일 병합 (comments 필드 제거)
    print("\ninfo 폴더 파일 병합 중...")
    info_data = merge_json_files(info_path, info_output, is_info=True)
    
    # question 폴더의 JSON 파일 병합
    print("\nquestion 폴더 파일 병합 중...")
    question_data = merge_json_files(question_path, question_output, is_info=False)
    
    print(f"\n작업 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"총 처리 결과: info.json ({len(info_data)}개 항목), question.json ({len(question_data)}개 항목)")

if __name__ == "__main__":
    main()
