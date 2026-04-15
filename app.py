import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
from datetime import datetime, timedelta

# --- 페이지 설정 ---
st.set_page_config(page_title="YouTube 상승세 채널 발굴기", layout="wide")

# --- 사이드바: 설정 및 필터 ---
st.sidebar.title("🔍 검색 설정")

api_key = st.sidebar.text_input("YouTube API Key를 입력하세요", type="password")
keyword = st.sidebar.text_input("검색 키워드", placeholder="예: 브이로그, 캠핑, 테크")

# 영상 길이 설정
duration_options = {
    "전체": "any",
    "짧음 (4분 미만)": "short",
    "중간 (4~20분)": "medium",
    "김 (20분 이상)": "long"
}
duration_label = st.sidebar.selectbox("영상 길이", list(duration_options.keys()))
duration_value = duration_options[duration_label]

# 국가 및 언어 설정
region_options = {"대한민국": "KR", "미국": "US", "일본": "JP", "전체": None}
region_label = st.sidebar.selectbox("국가 선택", list(region_options.keys()))
region_value = region_options[region_label]

lang_options = {"한국어": "ko", "영어": "en", "일본어": "ja", "전체": None}
lang_label = st.sidebar.selectbox("언어 선택", list(lang_options.keys()))
lang_value = lang_options[lang_label]

# 기간 설정
days_back = st.sidebar.number_input("최근 몇 일 이내 영상?", min_value=1, max_value=365, value=30)
published_after = (datetime.utcnow() - timedelta(days=days_back)).isoformat() + "Z"

st.sidebar.divider()
st.sidebar.title("📈 상승세 필터")
max_subs = st.sidebar.number_input("최대 구독자 수", min_value=0, value=10000, step=1000)
min_views = st.sidebar.number_input("최소 조회수", min_value=0, value=50000, step=5000)
min_ratio = st.sidebar.number_input("구독자 대비 조회수 최소 배수 (예: 10배)", min_value=1.0, value=5.0, step=0.5)

# --- 메인 화면 ---
st.title("🚀 YouTube 상승세 채널 발굴 프로그램")
st.write("구독자 수는 적지만 조회수가 폭발적으로 높은 알짜 채널을 찾아보세요.")

if st.button("검색 시작"):
    if not api_key:
        st.error("API Key를 입력해주세요.")
    elif not keyword:
        st.error("검색 키워드를 입력해주세요.")
    else:
        try:
            youtube = build("youtube", "v3", developerKey=api_key)
            
            with st.spinner("YouTube 데이터를 가져오는 중..."):
                # 1. 영상 검색 (search.list)
                search_params = {
                    "q": keyword,
                    "part": "snippet",
                    "type": "video",
                    "maxResults": 50,
                    "videoDuration": duration_value,
                    "publishedAfter": published_after,
                    "order": "viewCount" # 조회수 높은 순으로 1차 시도 (API 제약상 완벽하진 않음)
                }
                if region_value: search_params["regionCode"] = region_value
                if lang_value: search_params["relevanceLanguage"] = lang_value
                
                search_response = youtube.search().list(**search_params).execute()
                
                items = search_response.get("items", [])
                if not items:
                    st.warning("검색 결과가 없습니다.")
                else:
                    video_ids = [item["id"]["videoId"] for item in items]
                    channel_ids = [item["snippet"]["channelId"] for item in items]
                    
                    # 2. 영상 상세 정보 가져오기 (videos.list) - 정확한 조회수 확인
                    video_response = youtube.videos().list(
                        part="statistics,snippet",
                        id=",".join(video_ids)
                    ).execute()
                    
                    video_data = {}
                    for v in video_response.get("items", []):
                        video_data[v["id"]] = {
                            "title": v["snippet"]["title"],
                            "viewCount": int(v["statistics"].get("viewCount", 0)),
                            "channelId": v["snippet"]["channelId"],
                            "channelTitle": v["snippet"]["channelTitle"],
                            "publishedAt": v["snippet"]["publishedAt"]
                        }
                    
                    # 3. 채널 정보 가져오기 (channels.list) - 구독자 수 확인
                    # 중복 채널 ID 제거
                    unique_channel_ids = list(set(channel_ids))
                    channel_response = youtube.channels().list(
                        part="statistics",
                        id=",".join(unique_channel_ids)
                    ).execute()
                    
                    channel_subs = {}
                    for c in channel_response.get("items", []):
                        channel_subs[c["id"]] = int(c["statistics"].get("subscriberCount", 0))
                    
                    # 4. 데이터 병합 및 필터링
                    results = []
                    for vid, info in video_data.items():
                        subs = channel_subs.get(info["channelId"], 0)
                        views = info["viewCount"]
                        
                        # 상승세 조건 체크
                        # 1. 최대 구독자 수 조건
                        # 2. 최소 조회수 조건
                        if subs <= max_subs and views >= min_views:
                            # 3. 배수 계산 (분모가 0인 경우 처리)
                            ratio = round(views / subs, 2) if subs > 0 else views
                            
                            if ratio >= min_ratio:
                                results.append({
                                    "채널명": info["channelTitle"],
                                    "영상 제목": info["title"],
                                    "구독자 수": subs,
                                    "조회수": views,
                                    "조회수 비율(배)": ratio,
                                    "업로드일": info["publishedAt"][:10],
                                    "영상 링크": f"https://www.youtube.com/watch?v={vid}",
                                    "채널 링크": f"https://www.youtube.com/channel/{info['channelId']}"
                                })
                    
                    if not results:
                        st.info("조건에 맞는 상승세 채널을 찾지 못했습니다. 필터를 조절해보세요.")
                    else:
                        df = pd.DataFrame(results)
                        # 배수 기준으로 내림차순 정렬
                        df = df.sort_values(by="조회수 비율(배)", ascending=False)
                        
                        st.success(f"총 {len(results)}개의 상승세 영상을 찾았습니다!")
                        
                        # 표 출력 (링크를 클릭 가능하게 만들려면 st.dataframe 대신 st.data_editor나 html 사용 가능)
                        st.dataframe(
                            df,
                            column_config={
                                "영상 링크": st.column_config.LinkColumn("영상 링크"),
                                "채널 링크": st.column_config.LinkColumn("채널 링크"),
                                "조회수": st.column_config.NumberColumn(format="%d"),
                                "구독자 수": st.column_config.NumberColumn(format="%d"),
                            },
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # CSV 다운로드 기능
                        csv = df.to_csv(index=False, encoding='utf-8-sig')
                        st.download_button(
                            label="결과 CSV 다운로드",
                            data=csv,
                            file_name=f"rising_channels_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                        )
                        
        except HttpError as e:
            st.error(f"YouTube API 오류가 발생했습니다: {e}")
        except Exception as e:
            st.error(f"알 수 없는 오류가 발생했습니다: {e}")

st.divider()
st.caption("© 2026 YouTube Rising Channel Finder. 모든 데이터는 YouTube Data API v3를 통해 실시간으로 제공됩니다.")
