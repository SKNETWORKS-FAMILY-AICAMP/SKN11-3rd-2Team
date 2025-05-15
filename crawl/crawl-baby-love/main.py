#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import os
from playwright.async_api import async_playwright
from datetime import datetime

# 저장 디렉토리 생성
def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"디렉토리 생성: {directory}")
    return directory

# 메인 함수
async def main():
    # 저장할 경로 설정
    base_path = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_path, "data")
    create_directory(data_path)
    
    # 현재 시간으로 폴더 생성
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    current_dir = os.path.join(data_path, current_time)
    create_directory(current_dir)
    
    # Playwright 시작
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # headless=True로 설정하면 화면 없이 실행
        context = await browser.new_context()
        page = await context.new_page()
        
        # 크롤링할 페이지 목록 (menuno=287 ~ 294)
        menu_numbers = range(287, 295)
        
        for menu_num in menu_numbers:
            # 메인 페이지 방문
            url = f"https://www.childcare.go.kr/?menuno={menu_num}"
            await page.goto(url)
            print(f"페이지 방문: {url}")
            
            # 페이지 제목 가져오기 (h3.title)
            page_title = await page.locator("h3.title").text_content()
            page_title = page_title.strip()
            print(f"페이지 제목: {page_title}")
            
            # 각 페이지의 디렉토리 생성
            page_dir = os.path.join(current_dir, f"{menu_num}_{page_title}")
            create_directory(page_dir)
            
            # 탭 있는지 확인
            has_tabs = await page.locator("ul.tab").count() > 0
            
            if has_tabs:
                # 각 탭의 링크 가져오기
                tab_links = await page.locator("ul.tab li a").all()
                
                for i, tab_link in enumerate(tab_links):
                    # 탭 제목 가져오기
                    tab_title = await tab_link.text_content()
                    tab_title = tab_title.strip()
                    
                    # 탭 URL 가져오기
                    tab_href = await tab_link.get_attribute("href")
                    
                    # menuno 파라미터 추출
                    menuno = None
                    if "menuno=" in tab_href:
                        menuno = tab_href.split("menuno=")[1].split("&")[0]
                    
                    if menuno:
                        tab_url = f"https://www.childcare.go.kr/?menuno={menuno}"
                        print(f"탭 접근: {tab_title} - {tab_url}")
                        
                        # 탭 페이지 방문
                        await page.goto(tab_url)
                        
                        # 페이지 콘텐츠 가져오기
                        content = await page.locator("section.contents_wrap").inner_html()
                        
                        # 파일로 저장
                        filename = f"{i+1}_{tab_title}.html"
                        file_path = os.path.join(page_dir, filename)
                        
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(content)
                        
                        print(f"파일 저장: {file_path}")
                        
                # 다시 원래 페이지로 돌아가기
                await page.goto(url)
            else:
                # 탭이 없는 경우 현재 페이지 내용만 저장
                content = await page.locator("section.contents_wrap").inner_html()
                
                # 파일로 저장
                filename = f"{page_title}.html"
                file_path = os.path.join(page_dir, filename)
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                
                print(f"파일 저장: {file_path}")
        
        # 브라우저 종료
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
