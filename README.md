# YouTube 상승세 채널 발굴기 (YouTube Rising Channel Finder)

구독자 수는 적지만 조회수가 폭발적으로 높은 알짜 채널을 발굴하기 위한 도구입니다.

## 주요 기능
- 키워드별 영상 검색
- 특정 기간 내 업로드된 영상 필터링
- 구독자 수 대비 조회수 비율(배수) 계산
- 결과 데이터 CSV 다운로드

## 설치 및 실행 방법

1. 필수 라이브러리 설치:
   ```bash
   pip install -r requirements.txt
   ```

2. 프로그램 실행:
   ```bash
   streamlit run app.py
   ```

3. 브라우저에서 YouTube API Key를 입력하고 검색을 시작하세요.

## 기술 스택
- Streamlit
- YouTube Data API v3
- Pandas
