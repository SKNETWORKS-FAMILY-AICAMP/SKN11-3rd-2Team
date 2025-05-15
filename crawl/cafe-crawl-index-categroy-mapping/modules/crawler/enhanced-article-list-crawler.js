/**
 * 향상된 네이버 카페 게시글 목록 크롤러
 * API를 우선 사용하고, 실패 시 기존 HTML 파싱 방식으로 폴백합니다.
 */
const config = require('../../config/config');
const { log, logError } = require('../../lib/logger');
const { sleep, getRandomDelay } = require('../../lib/utils');
const { getArticleList: getLegacyArticleList } = require('./article-list');
const { getArticleListFromApi } = require('../api/article-list-api');

/**
 * 향상된 네이버 카페 게시글 목록 크롤링
 * API 호출을 먼저 시도하고, 실패 시 HTML 파싱을 사용합니다.
 * @param {Object} page Playwright 페이지 객체
 * @param {Object} options 크롤링 옵션
 * @param {number} options.pageNum 페이지 번호 (기본값: 1)
 * @param {number} options.pageSize 페이지당 게시글 수 (기본값: 환경변수에서 가져오기, 기본 5개)
 * @param {string} options.sortBy 정렬 기준 (기본값: 'TIME')
 * @param {string} options.menuId 메뉴 ID (기본값: '0', 전체글)
 * @param {boolean} options.forceHtml HTML 파싱 방식 강제 사용 (기본값: false)
 * @param {boolean} options.forceApi API 방식 강제 사용 (기본값: false)
 * @param {number} options.requiredCount 필요한 게시글 수 (기본값: 10)
 * @param {string} options.lastArticleId 마지막으로 수집한 게시글 ID (기본값: '')
 * @param {boolean} options.continueFromLast 마지막 ID 이후부터 수집 (기본값: false)
 * @returns {Promise<Array>} 게시글 목록 배열
 */
async function getArticleList(page, options = {}) {
  const {
    pageNum = 1,
    pageSize = config.crawler.pageSize || 50, // 페이지당 게시글 수를 환경변수에서 가져오기
    sortBy = 'TIME',
    menuId = '0',
    forceHtml = false,
    forceApi = false,
    requiredCount = 10,
    lastArticleId = '',
    continueFromLast = false
  } = options;

  // API 방식과 HTML 파싱 방식 중 어떤 방식을 사용할지 결정
  const useApi = !forceHtml || forceApi;
  const useHtml = !forceApi || forceHtml;

  let articles = [];

  // 1. API 방식 시도
  if (useApi) {
    log(`API 방식으로 페이지 ${pageNum} 게시글 목록 가져오기 시도`);
    
    try {
      articles = await getArticleListFromApi(page, {
        pageNum,
        pageSize,
        sortBy,
        viewType: 'L',
        menuId
      });
      
      // API 호출이 성공적으로 게시글을 가져왔다면
      if (articles.length > 0) {
        log(`API에서 ${articles.length}개의 게시글을 성공적으로 가져옴`);
        
        // 마지막 게시글 ID부터 계속 수집하는 경우
        if (continueFromLast && lastArticleId) {
          log(`이전에 수집한 게시글 ID ${lastArticleId} 이후부터 필터링...`);
          
          const originalCount = articles.length;
          // ID 기준으로 필터링 (최신 게시글이 더 큰 ID를 가짐)
          articles = articles.filter(article => {
            try {
              return parseInt(article.id) > parseInt(lastArticleId);
            } catch (e) {
              // ID가 숫자가 아닐 경우 기본적으로 포함
              return true;
            }
          });
          
          log(`총 ${originalCount}개 중 ${articles.length}개의 새 게시글 찾음`);
        }
        
        return articles.slice(0, requiredCount);
      } else {
        log('API에서 게시글을 가져오지 못함, HTML 파싱 방식으로 전환', 'warn');
      }
    } catch (error) {
      logError(error, 'API 게시글 목록 가져오기 실패');
      log('HTML 파싱 방식으로 전환', 'warn');
    }
  }

  // 2. API 방식이 실패하거나 강제 HTML 파싱 모드인 경우, HTML 파싱 방식 시도
  if (useHtml && articles.length === 0) {
    log(`HTML 파싱 방식으로 페이지 ${pageNum} 게시글 목록 가져오기 시도`);
    
    try {
      articles = await getLegacyArticleList(page, { pageNum, requiredCount });
      log(`HTML 파싱에서 ${articles.length}개의 게시글을 가져옴`);
      
      // 마지막 게시글 ID부터 계속 수집하는 경우 (HTML 방식에서도 적용)
      if (continueFromLast && lastArticleId && articles.length > 0) {
        log(`이전에 수집한 게시글 ID ${lastArticleId} 이후부터 필터링...`);
        
        const originalCount = articles.length;
        articles = articles.filter(article => {
          try {
            return parseInt(article.id) > parseInt(lastArticleId);
          } catch (e) {
            return true;
          }
        });
        
        log(`총 ${originalCount}개 중 ${articles.length}개의 새 게시글 찾음`);
      }
    } catch (error) {
      logError(error, 'HTML 파싱 게시글 목록 가져오기 실패');
      // 두 방식 모두 실패한 경우 빈 배열 반환
      return [];
    }
  }

  return articles.slice(0, requiredCount);
}

/**
 * 여러 페이지의 게시글 목록 가져오기
 * @param {Object} page Playwright 페이지 객체
 * @param {Object} options 크롤링 옵션
 * @param {number} options.startPage 시작 페이지 (기본값: 환경변수에서 가져오기, 1)
 * @param {number} options.endPage 종료 페이지 (기본값: 환경변수에서 가져오기, 10)
 * @param {number} options.pageSize 페이지당 게시글 수 (기본값: 환경변수에서 가져오기, 5)
 * @param {string} options.sortBy 정렬 기준 (기본값: 'TIME')
 * @param {string} options.menuId 메뉴 ID (기본값: '0', 전체글)
 * @param {boolean} options.forceHtml HTML 파싱 방식 강제 사용 (기본값: false)
 * @param {boolean} options.forceApi API 방식 강제 사용 (기본값: false)
 * @param {number} options.totalRequired 필요한 총 게시글 수 (기본값: 50)
 * @param {string} options.lastArticleId 마지막으로 수집한 게시글 ID (기본값: '')
 * @param {boolean} options.continueFromLast 마지막 ID 이후부터 수집 (기본값: false)
 * @param {number} options.batchSize 한 번에 수집할 페이지 수 (기본값: 환경변수에서 가져오기, 5)
 * @param {boolean} options.parallel 병렬 처리 여부 (기본값: true)
 * @returns {Promise<Array>} 모든 페이지의 게시글 목록 배열
 */
async function getMultiPageArticles(page, options = {}) {
  const {
    startPage = config.crawler.startPage || 1,
    endPage = config.crawler.endPage || 10,
    pageSize = config.crawler.pageSize || 50,
    sortBy = 'TIME',
    menuId = '0',
    forceHtml = false,
    forceApi = false,
    totalRequired = 50,
    lastArticleId = '',
    continueFromLast = false,
    batchSize = config.crawler.batchSize || 5,
    parallel = true
  } = options;
  
  let allArticles = [];
  
  // 공통 옵션 추출
  const commonOptions = {
    pageSize,
    sortBy,
    menuId,
    forceHtml,
    forceApi,
    lastArticleId,
    continueFromLast
  };
  
  // 페이지 범위를 batchSize 단위로 나누어 처리
  for (let batchStart = startPage; batchStart <= endPage; batchStart += batchSize) {
    const batchEnd = Math.min(batchStart + batchSize - 1, endPage);
    log(`페이지 ${batchStart}부터 ${batchEnd}까지의 게시글 목록 배치 처리 시작...`);
    
    // 병렬 처리를 사용하는 경우
    if (parallel) {
      const pagePromises = [];
      
      // 배치 내 페이지들에 대한 요청을 병렬로 생성
      for (let pageNum = batchStart; pageNum <= batchEnd; pageNum++) {
        log(`${pageNum}페이지 게시글 목록 병렬 요청 준비...`);
        
        const promise = getArticleList(page, {
          ...commonOptions,
          pageNum,
          requiredCount: Math.min(pageSize, totalRequired - allArticles.length)
        });
        
        pagePromises.push(promise);
      }
      
      // 모든 페이지 요청 병렬 실행
      log(`${pagePromises.length}개의 페이지 요청을 병렬로 처리 중...`);
      const results = await Promise.all(pagePromises);
      
      // 결과 처리
      for (let i = 0; i < results.length; i++) {
        const articles = results[i];
        const pageNum = batchStart + i;
        
        // 새 게시글이 없는 경우 (이전에 수집한 ID 이후가 없음)
        if (articles.length === 0 && continueFromLast && lastArticleId) {
          log(`${pageNum}페이지에서 이전에 수집한 ID ${lastArticleId} 이후의 새 게시글이 없습니다.`);
          continue;
        }
        
        // 결과에 추가
        allArticles = allArticles.concat(articles);
        
        // 더 이상 게시글이 없는 경우 로깅
        if (articles.length === 0 || articles.length < pageSize) {
          log(`페이지 ${pageNum}에서 게시글이 ${articles.length}개 밖에 없습니다.`);
        }
      }
      
      // 필요한 게시글 수를 모두 가져온 경우
      if (allArticles.length >= totalRequired) {
        log(`필요한 게시글 수(${totalRequired}개)를 모두 가져와 종료합니다.`);
        return allArticles.slice(0, totalRequired);
      }
      
      // 더 이상 게시글이 없으면 종료
      if (results.every(articles => articles.length === 0 || articles.length < pageSize)) {
        log(`더 이상 게시글이 없어 종료합니다.`);
        return allArticles;
      }
    } else {
      // 기존 코드: 배치 단위로 순차 처리
      for (let pageNum = batchStart; pageNum <= batchEnd; pageNum++) {
        log(`${pageNum}페이지 게시글 목록 가져오는 중...`);
        
        // 게시글 목록 가져오기
        const articles = await getArticleList(page, {
          ...commonOptions,
          pageNum,
          requiredCount: Math.min(pageSize, totalRequired - allArticles.length)
        });
        
        // 새 게시글이 없는 경우 (이전에 수집한 ID 이후가 없음)
        if (articles.length === 0 && continueFromLast && lastArticleId) {
          log(`${pageNum}페이지에서 이전에 수집한 ID ${lastArticleId} 이후의 새 게시글이 없습니다.`);
          
          // 이미 충분한 게시글을 수집했거나 더 이상 페이지가 없으면 종료
          if (allArticles.length >= totalRequired || pageNum >= batchEnd) {
            break;
          }
          
          // 새 게시글을 찾을 때까지 다음 페이지로 계속 진행
          await sleep(getRandomDelay(config.crawler.delay.min, config.crawler.delay.max));
          continue;
        }
        
        // 결과에 추가
        allArticles = allArticles.concat(articles);
        
        // 필요한 게시글 수를 모두 가져온 경우 종료
        if (allArticles.length >= totalRequired) {
          log(`필요한 게시글 수(${totalRequired}개)를 모두 가져와 종료합니다.`);
          return allArticles.slice(0, totalRequired);
        }
        
        // 페이지 간 딜레이
        if (pageNum < batchEnd && allArticles.length < totalRequired) {
          await sleep(getRandomDelay(config.crawler.delay.min, config.crawler.delay.max));
        }
        
        // 더 이상 게시글이 없으면 종료
        if (articles.length === 0 || articles.length < pageSize) {
          log(`페이지 ${pageNum}에서 게시글이 ${articles.length}개 밖에 없어 종료합니다.`);
          return allArticles;
        }
      }
    }
    
    // 배치 간 더 긴 딜레이 추가 (API 제한 방지)
    if (batchStart + batchSize <= endPage && allArticles.length < totalRequired) {
      log(`페이지 배치 처리 완료, 다음 배치 전 잠시 대기...`);
      await sleep(getRandomDelay(config.crawler.delay.max, config.crawler.delay.max * 2));
    }
  }
  
  log(`총 ${allArticles.length}개의 게시글 정보 수집 완료`);
  return allArticles.slice(0, totalRequired);
}

module.exports = {
  getArticleList,
  getMultiPageArticles
};