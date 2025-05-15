#!/usr/bin/env python
# coding: utf-8

import os
import json
import glob
from tqdm import tqdm
from dotenv import load_dotenv
import ast


load_dotenv()
def main():
    # 환경 변수에서 메뉴명 리스트 가져오기
    menu_name_list_raw = os.environ.get('MANU_NAME_LIST', '')   
    menu_name_list = [menu.strip() for menu in menu_name_list_raw.split(',')]

    menu_name_list = [
    '#LIVE#보험방송#선물#즉답', '[인증]K클래스 경품&선물 자랑', '[일정]K클래스 임신육아교실', '[일정]두드림 산모교실',
    '[일정]맘스스토리 임신육아교실', '[후기]K클래스 임신육아교실', '[후기]두드림 산모교실', '[후기]맘스스토리 임신육아교실',
    '★두잉박스 신청', '★모든 핫딜 쇼핑★', '★무료 임신축하선물', '★이벤트&체험단 공유/홍보',
    '★전국 육아박람회', '★전국 임신육아교실', '★크베맘 선물2종 신청', '★크베맘박스 신청',
    '★필수 육아 정보', 'TV드라마[얘기방]', '가족/아이/만삭사진', '가입인사[첫인사]',
    '공식 홈페이지', '공지', '공지위반[신고]', '내돈내산 쇼핑 후기',
    '놀이/여행/기타', '대구 제니스뷔페 달서점', '동안미소한의원', '베스트글[참여종료]',
    '배경화면[인증샷]', '복지혜택[맘정보]', '쇼핑/제품 후기', '소리맘 산모교실',
    '소소한 가족의 행복', '소확행[육퇴인증]', '손재주/인테리어', '시끌벅적[수다방]',
    '아이폰 어플', '안드로이드 어플', '인스타그램', '유튜브',
    '제휴문의', '└ 장바구니 질문!', '이벤트 꿀정보(스크랩글X)', '이야기쫌[속풀이]',
    '오늘뭐입지[패션]', '오늘의 택배[언박싱]', '음식/요리/맛집', '임신육아교실 후기',
    '중고벼룩[팝니다]', '중고벼룩[구합니다]', '크베맘 손글씨', '크베맘[베스트글]',
    '크베맘[약속실천인증]', '크베앱[출석인증샷]', '필독', '필독 공지사항',
    '함소아, 우리가족주치의', '현대해상 베이비페어', '육아용품 후기(체험단X)', '무료 포토북 후기',
    '└ 강원도', '└ 경상권', '└ 광주', '└ 대구',
    '└ 대전', '└ 부산', '└ 서울', '└ 인천',
    '└ 울산', '└ 전라권', '└ 제주도', '└ 충청권',
    '└ 스페셜 선물 후기', '└ 보험 상담 신청', '☞ 이벤트 안내', '☞ 이벤트 당첨자발표',
    '☞ 이벤트 후기', '☞ 체험단 후기', '서포터즈(마감)', '카페출석부[끝말잇기]',
    '맛있는 레시피 노하우', 
]

    
    # 환경 변수에서 입력 디렉토리 경로 가져오기
    input_dir = os.environ.get('INPUT_DIR', './filtered_output')
    
    # 환경 변수에서 출력 파일 경로 가져오기
    output_file = os.environ.get('OUTPUT_FILE', './filtered/filtered_data.json')
    
    print(f"입력 디렉토리 경로: {input_dir}")
    print(f"출력 파일 경로: {output_file}")
    
    # 모든 JSON 파일 목록 가져오기
    json_files = glob.glob(os.path.join(input_dir, '*.json'))
    
    # 필터링된 데이터를 저장할 리스트
    filtered_data = []
    
    # 각 파일 처리
    for file_path in tqdm(json_files, desc="파일 처리 중"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # 각 항목을 순회하며 menuName이 제외 리스트에 없는 경우만 추가
                for item in data:
                    if 'menuName' in item and item['menuName'] not in menu_name_list:
                        filtered_data.append(item)
        except Exception as e:
            print(f"파일 처리 중 오류 발생: {file_path}, 오류: {e}")
    
    # 총 항목 수 계산
    total_items = sum(len(data) for file_path in json_files for data in [json.load(open(file_path, 'r', encoding='utf-8'))])
    
    # 필터링된 데이터 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=4)
    
    print(f"총 {len(json_files)}개 파일, {total_items}개 항목 중 {len(filtered_data)}개 항목이 필터링되어 저장되었습니다.")
    print(f"필터링된 데이터가 {output_file}에 저장되었습니다.")
    print(f"필터링된 메뉴: {menu_name_list}")
    
    # 각 메뉴의 개수 확인 위한 통계
    menu_counts = {}
    for file_path in json_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                if 'menuName' in item:
                    menu_name = item['menuName']
                    menu_counts[menu_name] = menu_counts.get(menu_name, 0) + 1
    
    print("\n메뉴별 항목 수:")
    for menu, count in sorted(menu_counts.items(), key=lambda x: x[1], reverse=True):
        if menu in menu_name_list:
            print(f" - {menu}: {count} (필터링 대상)")
        else:
            print(f" - {menu}: {count}")
    
    # 제외된 항목 수
    filtered_out_count = total_items - len(filtered_data)
    print(f"\n필터링으로 제외된 항목 수: {filtered_out_count}")
    print(f"필터링 비율: {filtered_out_count / total_items * 100:.2f}%")

if __name__ == "__main__":
    main()
