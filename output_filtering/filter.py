import json
import re

def filter_promotional_posts(json_file_path, output_file_path=None):
    """
    육아 카페에서 크롤링한 JSON 데이터에서 광고, 이벤트, 출석 관련 게시글을 필터링하는 함수
    
    Parameters:
    json_file_path (str): 입력 JSON 파일 경로
    output_file_path (str, optional): 필터링된 결과를 저장할 파일 경로. 지정하지 않으면 'filtered_' + 원본 파일명으로 저장
    
    Returns:
    dict: 필터링된 데이터
    """
    # 파일 읽기
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 필터링 전 게시글 수
    before_count = len(data.get('articles', [])) if isinstance(data, dict) else len(data)
    print(f"필터링 전 게시글 수: {before_count}")
    
    # 필터링할 키워드 패턴 정의
    filter_patterns = [
        # 이벤트 관련 패턴
        r'\[이벤트\]', r'\(이벤트\)', r'이벤트', r'응모', r'당첨', r'선물', r'혜택', 
        r'쿠폰', r'할인', r'무료', r'공짜', r'경품', r'퀴즈', r'수다왕', r'쇼핑라이브',
        r'울쎄라', r'skt',
        
        # 광고 관련 패턴
        r'\[광고\]', r'\(광고\)', r'홍보', r'추천', r'리뷰', r'후기', r'체험단', r'박스',
        r'상품', r'쇼핑', r'라이브', r'특가', r'기획전', r'구매', r'판매', r'입점', r'증정',
        r'핫딜', r'1+1', r'1 + 1',
        
        # 출석 관련 패턴
        r'\[출석\]', r'\(출석\)', r'출석', r'출석체크', r'출석부', r'출첵', r'인증', r'안녕', r'인사',
        r'좋은아침', r'굿모닝',

        # 공지 관련 패턴
        r'\[안내\]', r'\(안내\)', r'안내',  r'\[공지\]', r'공지', r'주의', r'필독', r'전국\s?\S+',
        r'박람회', r'전시회', r'페어', r'유아교육전',

         # 일상/음식/기타 비관련
        r'맥주', r'소주', r'형주', r'루비락', r'다이어트', r'커피', r'카페', r'쇼핑', r'브랜드',
        r'할인', r'배송', r'주식', r'부동산', r'자동차', r'드라마', r'영화', r'예능', r'운세',
        r'반려동물', r'맛집', r'재테크', r'연예인', r'출근', r'퇴근', r'회사', r'직장', r'운전',
        r'화장품', r'피부관리', r'스킨케어', r'메이크업', r'명언', r'헬스', r'요가', r'패션',
        r'쿠폰', r'이벤트', r'체험단', r'포인트', r'적립', r'홍보', r'리뷰', r'가입', r'상담',
        r'공구', r'클릭', r'링크', r'후기', r'사은품', r'경품', r'제품', r'등록', r'신청',

        # 금액 표현 패턴
        r'\b\d{1,3}(,\d{3})?원\b',        # 8,300원 / 8300원
        r'\b\d+(만원|천원)\b',           # 5만원 / 7천원
        r'\b\d{1,3}(,\d{3})?\s?원\b',     # 12,000 원 (공백 포함 버전)

        # 일상/잡담/기타
        r'서브웨이', r'짜파게티', r'씨리얼', r'볶음밥', r'감자볶음', r'파김치', r'실내자전거', 
        r'다이어트', r'요리했어요', r'짐 싸봅니다', r'넷플릭스', r'치맥', r'술한잔', r'맥주', 
        r'드라마', r'설날 약속', r'장바구니', r'위약금', r'정수기 렌탈', r'생리통'

        # 날씨/감정
        r'연휴의 끝', r'오늘 날씨', r'시간 참 빠르네요', r'오늘도 고생했어요', r'눈 마사지기', 
        r'혼자만의 자유시간', r'비가 와요', r'피곤해요', r'집콕', r'스트레스', r'갱년기', r'졸려요'

        # 이벤트/기획전/모임
        r'이모티콘', r'게릴라', r'댓글 참여', r'베이비페어', r'킨텍스', r'맘스스토리', r'산모교실', 
        r'돌잔치', r'홍보', r'공식 인증 제품', r'샤워 이벤트'

        # 쇼핑/제품 후기
        r'내돈내산', r'공식 인증', r'제품 소개', r'정밀하게 알려줘', r'최저가', r'쿠팡', r'구매했어요', 
        r'배송', r'추천드립니다', r'1등급 성능', r'찜질기', r'건강기능식품', r'후기', r'공진단', r'경옥고', 
        r'자운고', r'건강식품 제공', r'출연료O'

        # 마케팅 문구
        r'이벤트', r'푸짐한 경품', r'참여 선물', r'경품확인', r'무료', r'할인', r'특가', r'비포에프터', 
        r'후기 링크', r'쪽지보내드릴게요', r'위 링크 참조'

        # 금액 표현
        r'\d{1,3}(,\d{3})*원', r'\d{1,3}(,\d{3})*만원', r'\d{1,3}원', r'\d{1,3}만\s?원', r'\d{1,3}(,\d{3})*원\s?정도'

        # 빈도 기반 연관성 없는 단어어
        r'점심', r'저녁', r'아침', r'간식', r'볶음밥', r'서브웨이', r'짜파게티', r'다이어트',
        r'날씨', r'넷플릭스', r'반갑습니다', r'육퇴', r'낮잠', r'치맥', r'술한잔', r'배고파',
        r'졸려', r'커피', r'빨래', r'짐싸기', r'감자볶음', r'장바구니', r'위약금', r'집콕',
        r'갱년기', r'비가와요', r'시간 참 빠르네요', r'오늘도 고생했어요', r'눈마사지기',
        r'혼자만의 자유시간', r'스트레스', r'일기', r'출근', r'퇴근',

        # 문장
        "아기 로션",
        "수분크림대용량 적당해요",
        "수원메쎄 코베 왔어요~~",
        "토마토가 싱싱해서 가져왔어요",
        "딸기청 고르는 기준 좀 알려주세요!",
        "범보의자에서 이유식 시작하려는데 괜찮은가요??",
        "카시트 사려고 하는데 정보 부탁드려용~",
        "돌촬영 원피스",
        "편의점",
        "배도라지 주스",
        "밀푀유나베",
        "집안 공기 청정기?",
        "지갑",
        "킨더 초콜릿",

        r'점심', r'점심은', r'오늘', r'유모차', r'ㅎㅎ', r'댓제', r'카시트', r'ㅠㅠ', r'오늘의', r'너무',
        r'벌써', r'휴대용', r'있어요', r'가격', r'반가워요', r'왔어요', r'분들',
        r'있나요', r'14', r'시크', r'청소', r'수원', r'이모티콘', r'50', r'햄버거', r'다녀왔어요',
        r'먹었어요',

        r'너무', r'많이', r'있는', r'오늘', r'ㅎㅎ', r'같아요', r'이벤트', r'있어서',
        r'정말', r'다들', r'pzp', r'요즘', r'있어요', r'점심', r'해서', r'00', r'하고',
        r'바로', r'혹시', r'저는', r'다른', r'제가', r'진짜', r'먹고', r'점심은', r'/'

    ]

    # 키워드 패턴 통합
    combined_pattern = re.compile('|'.join(filter_patterns), re.IGNORECASE)
    
    # 필터링된 게시글을 저장할 리스트
    if isinstance(data, dict) and 'articles' in data:
        # 'articles' 키가 있는 경우
        filtered_data = {
            'articles': [
                article for article in data['articles'] 
                if not combined_pattern.search(article.get('title', ''))
            ]
        }
        
        # 다른 키가 있는 경우 복사
        for key in data:
            if key != 'articles':
                filtered_data[key] = data[key]
    else:
        # 'articles' 키가 없는 경우 (리스트 형태)
        filtered_data = [
            article for article in data 
            if not combined_pattern.search(article.get('title', ''))
        ]
    
    # 필터링 후 게시글 수
    after_count = len(filtered_data.get('articles', [])) if isinstance(filtered_data, dict) else len(filtered_data)
    print(f"필터링 후 게시글 수: {after_count}")
    print(f"제거된 게시글 수: {before_count - after_count}")
    
    # 결과 저장
    if output_file_path is None:
        # 출력 파일명 생성
        filename = json_file_path.split('/')[-1]
        output_file_path = 'filtered_' + filename
    
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=2)
    
    print(f"필터링된 데이터가 {output_file_path}에 저장되었습니다.")
    
    return filtered_data

# 필터링된 게시글의 제목을 확인하는 함수
def check_filtered_posts(json_file_path):
    """
    필터링된 JSON 데이터의 게시글 제목을 출력하는 함수
    
    Parameters:
    json_file_path (str): JSON 파일 경로
    """
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    articles = data.get('articles', []) if isinstance(data, dict) else data
    
    print(f"총 {len(articles)}개 게시글:")
    for i, article in enumerate(articles[:20], 1):  # 처음 20개만 출력
        print(f"{i}. {article.get('title', '제목 없음')}")
    
    if len(articles) > 20:
        print(f"... 외 {len(articles) - 20}개")

# 사용 예시
if __name__ == "__main__":
    # 파일 경로는 실제 환경에 맞게 수정해주세요
    for i in range(1, 134):
        input_file = f"./output/{i}.json"
        output_file = f"./filtered_output/filtered_data{i}.json"
        
        # 필터링 실행
        filtered_data = filter_promotional_posts(input_file, output_file)
        
        # 필터링된 결과 확인
        check_filtered_posts(output_file)