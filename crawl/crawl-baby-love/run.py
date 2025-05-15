#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import subprocess
import time
from datetime import datetime

def run_crawler():
    print("=== 크롤러 실행 ===")
    subprocess.run(["python", "crawler.py"], check=True)

def run_processor():
    print("=== 데이터 처리 시작 ===")
    subprocess.run(["python", "processor.py"], check=True)

def run_exporter(json_file, export_format='all'):
    print(f"=== 데이터 내보내기 ({export_format}) ===")
    subprocess.run(["python", "exporter.py", json_file, "--format", export_format], check=True)

def find_latest_json_file(directory):
    """가장 최근 생성된 processed_data.json 파일 찾기"""
    for root, dirs, files in os.walk(directory):
        json_files = [os.path.join(root, file) for file in files if file == 'processed_data.json']
        if json_files:
            # 수정 시간 기준으로 가장 최근 파일 찾기
            latest_json = max(json_files, key=os.path.getmtime)
            return latest_json
    return None

def main():
    parser = argparse.ArgumentParser(description='childcare.go.kr 사이트 크롤링 파이프라인')
    parser.add_argument('--skip-crawl', action='store_true', help='크롤링 단계 건너뛰기')
    parser.add_argument('--skip-process', action='store_true', help='처리 단계 건너뛰기')
    parser.add_argument('--format', choices=['excel', 'text', 'csv', 'all'], default='all',
                        help='내보낼 형식 (기본값: all)')
    
    args = parser.parse_args()
    
    # 시작 시간 측정
    start_time = time.time()
    
    # 단계 1: 크롤링
    if not args.skip_crawl:
        run_crawler()
    else:
        print("=== 크롤링 단계 건너뛰기 ===")
    
    # 단계 2: 데이터 처리
    if not args.skip_process:
        run_processor()
    else:
        print("=== 처리 단계 건너뛰기 ===")
    
    # 단계 3: 데이터 내보내기
    # 가장 최근의 processed_data.json 파일 찾기
    base_path = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_path, "data")
    
    if os.path.exists(data_path):
        # 가장 최근 디렉토리 찾기
        dirs = [os.path.join(data_path, d) for d in os.listdir(data_path) 
                if os.path.isdir(os.path.join(data_path, d))]
        
        if dirs:
            latest_dir = max(dirs, key=os.path.getmtime)
            latest_json = find_latest_json_file(latest_dir)
            
            if latest_json:
                run_exporter(latest_json, args.format)
            else:
                print(f"오류: '{latest_dir}' 디렉토리에 processed_data.json 파일이 없습니다.")
        else:
            print(f"오류: '{data_path}' 내에 처리할 디렉토리가 없습니다.")
    else:
        print(f"오류: '{data_path}' 디렉토리가 존재하지 않습니다.")
    
    # 종료 시간 및 실행 시간 계산
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"=== 작업 완료 ===")
    print(f"총 실행 시간: {elapsed_time:.2f}초")

if __name__ == "__main__":
    main()
